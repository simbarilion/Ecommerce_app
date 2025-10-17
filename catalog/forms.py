import json
import re

from django import forms
from fuzzywuzzy import fuzz

from .models import MessageFeedback, Product


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = MessageFeedback
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = "widgets/custom_file_input.html"


class ProductForm(forms.ModelForm):
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

    THRESHOLD = 85

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Нет категории"
        self.spam_words = self._load_spam_words("catalog/data/spam_words.json")
        self.pattern = self._build_pattern(self.spam_words)


    @staticmethod
    def _load_spam_words(filepath):
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return [word.lower() for word in data.get("spam_words", [])]

    @staticmethod
    def _build_pattern(words):
        """Создание regex-паттерна, который ищет любые из запрещённых слов"""
        escaped = [re.escape(word) for word in words]
        return re.compile(r'(' + "|".join(escaped) + r')\w*', re.IGNORECASE)


    def _check_spam(self, text):
        """Проверка текста на запрещенные слова с fuzzy matching"""
        if not text:
            return
        text_lower = text.lower()
        if self.pattern.search(text_lower):
            raise forms.ValidationError("Текст содержит запрещенные слова, которые нельзя использовать")
        for spam in self.spam_words:
            score = fuzz.partial_ratio(spam, text_lower)
            if score >= self.THRESHOLD:
                raise forms.ValidationError(f"Запрещенные слова, которые нельзя использовать: '{spam}'")


    def clean_name(self):
        name = self.cleaned_data.get("name")
        self._check_spam(name)
        return name


    def clean_brief_description(self):
        brief_description = self.cleaned_data.get("brief_description")
        self._check_spam(brief_description)
        return brief_description


    def clean_description(self):
        description = self.cleaned_data.get("description")
        self._check_spam(description)
        return description


    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price <= 0:
            raise forms.ValidationError("Цена не может быть отрицательной или равной нулю")
        return price


    def clean_image(self):
        image = self.cleaned_data.get("image")
        if hasattr(image, 'content_type'):
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise forms.ValidationError("Файл должен быть в формате JPEG или PNG")
            max_size_mb = 5
            if image.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size_mb} МБ")
        return image
