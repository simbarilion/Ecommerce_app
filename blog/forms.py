import json
import re

from django import forms
from fuzzywuzzy import fuzz

from .models import Blogpost


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


    THRESHOLD = 85


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


    def clean_title(self):
        title = self.cleaned_data.get("title")
        self._check_spam(title)
        return title
