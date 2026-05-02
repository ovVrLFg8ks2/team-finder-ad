from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image, ImageDraw, ImageFont
from random import randint
import io


class Skill(models.Model):
    name = models.CharField(max_length=124, null=False, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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

def make_avatar(letter):
    m = 125
    x = randint(0, 765)
    
    k = (255 - m) / 255
    r = int(max(0, abs(x - 382) - 127) * k + m)
    g = int(max(0, 255 - abs(x - 255)) * k + m)
    b = int(max(0, 255 - abs(x - 510)) * k + m)
    
    size = 128
    img = Image.new("RGB", (size, size), color=(r, g, b))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=size//2)
    except OSError:
        font = ImageFont.load_default(size=size//2)
    textbox = draw.textbbox((0, 0), letter, font=font)
    text_w = textbox[2] - textbox[0]
    text_h = textbox[3] - textbox[1]
    x = (size - text_w) / 2 - textbox[0]
    y = (size - text_h) / 2 - textbox[1]
    draw.text(
        (x, y), letter, 
        fill="black", font=font,
        stroke_width=3,
        stroke_fill="white"
    )
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue())


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
            self.avatar.save(f"avatar_{self.pk}.png", avatar_image, save=True)
    
    @property
    def formatted_phone(self):
        if not self.phone:
            return ""
        return self.phone.as_national.replace('8 ', '+7 ', 1) if self.phone.as_national.startswith('8 ') else self.phone.as_national