from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.manager import CustomUserManager
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    slug = models.UUIDField(default=uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
