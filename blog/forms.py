from django import forms

from .models import Blogpost


SPAM_WORDS = ["казино", "биржа", "обман", "криптовалюта", "дешево", "полиция", "крипта", "бесплатно", "радар"]


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = "widgets/custom_file_input.html"


class BlogpostForm(forms.ModelForm):
    class Meta:
        model = Blogpost
        fields = ["title", "content", "preview"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 20}),
            "preview": CustomClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        for word in SPAM_WORDS:
            if word in title:
                raise forms.ValidationError("Запрещенные слова, которые нельзя использовать в названиях")
        return title
