from http import HTTPStatus
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .forms import ProjectForm
from .models import Project


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project_detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {
        "form": form, "is_edit": False
    })


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {
        "form": form, 
        "is_edit": True, 
        "project": project
    })


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status != "open":
        return JsonResponse(
            {"status": "error", "message": "Project is not open"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = "closed"
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate(request, project_id):
    print('aaa')
    project = get_object_or_404(Project, pk=project_id)
    print('aa')
    if project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants"
    )
    return render(request, "projects/project_list.html", {"projects": paginate(request, projects)})
