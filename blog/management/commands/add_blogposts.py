from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from blog.models import Blogpost


class Command(BaseCommand):
    help = "Очищает таблицу статей пользователей и загружает данные из фикстуры blog/fixtures/blogposts_fixture.json"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Очистка таблицы статей пользователей..."))
        Blogpost.objects.all().delete()

        try:
            call_command("loaddata", "blog/fixtures/blogposts_fixture.json")
            self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))

        except Exception as e:
            raise CommandError(f"Ошибка при загрузке фикстур: {e}")
