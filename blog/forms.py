from django import forms

from catalog.services.product_service import SpamChecker
from .models import Blogpost


class CustomClearableFileInput(forms.ClearableFileInput):
    """Класс для создания кастомного поля формы для загрузки файлов"""
    template_name = "widgets/custom_file_input.html"


class BlogpostForm(forms.ModelForm):
    """Класс формы для создания карточки статьи"""
    class Meta:
        model = Blogpost
        fields = ["title", "content", "preview"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 20}),
            "preview": CustomClearableFileInput(attrs={"class": "form-control"}),
        }


    def __init__(self, *args, **kwargs):
        """Инициализация атрибутов класса"""
        super().__init__(*args, **kwargs)
        self.checker = SpamChecker()


    def clean_text_field(self, field_name):
        """Валидатор текстовых полей формы"""
        value = self.cleaned_data.get(field_name)
        self.checker.check_text(value)
        return value


    def clean_title(self):
        """Метод валидации поля формы 'заголовок' на спам и запрещенные слова"""
        return self.clean_text_field("title")


    def clean_image(self):
        """Метод валидации поля формы 'изображение' на формат и размер файла"""
        image = self.cleaned_data.get("preview")
        if hasattr(image, "content_type"):
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise forms.ValidationError("Файл должен быть в формате JPEG или PNG")
            max_size_mb = 5
            if image.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size_mb} МБ")
        return image


class BlogpostContentManagerForm(forms.ModelForm):
    """Класс формы модератора для редактирования карточки товара"""
    class Meta:
        model = Blogpost
        fields = ["status",]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
        }
