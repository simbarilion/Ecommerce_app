from .models import Category

def categories_processor(request):
    """Добавляет список категорий во все шаблоны"""
    categories = Category.objects.all().order_by("name")
    return {"global_categories": categories}
