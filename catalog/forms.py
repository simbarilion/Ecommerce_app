from django import forms
from .models import MessageFeedback, Product


SPAM_WORDS = ["казино", "биржа", "обман", "криптовалюта", "дешево", "полиция", "крипта", "бесплатно", "радар"]


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
        for word in SPAM_WORDS:
            if word in name:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в названиях")
        return name

    def clean_brief_description(self):
        brief_description = self.cleaned_data.get("brief_description")
        for word in SPAM_WORDS:
            if word in brief_description:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в описании товара")
        return brief_description

    def clean_description(self):
        description = self.cleaned_data.get("description")
        for word in SPAM_WORDS:
            if word in description:
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
