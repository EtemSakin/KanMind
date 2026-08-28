"""API views for boards, tasks, and comments."""

from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.api.permissions import (
    BoardObjectPermission,
    CommentObjectPermission,
    TaskObjectPermission,
    is_board_participant,
)
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardSummarySerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
)
from kanban_app.models import Board, Comment, Task


class BoardListCreateView(ListCreateAPIView):
    """List accessible boards and create new boards."""

    serializer_class = BoardSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return boards owned by or shared with the current user."""
        return (
            Board.objects.annotate(
                _member_count=Count("members", distinct=True),
                _ticket_count=Count("tasks", distinct=True),
                _tasks_to_do_count=Count(
                    "tasks",
                    filter=Q(tasks__status=Task.Status.TO_DO),
                    distinct=True,
                ),
                _tasks_high_prio_count=Count(
                    "tasks",
                    filter=Q(tasks__priority=Task.Priority.HIGH),
                    distinct=True,
                ),
            )
            .filter(Q(owner=self.request.user) | Q(members=self.request.user))
            .select_related("owner")
            .prefetch_related("members")
            .distinct()
            .order_by("id")
        )

    def perform_create(self, serializer):
        """Create a board and add its owner as a member."""
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an individual board."""

    queryset = Board.objects.select_related("owner").prefetch_related(
        "members",
        Prefetch(
            "tasks",
            queryset=Task.objects.select_related("assignee", "reviewer").annotate(
                _comments_count=Count("comments")
            ),
        ),
    )
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, BoardObjectPermission]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Return the serializer matching the current request method."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def update(self, request, *args, **kwargs):
        """Update a board and return its updated representation."""
        board = self.get_object()
        serializer = self.get_serializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        board.members.add(board.owner)

        return Response(
            BoardUpdateSerializer(
                board,
                context=self.get_serializer_context(),
            ).data
        )


class TaskCreateView(CreateAPIView):
    """Create tasks for existing boards."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a task and return 404 if its board does not exist."""
        board_id = request.data.get("board")

        try:
            board_id = int(board_id)
        except (TypeError, ValueError):
            return super().create(request, *args, **kwargs)

        get_object_or_404(Board, id=board_id)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create a task for an authorized board participant."""
        board = serializer.validated_data["board"]
        if not is_board_participant(self.request.user, board):
            raise PermissionDenied("Du bist kein Mitglied dieses Boards.")
        serializer.save(created_by=self.request.user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an individual task."""

    queryset = (
        Task.objects.select_related(
            "board",
            "board__owner",
            "assignee",
            "reviewer",
            "created_by",
        )
        .prefetch_related("board__members")
        .annotate(_comments_count=Count("comments"))
    )
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskObjectPermission]
    http_method_names = ["get", "patch", "delete", "head", "options"]


class AssignedTaskListView(ListAPIView):
    """List tasks assigned to the current user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks assigned to the authenticated user."""
        return (
            Task.objects.filter(assignee=self.request.user)
            .select_related("board", "assignee", "reviewer")
            .annotate(_comments_count=Count("comments"))
            .order_by("id")
        )


class ReviewingTaskListView(ListAPIView):
    """List tasks reviewed by the current user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks where the authenticated user is the reviewer."""
        return (
            Task.objects.filter(reviewer=self.request.user)
            .select_related("board", "assignee", "reviewer")
            .annotate(_comments_count=Count("comments"))
            .order_by("id")
        )


class TaskCommentListCreateView(ListCreateAPIView):
    """List comments for a task and create new comments."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        """Return the requested task after checking board access."""
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(
                Task.objects.select_related("board", "board__owner").prefetch_related(
                    "board__members"
                ),
                id=self.kwargs["task_id"],
            )
            if not is_board_participant(self.request.user, self._task.board):
                raise PermissionDenied("Du bist kein Mitglied dieses Boards.")
        return self._task

    def get_queryset(self):
        """Return comments belonging to the requested task."""
        return self.get_task().comments.select_related("author").all()

    def perform_create(self, serializer):
        """Create a comment for the requested task and current user."""
        serializer.save(task=self.get_task(), author=self.request.user)


class CommentDeleteView(DestroyAPIView):
    """Delete comments belonging to a specific task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentObjectPermission]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        """Return comments belonging to the requested task."""
        return (
            Comment.objects.filter(task_id=self.kwargs["task_id"])
            .select_related("author", "task", "task__board", "task__board__owner")
            .prefetch_related("task__board__members")
        )
