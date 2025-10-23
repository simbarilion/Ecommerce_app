from django.contrib.auth import login
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from config.settings import BASE_DIR
from .forms import CustomUserCreationForm
import os
from dotenv import load_dotenv


load_dotenv(BASE_DIR / ".env")


class RegisterView(FormView):
    """Класс регистрации пользователя"""
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("catalog:home")


    def form_valid(self, form):
        """Сохраняет данные пользователя в базу данных, осуществляет вход пользователя в систему как авторизованного"""
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)


    @staticmethod
    def send_welcome_email(user_email):
        """Отправляет на почту пользователя письмо об успешной регистрации на сайте"""
        subject = "Добро пожаловать в Skystore"
        message = "Спасибо, что зарегистрировались в нашем сервисе!"
        from_email = os.getenv("EMAIL_HOST_USER")
        recipient_list = [user_email,]
        send_mail(subject, message, from_email, recipient_list)
