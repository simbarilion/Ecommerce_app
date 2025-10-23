from django.core.management import BaseCommand, call_command, CommandError

from blog.models import Blogpost


class Command(BaseCommand):
    help = "Очищает таблицу статей блога и загружает данные из фикстуры blog/fixtures/blogposts_fixture.json"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Очистка таблицы статей блога..."))
        Blogpost.objects.all().delete()

        try:
            call_command("loaddata", "blog/fixtures/blogposts_fixture.json")
            self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))

        except Exception as e:
            raise CommandError(f"Ошибка при загрузке фикстур: {e}")
