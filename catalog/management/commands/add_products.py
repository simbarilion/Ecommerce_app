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

        call_command("loaddata", "catalog/fixtures/catalog_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены категории и товары из фикструры"))

        category_1, _ = Category.objects.get_or_create(name="Frontend & UI")
        category_2, _ = Category.objects.get_or_create(name="Backend & Dev Tools")

        products = [
            {"name": "Data Visualization Kit (D3.js)",
             "slug": "data_visualization_kit_d3_js",
             "brief_description": "Набор интерактивных графиков на D3.js",
             "description": "Набор интерактивных графиков на D3.js делает данные наглядными. Вы можете создавать диаграммы, карты и динамические визуализации. Это помогает лучше понять аналитику и презентовать её пользователям. Инструмент подходит для дашбордов и отчетов",
             "image": "products/images/Data_Visualization_Kit.jpg",
             "category": category_1,
             "price": 2499.0},
            {"name": "Node.js Payment Gateway",
             "slug": "node_js_payment_gateway",
             "brief_description": "Готовая интеграция Stripe/PayPal для Node.js проектов",
             "description": "Готовая интеграция Stripe и PayPal для проектов на Node.js. Вы сможете быстро подключить онлайн-оплаты в свое приложение. Код написан с учетом безопасности и удобства. Поддерживает популярные платежные сценарии",
             "image": "products/images/Node_js_Payment_Gateway.jpg",
             "category": category_2,
             "price": 2499.0},
            {
            "name": "SaaS Billing System (Laravel)",
            "slug": "saas_billing_system_laravel",
            "brief_description": "Готовая система подписок и биллинга для SaaS",
            "description": "Готовая система подписок и биллинга на Laravel экономит месяцы разработки. В ней реализованы тарифные планы, платежи и управление пользователями. Подходит для SaaS-проектов любого масштаба. Вы получаете надёжное решение для монетизации бизнеса",
            "image": "products/images/SaaS_Billing_System.png",
            "category": category_2,
            "price": 4800.0
            }
        ]

        for prod in products:
            product, created = Product.objects.get_or_create(**prod)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Успешно добавлен товар: {Product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Товар уже существует: {Product.name}"))

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
