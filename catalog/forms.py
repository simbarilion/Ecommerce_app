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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "brief_description", "description", "image", "category", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "brief_description": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "category": forms.CheckboxInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }

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

    def clean_price(self):  # метод для валидации поля email
        price = self.cleaned_data.get("price")
        if price <= 0:
            raise forms.ValidationError("Цена не может быть отрицательной или равной нулю")
        return price
