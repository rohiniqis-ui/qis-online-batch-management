from django import forms

from batches.models import Batch

from .models import Assignment, ClassSession, Exam


class SyllabusProgressForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["syllabus_progress"]
        widgets = {
            "syllabus_progress": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100}
            )
        }

    def clean_syllabus_progress(self):
        progress = self.cleaned_data["syllabus_progress"]
        if progress > 100:
            raise forms.ValidationError("Syllabus progress cannot be more than 100.")
        return progress


class ClassSessionForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = [
            "title",
            "session_date",
            "start_time",
            "end_time",
            "meeting_link",
            "recording_url",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "session_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "meeting_link": forms.URLInput(attrs={"class": "form-control"}),
            "recording_url": forms.URLInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date", "total_marks", "attachment_url"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "attachment_url": forms.URLInput(attrs={"class": "form-control"}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["title", "exam_date", "total_marks", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
