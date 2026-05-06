from django import forms
from team_finder.utils import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    github_url = forms.URLField(validators=[validate_github_url])

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Описание проекта"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/owner/repo"}),
            "status": forms.Select(),
        }
