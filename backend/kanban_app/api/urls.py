from django.urls import path

from kanban_app.api.views import (
    AssignedTaskListView,
    BoardDetailView,
    BoardListCreateView,
    CommentDeleteView,
    ReviewingTaskListView,
    TaskCommentListCreateView,
    TaskCreateView,
    TaskDetailView,
)


urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list-create"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/assigned-to-me/",
        AssignedTaskListView.as_view(),
        name="assigned-task-list",
    ),
    path(
        "tasks/reviewing/",
        ReviewingTaskListView.as_view(),
        name="reviewing-task-list",
    ),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentListCreateView.as_view(),
        name="task-comment-list-create",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
