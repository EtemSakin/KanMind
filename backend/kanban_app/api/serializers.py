from django.contrib.auth import get_user_model
from rest_framework import serializers

from auth_app.api.serializers import UserShortSerializer
from kanban_app.models import Board, Comment, Task


User = get_user_model()


class BoardSummarySerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = (
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        )
        read_only_fields = ("id",)

    def get_member_count(self, obj):
        if hasattr(obj, "_member_count"):
            return obj._member_count
        return obj.members.count()

    def get_ticket_count(self, obj):
        if hasattr(obj, "_ticket_count"):
            return obj._ticket_count
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        if hasattr(obj, "_tasks_to_do_count"):
            return obj._tasks_to_do_count
        return obj.tasks.filter(status=Task.Status.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        if hasattr(obj, "_tasks_high_prio_count"):
            return obj._tasks_high_prio_count
        return obj.tasks.filter(priority=Task.Priority.HIGH).count()


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserShortSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ("id", "title", "owner_id", "members", "tasks")

    def get_tasks(self, obj):
        return BoardTaskSerializer(obj.tasks.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = ("title", "members")
        extra_kwargs = {"title": {"required": False}}


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        board = attrs.get("board")
        if self.instance is not None:
            board = self.instance.board
            requested_board = attrs.get("board")
            if requested_board is not None and requested_board != board:
                raise serializers.ValidationError(
                    {"board": "Ein Task kann nicht in ein anderes Board verschoben werden."}
                )

        assignee = (
            attrs["assignee"]
            if "assignee" in attrs
            else getattr(self.instance, "assignee", None)
        )
        reviewer = (
            attrs["reviewer"]
            if "reviewer" in attrs
            else getattr(self.instance, "reviewer", None)
        )

        if board is not None:
            if assignee is not None and not self._is_board_participant(board, assignee):
                raise serializers.ValidationError(
                    {"assignee_id": "Der Assignee muss Mitglied des Boards sein."}
                )
            if reviewer is not None and not self._is_board_participant(board, reviewer):
                raise serializers.ValidationError(
                    {"reviewer_id": "Der Reviewer muss Mitglied des Boards sein."}
                )

        return attrs

    def get_comments_count(self, obj):
        if hasattr(obj, "_comments_count"):
            return obj._comments_count
        return obj.comments.count()

    @staticmethod
    def _is_board_participant(board, user):
        return board.owner_id == user.id or board.members.filter(id=user.id).exists()


class BoardTaskSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = tuple(
            field for field in TaskSerializer.Meta.fields if field != "board"
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "created_at", "author", "content")
        read_only_fields = ("id", "created_at", "author")
