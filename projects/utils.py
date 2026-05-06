from .models import Project


def get_projects_with_related():
    return Project.objects.select_related("owner").prefetch_related("participants")
