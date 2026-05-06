from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.utils import paginate

from .forms import ProjectForm
from .models import Project
from .utils import get_projects_with_related


def project_detail(request, project_id):
    project = get_object_or_404(
        get_projects_with_related(),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:project_detail", project_id=project.id)
    return render(request, "projects/create-project.html", {
        "form": form, "is_edit": False
    })


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_detail", project_id=project.id)
    return render(request, "projects/create-project.html", {
        "form": form,
        "is_edit": True,
        "project": project
    })


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Project is not open"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if is_member := project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not is_member})


def project_list(request):
    projects = get_projects_with_related()
    return render(request, "projects/project_list.html", {"projects": paginate(request, projects)})
