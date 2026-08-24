from rest_framework.permissions import BasePermission


def is_board_participant(user, board):
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


class BoardObjectPermission(BasePermission):
    message = "Du hast keine Berechtigung für dieses Board."

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner_id == request.user.id

        if request.method == "DELETE":
            return is_owner

        return is_board_participant(request.user, obj)


class TaskObjectPermission(BasePermission):
    message = "Du hast keine Berechtigung für diesen Task."

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return (
                obj.board.owner_id == request.user.id
                or obj.created_by_id == request.user.id
            )

        return is_board_participant(request.user, obj.board)


class CommentObjectPermission(BasePermission):
    message = "Nur der Autor darf diesen Kommentar löschen."

    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id
