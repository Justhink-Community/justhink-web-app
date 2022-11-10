from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)

    web_theme = models.CharField(editable=False, max_length=10)

    kvkk_agreed = models.BooleanField()
    email_permission = models.BooleanField()
