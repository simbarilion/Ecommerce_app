from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Создает контент-менеджера блога, если он не создан"

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            if not User.objects.filter(email="contentmanager@sky.pro").exists():
                user = User.objects.create_user(
                    email="contentmanager@sky.pro",
                    password="345qwe678rty",
                    first_name="Content",
                    last_name="Manager",
                    username="content_manager",
                    country="RU",
                    is_staff=True
                )

                group, _ = Group.objects.get_or_create(name="content_manager")
                user.groups.add(group)

                self.stdout.write(self.style.SUCCESS(f"Пользователь {user.email} успешно создан"))
            else:
                self.stdout.write(self.style.WARNING(f"Пользователь уже существует"))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка создания контент-менеджера блога: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Неожиданная ошибка: {e}"))
