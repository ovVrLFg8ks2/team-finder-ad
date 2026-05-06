from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from team_finder.constants import (
    SKILL_NAME_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from team_finder.utils import make_avatar

from .managers import UserManager


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, null=False, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, null=True, blank=True, related_name="users")

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
        if is_new and not self.avatar:
            letter = self.name[0].upper()
            avatar_image = make_avatar(letter)
            self.avatar.save(f"avatar_{self.pk}.jpg", avatar_image, save=True)

    @property
    def formatted_phone(self):
        if not self.phone:
            return ""
        if self.phone.as_national.startswith('8 '):
            return self.phone.as_national.replace('8 ', '+7 ', 1)
        return self.phone.as_national
