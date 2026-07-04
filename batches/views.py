# batches/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Batch

User = get_user_model()


from django.shortcuts import render
from accounts.models import CustomUser as User
from batches.models import Batch


def batch_list(request):

    batches = Batch.objects.select_related(
        "trainer",
        "assistant_manager"
    ).all().order_by("-created_at")

    # -------------------------
    # Search
    # -------------------------
    search = request.GET.get("search")

    if search:
        batches = batches.filter(
            batch_name__icontains=search
        )

    # -------------------------
    # Status Filter
    # -------------------------
    status = request.GET.get("status")

    if status:
        batches = batches.filter(
            status=status
        )

    # -------------------------
    # Trainer Filter
    # -------------------------
    trainer = request.GET.get("trainer")

    if trainer:
        batches = batches.filter(
            trainer_id=trainer
        )

    # -------------------------
    # Date Range
    # -------------------------
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        batches = batches.filter(
            start_date__gte=start_date
        )

    if end_date:
        batches = batches.filter(
            end_date__lte=end_date
        )

    trainers = User.objects.filter(
        role="Trainer",
        status=True
    )

    # -------------------------
    # Dynamic Base Template
    # -------------------------
    if request.user.role == "Assistant Manager":
        base_template = "includes/manager/base.html"

    elif request.user.role == "Counselor":
        base_template = "includes/counselor/base.html"

    elif request.user.role == "Admin":
        base_template = "includes/admin/base.html"

    else:
        base_template = "base.html"

    context = {
        "batches": batches,
        "trainers": trainers,

        "search": search,
        "status": status,
        "trainer": trainer,
        "start_date": start_date,
        "end_date": end_date,

        "upcoming_count": Batch.objects.filter(
            status="Upcoming"
        ).count(),

        "ongoing_count": Batch.objects.filter(
            status="Ongoing"
        ).count(),

        "completed_count": Batch.objects.filter(
            status="Completed"
        ).count(),

        "archived_count": Batch.objects.filter(
            status="Archived"
        ).count(),

        "base_template": base_template,
    }

    return render(
        request,
        "batches/batch_list.html",
        context
    )

def batch_form(request, id=None):

    batch = None

    if id:
        batch = get_object_or_404(
            Batch,
            id=id
        )

    trainers = User.objects.filter(
        role='Trainer',
        status=True
    )

    if request.method == 'POST':

        trainer_id = request.POST.get('trainer')

        trainer = None

        if trainer_id:
            trainer = User.objects.get(
                id=trainer_id
            )

        # Trainer Validation

        if trainer:

            trainer_batches = Batch.objects.filter(
                trainer=trainer,
                status='Ongoing'
            )

            if batch:
                trainer_batches = trainer_batches.exclude(
                    id=batch.id
                )

            if trainer_batches.exists():

                messages.error(
                    request,
                    f'{trainer.first_name} already has an active batch.'
                )

                return render(
                    request,
                    'batches/batch_form.html',
                    {
                        'batch': batch,
                        'trainers': trainers
                    }
                )

        if batch is None:

            batch = Batch()

        batch.batch_name = request.POST.get(
            'batch_name'
        )

        batch.course_name = request.POST.get(
            'course_name'
        )

        batch.trainer = trainer

        batch.assistant_manager = request.user

        batch.start_date = request.POST.get(
            'start_date'
        )

        batch.end_date = request.POST.get(
            'end_date'
        )

        batch.schedule = request.POST.get(
            'schedule'
        )

        batch.status = request.POST.get(
            'status'
        )

        batch.save()

        messages.success(
            request,
            'Batch saved successfully.'
        )

        return redirect('batches:batch_list')

    return render(
        request,
        'batches/batch_form.html',
        {
            'batch': batch,
            'trainers': trainers
        }
    )


def archive_batch(request, id):

    batch = get_object_or_404(
        Batch,
        id=id
    )

    batch.status = 'Archived'
    batch.save()

    messages.success(
        request,
        'Batch archived successfully.'
    )

    return redirect('batches:batch_list')