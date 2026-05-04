from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.widgets import RegionalPhoneNumberWidget

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Email',
            'password': 'Пароль',
        }
        fields = ['name', 'surname', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(),
    )


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "avatar": forms.FileInput(),
            "about": forms.Textarea(attrs={"rows": 4}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/username"}),
            'phone': RegionalPhoneNumberWidget(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот номер уже занят")
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        if "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return url


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Неверный текущий пароль")
        return old_password

    def clean(self):
        cleaned = super().clean()
        pswrd = cleaned.get("new_password1")
        pswrdch = cleaned.get("new_password2")
        if pswrd and pswrdch and pswrd != pswrdch:
            self.add_error("new_password2", "Пароли не совпадают")
        return cleaned
