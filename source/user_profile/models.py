from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)

    web_theme = models.CharField(editable=False, max_length=10)

    kvkk_agreed = models.BooleanField()
    email_permission = models.BooleanField()

    login_count = models.IntegerField(default=0)
    total_logged_time = models.DurationField()
    last_logged_in = models.DateTimeField()
