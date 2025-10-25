from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Создает модератора товаров, если он не создан"

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            if not User.objects.filter(email="productsmoderator@sky.pro").exists():
                user = User.objects.create_user(
                    email="productsmoderator@sky.pro",
                    password="234qwe567rty",
                    first_name="Products",
                    last_name="Moderator",
                    username="products_moderator",
                    country="RU",
                    is_staff=True
                )

                group, _ = Group.objects.get_or_create(name="products_moderator")
                user.groups.add(group)

                self.stdout.write(self.style.SUCCESS(f"Пользователь {user.email} успешно создан."))
            else:
                self.stdout.write(self.style.WARNING(f"Пользователь уже существует."))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка создания модератора товаров: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Неожиданная ошибка: {e}"))
