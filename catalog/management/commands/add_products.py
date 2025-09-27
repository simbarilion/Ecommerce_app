from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product

class Command(BaseCommand):
    help = "Add test products to the database and load test data from fixture"

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Category.objects.all().delete()

        call_command("loaddata", "catalog/fixtures/catalog_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))

        category_1, _ = Category.objects.get_or_create(name="Frontend & UI")
        category_2, _ = Category.objects.get_or_create(name="Backend & Dev Tools")

        products = [
            {"name": "Data Visualization Kit (D3.js)",
             "description": "Набор интерактивных графиков на D3.js",
             "image": "Data_Visualization_Kit.jpg",
             "category": category_1,
             "price": 31.00},
            {"name": "SaaS Billing System (Laravel)",
             "description": "Готовая система подписок и биллинга для SaaS",
             "image": "SaaS_Billing_System.jpg",
             "category": category_2,
             "price": 59.00},
            {"name": "Node.js Payment Gateway",
             "description": "Готовая интеграция Stripe/PayPal для Node.js проектов",
             "image": "Node_js_Payment_Gateway.jpg",
             "category": category_2,
             "price": 31.00},
        ]

        for prod in products:
            product, created = Product.objects.get_or_create(**prod)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added product: {Product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Product already exists: {Product.name}"))
