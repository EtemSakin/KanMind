from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board, Comment, Task


User = get_user_model()


class TaskApiTests(APITestCase):
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
        self.reviewer = User.objects.create_user(
            email="reviewer@example.com",
            fullname="Board Reviewer",
            password="StrongPass-4837!",
        )
        self.outsider = User.objects.create_user(
            email="outsider@example.com",
            fullname="Outside User",
            password="StrongPass-4837!",
        )
        self.board = Board.objects.create(title="KanMind", owner=self.owner)
        self.board.members.add(self.owner, self.member, self.reviewer)

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_task(self, **overrides):
        values = {
            "board": self.board,
            "title": "Backend bauen",
            "description": "REST API entwickeln",
            "status": Task.Status.TO_DO,
            "priority": Task.Priority.MEDIUM,
            "assignee": self.member,
            "reviewer": self.reviewer,
            "created_by": self.owner,
            "due_date": "2026-09-01",
        }
        values.update(overrides)
        return Task.objects.create(**values)

    def test_task_endpoints_require_authentication(self):
        task = self.create_task()

        responses = [
            self.client.post(reverse("task-create"), {}, format="json"),
            self.client.get(reverse("task-detail", args=[task.id])),
            self.client.get(reverse("assigned-task-list")),
            self.client.get(reverse("reviewing-task-list")),
        ]

        self.assertTrue(
            all(response.status_code == status.HTTP_401_UNAUTHORIZED for response in responses)
        )

    def test_board_member_can_create_task_with_nested_user_response(self):
        self.authenticate(self.member)
        payload = {
            "board": self.board.id,
            "title": "Backend fertigstellen",
            "description": "API entwickeln",
            "status": "to-do",
            "priority": "high",
            "assignee_id": self.member.id,
            "reviewer_id": self.reviewer.id,
            "due_date": "2026-09-01",
        }

        response = self.client.post(reverse("task-create"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.created_by, self.member)
        self.assertEqual(task.assignee, self.member)
        self.assertEqual(task.reviewer, self.reviewer)
        self.assertEqual(response.data["board"], self.board.id)
        self.assertEqual(response.data["assignee"]["id"], self.member.id)
        self.assertEqual(response.data["reviewer"]["id"], self.reviewer.id)
        self.assertNotIn("assignee_id", response.data)
        self.assertNotIn("reviewer_id", response.data)
        self.assertEqual(response.data["comments_count"], 0)

    def test_outsider_cannot_create_task(self):
        self.authenticate(self.outsider)
        payload = {
            "board": self.board.id,
            "title": "Forbidden Task",
            "description": "",
            "status": "to-do",
            "priority": "medium",
            "assignee_id": self.member.id,
            "reviewer_id": self.reviewer.id,
        }

        response = self.client.post(reverse("task-create"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Task.objects.exists())

    def test_assignee_and_reviewer_must_belong_to_board(self):
        self.authenticate(self.owner)
        base_payload = {
            "board": self.board.id,
            "title": "Invalid Assignment",
            "description": "",
            "status": "to-do",
            "priority": "medium",
        }

        assignee_response = self.client.post(
            reverse("task-create"),
            {**base_payload, "assignee_id": self.outsider.id},
            format="json",
        )
        reviewer_response = self.client.post(
            reverse("task-create"),
            {**base_payload, "reviewer_id": self.outsider.id},
            format="json",
        )

        self.assertEqual(assignee_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee_id", assignee_response.data)
        self.assertEqual(reviewer_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reviewer_id", reviewer_response.data)
        self.assertFalse(Task.objects.exists())

    def test_assigned_and_reviewing_lists_are_filtered_for_current_user(self):
        assigned = self.create_task(title="Assigned")
        reviewing = self.create_task(
            title="Reviewing",
            assignee=self.reviewer,
            reviewer=self.member,
        )
        self.create_task(
            title="Unrelated",
            assignee=self.reviewer,
            reviewer=self.owner,
        )
        self.authenticate(self.member)

        assigned_response = self.client.get(reverse("assigned-task-list"))
        reviewing_response = self.client.get(reverse("reviewing-task-list"))

        self.assertEqual(assigned_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [task["id"] for task in assigned_response.data],
            [assigned.id],
        )
        self.assertEqual(
            [task["id"] for task in reviewing_response.data],
            [reviewing.id],
        )
        self.assertEqual(assigned_response.data[0]["board"], self.board.id)

    def test_board_responses_include_tasks_and_real_summary_counts(self):
        first = self.create_task(priority=Task.Priority.HIGH)
        self.create_task(title="Second", status=Task.Status.IN_PROGRESS)
        self.create_task(
            title="Third",
            status=Task.Status.TO_DO,
            priority=Task.Priority.HIGH,
        )
        Comment.objects.create(task=first, author=self.member, content="Erster Kommentar")
        self.authenticate(self.owner)

        list_response = self.client.get(reverse("board-list-create"))
        detail_response = self.client.get(reverse("board-detail", args=[self.board.id]))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        summary = list_response.data[0]
        self.assertEqual(summary["ticket_count"], 3)
        self.assertEqual(summary["tasks_to_do_count"], 2)
        self.assertEqual(summary["tasks_high_prio_count"], 2)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(detail_response.data["tasks"]), 3)
        self.assertNotIn("board", detail_response.data["tasks"][0])
        self.assertEqual(detail_response.data["tasks"][0]["comments_count"], 1)

    def test_board_member_can_patch_task_but_cannot_move_it_to_another_board(self):
        task = self.create_task()
        other_board = Board.objects.create(title="Other", owner=self.owner)
        other_board.members.add(self.owner, self.member)
        self.authenticate(self.member)

        update_response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {
                "title": "Updated Task",
                "status": "review",
                "priority": "high",
                "assignee_id": None,
            },
            format="json",
        )
        move_response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {"board": other_board.id},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated Task")
        self.assertEqual(task.status, Task.Status.REVIEW)
        self.assertIsNone(task.assignee)
        self.assertIsNone(update_response.data["assignee"])
        self.assertEqual(move_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("board", move_response.data)
        task.refresh_from_db()
        self.assertEqual(task.board, self.board)

    def test_outsider_cannot_read_or_patch_task(self):
        task = self.create_task()
        self.authenticate(self.outsider)

        get_response = self.client.get(reverse("task-detail", args=[task.id]))
        patch_response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {"title": "Hacked"},
            format="json",
        )

        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        task.refresh_from_db()
        self.assertNotEqual(task.title, "Hacked")

    def test_only_creator_or_board_owner_can_delete_task(self):
        task = self.create_task(created_by=self.member)
        self.authenticate(self.reviewer)

        forbidden_response = self.client.delete(reverse("task-detail", args=[task.id]))

        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

        self.authenticate(self.member)
        creator_response = self.client.delete(reverse("task-detail", args=[task.id]))

        self.assertEqual(creator_response.status_code, status.HTTP_204_NO_CONTENT)

        owner_task = self.create_task(title="Owner deletes", created_by=self.member)
        self.authenticate(self.owner)
        owner_response = self.client.delete(
            reverse("task-detail", args=[owner_task.id])
        )

        self.assertEqual(owner_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_creator_can_delete_task_after_being_removed_from_board(self):
        task = self.create_task(created_by=self.member)
        self.board.members.remove(self.member)
        self.authenticate(self.member)

        response = self.client.delete(reverse("task-detail", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
