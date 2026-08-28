from django.contrib import admin

from kanban_app.models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Configure board management in Django admin."""

    list_display = ("title", "owner")
    search_fields = ("title", "owner__email", "owner__fullname")
    filter_horizontal = ("members",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configure task management in Django admin."""

    list_display = ("title", "board", "status", "priority", "assignee", "reviewer")
    list_filter = ("status", "priority")
    search_fields = ("title", "description", "board__title")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configure comment management in Django admin."""

    list_display = ("task", "author", "created_at")
    search_fields = ("content", "task__title", "author__email")
