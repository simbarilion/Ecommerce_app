from django import forms

from .models import MessageFeedback, Product
from .services.product_service import SpamChecker


class FeedbackForm(forms.ModelForm):
    """Класс формы обратной связи"""
    class Meta:
        model = MessageFeedback
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class CustomClearableFileInput(forms.ClearableFileInput):
    """Класс для создания кастомного поля формы для загрузки файлов"""
    template_name = "widgets/custom_file_input.html"


class ProductForm(forms.ModelForm):
    """Класс формы для создания карточки товара"""
    class Meta:
        model = Product
        fields = ["name", "brief_description", "description", "image", "category", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "brief_description": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "image": CustomClearableFileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }


    def __init__(self, *args, **kwargs):
        """Инициализация атрибутов класса"""
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Нет категории"
        self.checker = SpamChecker()


    def clean_text_field(self, field_name):
        """Валидатор текстовых полей формы"""
        value = self.cleaned_data.get(field_name)
        self.checker.check_text(value)
        return value


    def clean_name(self):
        """Метод валидации поля формы 'наименование товара' на спам и запрещенные слова"""
        return self.clean_text_field("name")


    def clean_brief_description(self):
        """Метод валидации поля формы 'краткое описание товара' на спам и запрещенные слова"""
        return self.clean_text_field("brief_description")


    def clean_description(self):
        """Метод валидации поля формы 'описание товара' на спам и запрещенные слова"""
        return self.clean_text_field("description")


    def clean_price(self):
        """Метод валидации поля формы 'цена товара'"""
        price = self.cleaned_data.get("price")
        if price <= 0:
            raise forms.ValidationError("Цена не может быть отрицательной или равной нулю")
        return price


    def clean_image(self):
        """Метод валидации поля формы 'изображение' на формат и размер файла"""
        image = self.cleaned_data.get("image")
        max_size_mb = 5
        if hasattr(image, "content_type"):
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise forms.ValidationError("Файл должен быть в формате JPEG или PNG")
            if image.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size_mb} МБ")
        return image


class ProductModeratorForm(forms.ModelForm):
    """Класс формы модератора для редактирования карточки товара"""
    class Meta:
        model = Product
        fields = ["category", "status"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
