from django import forms
from .models import MessageFeedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = MessageFeedback
        fields = ["name", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
