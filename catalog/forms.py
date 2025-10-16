import re

from django import forms
from rapidfuzz import fuzz

from .models import MessageFeedback, Product


SPAM_WORDS = [
    "казино", "биржа", "обман", "криптовалюта", "дешево", "полиция", "крипта", "бесплатно", "радар",
    "игровые автоматы", "гемблинг", "ставки", "азартные игры", "слоты", "лохотрон", "мошенничество",
    "scam", "фейк", "крипта", "биткоин", "эфириум", "altcoin", "токен", "blockchain", "низкая цена",
    "скидка", "акция", "распродажа", "выгодно", "free", "подарок", "без оплаты", "даром", "радар",
    "отслеживание", "слежка",
]
PATTERN = re.compile(r'\b(' + '|'.join(SPAM_WORDS) + r')\b', re.IGNORECASE)
THRESHOLD = 80


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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Нет категории"


    def clean_name(self):
        name = self.cleaned_data.get("name")
        if PATTERN.search(name):
            raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в названиях")
        for spam in SPAM_WORDS:
            if spam.lower() in name.lower():
                raise forms.ValidationError("Запрещенные слова!")
        for spam in SPAM_WORDS:
            if fuzz.ratio(spam, name) > THRESHOLD:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в названиях")
        return name


    def clean_brief_description(self):
        brief_description = self.cleaned_data.get("brief_description")
        if PATTERN.search(brief_description):
            raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в описании товара")
        for spam in SPAM_WORDS:
            if fuzz.ratio(spam, brief_description) > THRESHOLD:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в описании товара")
        return brief_description


    def clean_description(self):
        description = self.cleaned_data.get("description")
        if PATTERN.search(description):
            raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в описании товара")
        for spam in SPAM_WORDS:
            if fuzz.ratio(spam, description) > THRESHOLD:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в описании товара")
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
