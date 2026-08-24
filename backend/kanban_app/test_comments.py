from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board, Comment, Task


User = get_user_model()


class CommentApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            fullname="Board Owner",
            password="StrongPass-4837!",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            fullname="Board Member",
            password="StrongPass-4837!",
        )
        self.outsider = User.objects.create_user(
            email="outsider@example.com",
            fullname="Outside User",
            password="StrongPass-4837!",
        )
        self.board = Board.objects.create(title="KanMind", owner=self.owner)
        self.board.members.add(self.owner, self.member)
        self.task = Task.objects.create(
            board=self.board,
            title="Comment Task",
            created_by=self.owner,
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_comment_endpoints_require_authentication(self):
        list_response = self.client.get(
            reverse("task-comment-list-create", args=[self.task.id])
        )
        create_response = self.client.post(
            reverse("task-comment-list-create", args=[self.task.id]),
            {"content": "Nicht erlaubt"},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_board_member_can_create_and_list_comments(self):
        self.authenticate(self.member)

        create_response = self.client.post(
            reverse("task-comment-list-create", args=[self.task.id]),
            {"content": "Bitte noch einmal prüfen."},
            format="json",
        )
        list_response = self.client.get(
            reverse("task-comment-list-create", args=[self.task.id])
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=create_response.data["id"])
        self.assertEqual(comment.author, self.member)
        self.assertEqual(comment.task, self.task)
        self.assertEqual(
            set(create_response.data),
            {"id", "created_at", "author", "content"},
        )
        self.assertEqual(create_response.data["author"], "Board Member")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, [create_response.data])

    def test_outsider_cannot_read_or_create_comments(self):
        Comment.objects.create(task=self.task, author=self.member, content="Intern")
        self.authenticate(self.outsider)

        list_response = self.client.get(
            reverse("task-comment-list-create", args=[self.task.id])
        )
        create_response = self.client.post(
            reverse("task-comment-list-create", args=[self.task.id]),
            {"content": "Hacked"},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)

    def test_only_comment_author_can_delete_comment(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content="Mein Kommentar",
        )
        url = reverse("comment-delete", args=[self.task.id, comment.id])
        self.authenticate(self.owner)

        owner_response = self.client.delete(url)

        self.assertEqual(owner_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

        self.authenticate(self.member)
        author_response = self.client.delete(url)

        self.assertEqual(author_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_comment_delete_url_must_match_parent_task(self):
        other_task = Task.objects.create(
            board=self.board,
            title="Other Task",
            created_by=self.owner,
        )
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content="Mein Kommentar",
        )
        self.authenticate(self.member)

        response = self.client.delete(
            reverse("comment-delete", args=[other_task.id, comment.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_unknown_task_returns_not_found(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse("task-comment-list-create", args=[999_999])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
