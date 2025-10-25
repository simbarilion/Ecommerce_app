import json
import re
from typing import Any

from fuzzywuzzy import fuzz
from django import forms


def is_moderator(user):
    """Проверяет, состоит ли пользователь в группе модераторов"""
    return user.groups.filter(name="products_moderator").exists()


class SpamValidationMixin:
    """Миксин для проверки текстовых полей на запрещённые слова."""

    THRESHOLD = 85  # Порог похожести для fuzzy matching
    SPAM_WORDS_PATH = "catalog/data/spam_words.json"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.spam_words = self._load_spam_words(self.SPAM_WORDS_PATH)
        self.pattern = self._build_pattern(self.spam_words)


    @staticmethod
    def _load_spam_words(filepath: str) -> list:
        """Загружает список запрещённых слов из JSON файла"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            return [word.lower() for word in data.get("spam_words", [])]
        except FileNotFoundError:
            return []


    @staticmethod
    def _build_pattern(words: list) -> Any:
        """Создаёт паттерн для поиска запрещённых слов"""
        escaped = [re.escape(word) for word in words]
        return re.compile(r'(' + "|".join(escaped) + r')\w*', re.IGNORECASE)


    def _check_spam(self, text: str) -> None:
        """Проверяет текст на спам и запрещённые слова"""
        if not text:
            return

        text_lower = text.lower()
        if self.pattern.search(text_lower):
            raise forms.ValidationError("Текст содержит запрещённые слова, которые нельзя использовать")

        for spam in self.spam_words:
            if fuzz.partial_ratio(spam, text_lower) >= self.THRESHOLD:
                raise forms.ValidationError(f"Запрещённые слова, которые нельзя использовать: '{spam}'")
