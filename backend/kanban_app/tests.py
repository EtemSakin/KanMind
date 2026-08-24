from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board


User = get_user_model()


class BoardModelTests(TestCase):
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

    def test_board_relations_are_available_from_both_sides(self):
        board = Board.objects.create(title="KanMind API", owner=self.owner)
        board.members.add(self.owner, self.member)

        self.assertEqual(str(board), "KanMind API")
        self.assertEqual(board.owner, self.owner)
        self.assertQuerySetEqual(
            board.members.order_by("id"),
            [self.owner, self.member],
        )
        self.assertQuerySetEqual(self.owner.owned_boards.all(), [board])
        self.assertQuerySetEqual(self.member.boards.all(), [board])

    def test_board_title_does_not_have_to_be_unique(self):
        Board.objects.create(title="Sprint", owner=self.owner)
        Board.objects.create(title="Sprint", owner=self.owner)

        self.assertEqual(Board.objects.filter(title="Sprint").count(), 2)


class BoardApiTests(APITestCase):
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

    def authenticate(self, user=None):
        user = user or self.owner
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_board_endpoint_requires_token_authentication(self):
        list_response = self.client.get(reverse("board-list-create"))
        create_response = self.client.post(
            reverse("board-list-create"),
            {"title": "Private Board", "members": []},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_contains_only_owned_or_joined_boards_without_duplicates(self):
        owned_board = Board.objects.create(title="Owned", owner=self.owner)
        owned_board.members.add(self.owner)
        joined_board = Board.objects.create(title="Joined", owner=self.outsider)
        joined_board.members.add(self.owner, self.outsider)
        hidden_board = Board.objects.create(title="Hidden", owner=self.member)
        hidden_board.members.add(self.member)
        self.authenticate()

        response = self.client.get(reverse("board-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [board["id"] for board in response.data],
            [owned_board.id, joined_board.id],
        )
        self.assertNotIn(hidden_board.id, [board["id"] for board in response.data])
        self.assertEqual(
            set(response.data[0]),
            {
                "id",
                "title",
                "member_count",
                "ticket_count",
                "tasks_to_do_count",
                "tasks_high_prio_count",
                "owner_id",
            },
        )
        self.assertEqual(response.data[0]["member_count"], 1)
        self.assertEqual(response.data[1]["member_count"], 2)
        self.assertEqual(response.data[0]["ticket_count"], 0)

    def test_create_sets_owner_and_includes_owner_as_member(self):
        self.authenticate()

        response = self.client.post(
            reverse("board-list-create"),
            {"title": "New Board", "members": [self.member.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.get(id=response.data["id"])
        self.assertEqual(board.owner, self.owner)
        self.assertQuerySetEqual(
            board.members.order_by("id"),
            [self.owner, self.member],
        )
        self.assertEqual(response.data["owner_id"], self.owner.id)
        self.assertEqual(response.data["member_count"], 2)
        self.assertEqual(response.data["tasks_to_do_count"], 0)

    def test_create_rejects_unknown_member_id(self):
        self.authenticate()

        response = self.client.post(
            reverse("board-list-create"),
            {"title": "Invalid Board", "members": [999_999]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("members", response.data)
        self.assertFalse(Board.objects.exists())

    def test_member_can_retrieve_board_with_nested_members(self):
        board = Board.objects.create(title="Detail Board", owner=self.owner)
        board.members.add(self.owner, self.member)
        self.authenticate(self.member)

        response = self.client.get(reverse("board-detail", args=[board.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"id", "title", "owner_id", "members", "tasks"},
        )
        self.assertEqual(response.data["owner_id"], self.owner.id)
        self.assertEqual(
            {member["id"] for member in response.data["members"]},
            {self.owner.id, self.member.id},
        )
        self.assertEqual(
            set(response.data["members"][0]),
            {"id", "email", "fullname"},
        )
        self.assertEqual(response.data["tasks"], [])

    def test_outsider_cannot_retrieve_board(self):
        board = Board.objects.create(title="Private Board", owner=self.owner)
        board.members.add(self.owner, self.member)
        self.authenticate(self.outsider)

        response = self.client.get(reverse("board-detail", args=[board.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_patch_board_and_owner_remains_member(self):
        board = Board.objects.create(title="Old Title", owner=self.owner)
        board.members.add(self.owner, self.member)
        self.authenticate(self.member)

        response = self.client.patch(
            reverse("board-detail", args=[board.id]),
            {"title": "New Title", "members": [self.outsider.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        board.refresh_from_db()
        self.assertEqual(board.title, "New Title")
        self.assertQuerySetEqual(
            board.members.order_by("id"),
            [self.owner, self.outsider],
        )
        self.assertEqual(
            {member["id"] for member in response.data["members"]},
            {self.owner.id, self.outsider.id},
        )

    def test_only_owner_can_delete_board(self):
        board = Board.objects.create(title="Delete Board", owner=self.owner)
        board.members.add(self.owner, self.member)
        self.authenticate(self.member)

        forbidden_response = self.client.delete(
            reverse("board-detail", args=[board.id])
        )

        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Board.objects.filter(id=board.id).exists())

        self.authenticate(self.owner)
        owner_response = self.client.delete(reverse("board-detail", args=[board.id]))

        self.assertEqual(owner_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=board.id).exists())

    def test_board_detail_returns_not_found_for_unknown_id(self):
        self.authenticate()

        response = self.client.get(reverse("board-detail", args=[999_999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
