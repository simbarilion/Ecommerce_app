import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from blog.models import Blogpost


# class Command(BaseCommand):
#     help = "Загружает тестовые данные из фикстур blog/fixtures/"
#
#     def handle(self, *args, **kwargs):
#         Blogpost.objects.all().delete()
#
#         base_dir = os.path.join("blog", "fixtures")
#         users_fixture = os.path.join(base_dir, "users_fixture.json")
#         posts_fixture = os.path.join(base_dir, "blogposts_fixture.json")
#
#         try:
#             with open(users_fixture, encoding="utf-8") as f:
#                 users = json.load(f)
#
#             for u in users:
#                 fields = u["fields"]
#                 if not User.objects.filter(username=fields["username"]).exists():
#                     User.objects.create_user(
#                         username=fields["username"],
#                         email=fields.get("email", ""),
#                         first_name=fields.get("first_name", ""),
#                         last_name=fields.get("last_name", ""),
#                         password="pbkdf2_sha256$600000$dummy$fakehash"
#                     )
#             self.stdout.write(self.style.SUCCESS("Загружены пользователи из фикстуры"))
#
#             call_command("loaddata", posts_fixture)
#             self.stdout.write(self.style.SUCCESS("Загружены статьи из фикстуры"))
#         except Exception as e:
#             raise CommandError(f"Ошибка при загрузке фикстур: {e}")
#
#         self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
