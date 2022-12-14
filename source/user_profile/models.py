import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse

import hashlib

JUSTHINK_RANKS = {"ranks": (("rookie", "ROOKIE"),), "points": {"rookie": 0}}


class Profile(models.Model):

    account = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    shop_bought_products = models.JSONField(default=dict, editable=False)
    web_theme = models.CharField(editable=False, max_length=30) 

    kvkk_agreed = models.BooleanField(editable=False)
    email_permission = models.BooleanField(editable=False)

    login_count = models.IntegerField(default=0, editable=False)
    total_logged_time = models.DurationField(editable=False)
    last_logged_in = models.DateTimeField(editable=False)

    total_point = models.IntegerField(default=0, editable=False)
    login_strike = models.IntegerField(default=0, editable=False, null=False)

    # PROFILE FIELDS

    profile_rank = models.CharField(
        choices=JUSTHINK_RANKS["ranks"], default="rookie", editable=False, max_length=10
    )

    # USER SYSTEM

    profile_user = models.CharField(max_length=50, editable=False)

    profile_oses = models.JSONField(default=dict, editable=False)
    profile_platforms = models.JSONField(default=dict, editable=False)
    profile_browsers = models.JSONField(default=dict, editable=False)
    is_bot = models.BooleanField(default=False, editable=False)

    ip_addresses = models.JSONField(default=dict, editable=False)

    # MULTILAYER SECURITY PURPOSES 

    account_verifications = models.JSONField(default=dict, editable=False)
    # 2fa_status
    # remember_me_status
    # recovery_devices
    
    user_restricted = models.BooleanField(default=False, null=False, editable=True)

    user_notifications = models.JSONField(default=dict, editable=True, blank=True)

    # SOCIAL 

    profile_followers = models.JSONField(default=dict, editable=False, blank=True, null=True)

    @property
    def get_user_secret(self):
        return str(
            hashlib.sha256(str(self.account.id).encode()).hexdigest(),
        )[:30]

    def __str__(self):
        return self.account.username 

    def get_absolute_url(self,):
        return reverse('profile-page', args=[self.account.username,])