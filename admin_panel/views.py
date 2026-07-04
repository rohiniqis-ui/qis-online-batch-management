from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import CustomUser


def user_list(request, role):
    users = CustomUser.objects.filter(role=role)

    context = {
        'users': users,
        'role': role
    }
    return render( request, 'admin/users/user_list.html', context)


def add_user(request, role):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        profile_image = request.FILES.get('profile_image')

        user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            role=role,
            profile_image=profile_image
        )

        user.set_password(password)
        user.save()

        return redirect(
            'admin:user_list',
            role=role
        )

    return render( request, 'admin/users/user_form.html', 
                  {'role': role,'action': 'Add'}
    )

def edit_user(request, id):

    user = get_object_or_404(
        CustomUser,
        id=id
    )

    if request.method == "POST":

        user.first_name = request.POST.get('first_name')

        user.last_name = request.POST.get('last_name')

        user.username = request.POST.get('username')

        user.email = request.POST.get('email')

        user.phone = request.POST.get('phone')

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        password = request.POST.get('password')

        if password:
            user.set_password(password)

        user.save()

        return redirect('admin:user_list',role=user.role)

    return render(
        request,
        'admin/users/user_form.html',
        {
            'user_obj': user,
            'role': user.role,
            'action': 'Edit'
        }
    )

def toggle_user_status(request,id):

    user = get_object_or_404(CustomUser,id=id)
    user.status = not user.status
    user.save()

    return redirect(
        'admin:user_list',
        role=user.role
    )