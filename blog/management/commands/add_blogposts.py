from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


from blog.models import Author, Blogpost

class Command(BaseCommand):
    help = "Загружает тестовые данные из фикстур blog/fixtures/"

    def handle(self, *args, **kwargs):
        Blogpost.objects.all().delete()
        Author.objects.all().delete()

        try:
            call_command("loaddata", "blog/fixtures/author_fixture.json")
            self.stdout.write(self.style.SUCCESS("Загружены авторы"))

            call_command("loaddata", "blog/fixtures/blogpost_fixture.json")
            self.stdout.write(self.style.SUCCESS("Загружены статьи"))
        except Exception as e:
            raise CommandError(f"Ошибка при загрузке фикстур: {e}")

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
