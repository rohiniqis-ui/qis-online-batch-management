from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home_index(request):
    return render(request, 'home/index.html')


def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        print(f"Username/Email: {username_or_email}, Password: {password}")  

        user = authenticate(
            request,
            username=username_or_email,
            password=password
        )
        print(f"Authenticated User: {user}")

        if user is not None:
            login(request, user)

            if user.role == 'Admin':
                return redirect('admin_dashboard')

            elif user.role == 'Assistant Manager':
                return redirect('assistant_dashboard')

            elif user.role == 'Counselor':
                return redirect('counselor_dashboard')

            elif user.role == 'Trainer':
                return redirect('trainer_dashboard')

            elif user.role == 'Student':
                return redirect('student_dashboard')

            else:
                messages.error(request, 'Invalid user role.')
                return redirect('home_index')

        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('home_index')

    return redirect('home_index')


def logout_user(request):
    logout(request)
    return redirect('home_index')


from django.contrib.auth.decorators import login_required


@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')


@login_required
def assistant_dashboard(request):
    return render(request, 'dashboards/assistant_dashboard.html')


@login_required
def counselor_dashboard(request):
    return render(request, 'dashboards/counselor_dashboard.html')


@login_required
def trainer_dashboard(request):
    return render(request, 'dashboards/trainer_dashboard.html')


@login_required
def student_dashboard(request):
    return render(request, 'dashboards/student_dashboard.html')