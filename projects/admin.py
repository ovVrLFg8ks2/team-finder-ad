from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "get_participants_count", "created_at")
    list_filter = ("status", )
    list_editable = ("status", )
    search_fields = ("name", "owner__email")
    filter_horizontal = ("participants",)

    @admin.display(description="Кол-во участников")
    def get_participants_count(self, obj):
        return obj.participants.count()
