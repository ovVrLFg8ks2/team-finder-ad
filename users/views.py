import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.utils import paginate

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegistrationForm
from .models import Skill, User


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
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
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


@login_required
def edit_profile(request):
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("users:user_detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        request.user.set_password(form.cleaned_data["new_password1"])
        request.user.save()
        login(request, request.user)
        return redirect("users:user_detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


def user_list(request):
    queryset = User.objects.all().order_by("-id")

    active_filter = request.GET.get("skill", "").strip()
    if active_filter:
        queryset = queryset.filter(skills__name=active_filter)

    skills = Skill.objects.all().order_by("name")

    queryset = queryset.distinct()

    return render(
        request,
        "users/participants.html",
        {
            "participants": paginate(request, queryset),
            "active_filter": active_filter,
            "skills": skills,
        },
    )


@require_GET
def skill_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")
    data = list(skills.values("id", "name"))
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_user_skill(request):
    try:
        data = json.loads(request.body)
        skill_id = data.get("skill_id")
        skill_name = data.get("name")

        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name.strip())
        else:
            return JsonResponse({"error": "No skill data provided"}, status=HTTPStatus.BAD_REQUEST)

        request.user.skills.add(skill)

        return JsonResponse({
            "id": skill.id,
            "name": skill.name
        }, status=HTTPStatus.OK)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)


@login_required
@require_POST
def remove_user_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if not request.user.skills.filter(pk=skill_id).exists():
        return JsonResponse({"error": "Skill not in user profile"}, status=HTTPStatus.BAD_REQUEST)
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
