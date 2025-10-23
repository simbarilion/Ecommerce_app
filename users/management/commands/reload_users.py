from django.core.management import BaseCommand, call_command, CommandError

from users.models import CustomUser


class Command(BaseCommand):
    help = "Очищает таблицу пользователей и загружает данные из фикстуры users/fixtures/users_fixture.json"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Очистка таблицы пользователей..."))
        CustomUser.objects.exclude(is_superuser=True).delete()

        try:
            call_command("loaddata", "users/fixtures/users_fixture.json")
            self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))

        except Exception as e:
            raise CommandError(f"Ошибка при загрузке фикстур: {e}")
