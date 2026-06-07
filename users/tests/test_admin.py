from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from users.admin import UserAdmin, CrewAdmin
from users.models import User, Crew
from tests.helpers import sample_user, create_crew


class UserAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ("email", "first_name", "last_name", "is_staff"),
        )

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("email", "first_name", "last_name"),
        )

    def test_ordering(self):
        self.assertEqual(self.admin.ordering, ("id",))

    def test_add_fieldsets_contains_email(self):
        add_fields = self.admin.add_fieldsets[0][1]["fields"]
        self.assertIn("email", add_fields)

    def test_fieldsets_contain_email(self):
        all_fields = [
            field for _, options in self.admin.fieldsets for field in options["fields"]
        ]
        self.assertIn("email", all_fields)


class CrewAdminTests(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = CrewAdmin(Crew, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            ("last_name", "first_name", "user"),
        )

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("last_name", "first_name", "user__email"),
        )

    def test_crew_str(self):
        crew = create_crew(
            sample_user(email="str@example.com"), first_name="John", last_name="Doe"
        )
        self.assertEqual(str(crew), "John Doe")
