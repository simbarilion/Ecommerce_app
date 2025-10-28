from django.core.management.base import BaseCommand
from django.core.management import call_command

from catalog.models import Category, Product, Contacts


class Command(BaseCommand):
    help = "Add test categories, products, contacts to the database and load test data from fixture"

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Category.objects.all().delete()
        Contacts.objects.all().delete()

        call_command("loaddata", "catalog/fixtures/contacts_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены контакты из фикструры"))

        call_command("loaddata", "catalog/fixtures/category_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены категории из фикструры"))

        call_command("loaddata", "catalog/fixtures/product_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены товары из фикструры"))

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
