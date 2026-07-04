from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from batches.models import Batch

from .models import StudentProfile


User = get_user_model()


class BatchAssignmentRequestForm(forms.Form):
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.none(),
        empty_label="Select batch",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    request_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        current_batch = kwargs.pop("current_batch", None)
        super().__init__(*args, **kwargs)

        batches = Batch.objects.exclude(status="Archived").order_by("start_date", "batch_name")
        if current_batch:
            batches = batches.exclude(pk=current_batch.pk)
        self.fields["batch"].queryset = batches


class BatchAssignmentReviewForm(forms.Form):
    ACTION_CHOICES = (
        ("approve", "Approve"),
        ("reject", "Reject"),
    )

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    review_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class StudentProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Required when creating a new student login.",
    )

    class Meta:
        model = StudentProfile
        fields = [
            "user",
            "batch",
            "counselor",
            "admission_date",
            "date_of_birth",
            "gender",
            "qualification",
            "college",
            "guardian_name",
            "guardian_phone",
            "emergency_contact",
            "address",
            "city",
            "state",
            "pincode",
            "status",
            "remarks",
        ]
        widgets = {
            "admission_date": forms.DateInput(attrs={"type": "date"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        used_user_ids = StudentProfile.objects.values_list("user_id", flat=True)
        if self.instance and self.instance.pk:
            self.fields["user"].queryset = User.objects.filter(
                pk=self.instance.user_id
            ) | User.objects.exclude(pk__in=used_user_ids)
        else:
            self.fields["user"].queryset = User.objects.exclude(pk__in=used_user_ids)

        if self._is_counselor_user():
            self.fields.pop("user", None)
            self.fields.pop("counselor", None)
            if self.instance and self.instance.pk:
                self.fields["password"].help_text = "Leave blank to keep the current password."
                self.fields["username"].initial = self.instance.user.username
                self.fields["first_name"].initial = self.instance.user.first_name
                self.fields["last_name"].initial = self.instance.user.last_name
                self.fields["email"].initial = self.instance.user.email
                self.fields["phone"].initial = getattr(self.instance.user, "phone", "")
            else:
                self.fields["password"].required = True
        else:
            for field_name in ["username", "first_name", "last_name", "email", "phone", "password"]:
                self.fields.pop(field_name, None)

        self.order_fields(self._field_order())

        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css_class

    def save(self, commit=True):
        if not self._is_counselor_user():
            return super().save(commit=commit)

        with transaction.atomic():
            student = super().save(commit=False)
            student.user = self._save_student_user()
            student.counselor = self.current_user
            if commit:
                student.save()
                self.save_m2m()
            return student

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        existing_users = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            existing_users = existing_users.exclude(pk=self.instance.user_id)
        if existing_users.exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        existing_users = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            existing_users = existing_users.exclude(pk=self.instance.user_id)
        if existing_users.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password

    def clean_guardian_phone(self):
        return self._clean_phone("guardian_phone")

    def clean_emergency_contact(self):
        return self._clean_phone("emergency_contact")

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode", "").strip()
        if pincode and not pincode.isdigit():
            raise forms.ValidationError("Pincode must contain digits only.")
        return pincode

    def _clean_phone(self, field_name):
        value = self.cleaned_data.get(field_name, "").strip()
        if value and (not value.isdigit() or len(value) < 10):
            raise forms.ValidationError("Enter a valid phone number with at least 10 digits.")
        return value

    def _is_counselor_user(self):
        return bool(self.current_user and getattr(self.current_user, "role", None) == "Counselor")

    def _field_order(self):
        account_fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
        ]
        profile_fields = [
            "user",
            "batch",
            "counselor",
            "status",
            "admission_date",
            "date_of_birth",
            "gender",
            "qualification",
            "college",
            "guardian_name",
            "guardian_phone",
            "emergency_contact",
            "address",
            "city",
            "state",
            "pincode",
            "remarks",
        ]
        return account_fields + profile_fields

    def _save_student_user(self):
        if self.instance and self.instance.pk:
            user = self.instance.user
        else:
            user = User(role="Student", status=True)

        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.role = "Student"

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        return user


from django import forms


class PaymentProofForm(forms.Form):
    transaction_id = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    amount_paid = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    proof_file = forms.FileField(widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class StudentFeedbackForm(forms.Form):
    session = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}))
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=5,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
    )
    comments = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}))

    def __init__(self, *args, **kwargs):
        sessions = kwargs.pop("sessions", [])
        super().__init__(*args, **kwargs)
        self.fields["session"].choices = [("", "General feedback")] + [
            (session.pk, f"{session.session_date} - {session.title}") for session in sessions
        ]


class StudentRequestForm(forms.Form):
    REQUEST_TO_CHOICES = (
        ("Counselor", "Counselor"),
        ("Trainer", "Trainer"),
    )

    request_to = forms.ChoiceField(choices=REQUEST_TO_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}))
