from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser
from catalog.forms import CustomClearableFileInput


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, help_text="Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.")


    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "username", "first_name", "last_name", "country", "phone_number",
                  "avatar", "password1", "password2", "is_mailing_recipient")
        widgets = {
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7 999 123 45 67"}),
            "avatar": CustomClearableFileInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
            "is_mailing_recipient": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


    def clean_avatar(self):
        """Метод валидации поля формы 'аватар' на формат и размер файла"""
        avatar = self.cleaned_data.get("avatar")
        if hasattr(avatar, "content_type"):
            if avatar.content_type not in ["avatar/jpeg", "avatar/png"]:
                raise forms.ValidationError("Файл должен быть в формате JPEG или PNG")
            max_size_mb = 5
            if avatar.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size_mb} МБ")
        return avatar
