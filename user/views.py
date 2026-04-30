from django.shortcuts import get_object_or_404, render
from .models import User


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


def register(request):
    return


def login_view(request):
    return


def logout_view(request):
    return


def edit_profile(request):
    return


def change_password(request):
    return
