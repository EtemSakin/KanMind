"""Custom permissions for boards, tasks, and comments."""

from rest_framework.permissions import BasePermission


def is_board_participant(user, board):
    """Return whether the user owns or belongs to the board."""
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


class BoardObjectPermission(BasePermission):
    """Control access to individual boards."""

    message = "Du hast keine Berechtigung für dieses Board."

    def has_object_permission(self, request, view, obj):
        """Allow board access based on membership and ownership."""
        is_owner = obj.owner_id == request.user.id

        if request.method == "DELETE":
            return is_owner

        return is_board_participant(request.user, obj)


class TaskObjectPermission(BasePermission):
    """Control access to individual tasks."""

    message = "Du hast keine Berechtigung für diesen Task."

    def has_object_permission(self, request, view, obj):
        """Allow task access based on board participation and ownership."""
        if request.method == "DELETE":
            return (
                obj.board.owner_id == request.user.id
                or obj.created_by_id == request.user.id
            )

        return is_board_participant(request.user, obj.board)


class CommentObjectPermission(BasePermission):
    """Restrict comment deletion to the comment author."""

    message = "Nur der Autor darf diesen Kommentar löschen."

    def has_object_permission(self, request, view, obj):
        """Return whether the current user authored the comment."""
        return obj.author_id == request.user.id
