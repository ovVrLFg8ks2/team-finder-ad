from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.CharField(max_length=1024)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
    
    @property
    def formatted_phone(self):
        if not self.phone:
            return ""
        return self.phone.as_national.replace('8 ', '+7 ', 1) if self.phone.as_national.startswith('8 ') else self.phone.as_national