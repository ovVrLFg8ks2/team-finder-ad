from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from .forms import RegistrationForm, LoginForm, EditProfileForm, ChangePasswordForm
from .models import User


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("users:user_detail", user_id=user.id)
            form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    user = request.user
    logout(request)
    return redirect("users:user_detail", user_id=user.id)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", user_id=request.user.id)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password1"])
            request.user.save()
            login(request, request.user)
            return redirect("users:user_detail", user_id=request.user.id)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})
    
    
def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def user_list(request):
    active_filter = request.GET.get("filter")
    queryset = User.objects.all().order_by("-id")
    
    ''' ! setup projects first !
    if active_filter == 'owners-of-favorite-projects':
        queryset = queryset.filter(projects__favorites__user=request.user).distinct()
    elif active_filter == 'owners-of-participating-projects':
        queryset = queryset.filter(projects__participants=request.user).distinct()
    elif active_filter == 'interested-in-my-projects':
        queryset = queryset.filter(projects__participants=request.user).distinct()
    elif active_filter == 'participants-of-my-projects':
        queryset = queryset.filter(projects__participants=request.user).distinct()
    '''
    
    return render(
        request,
        "users/participants.html",
        {
            "participants": paginate(request, queryset),
            "active_filter": active_filter,
        },
    )
