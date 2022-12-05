from django.contrib import admin
from .models import Profile

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.username == "FurkanEsen":
            return [f.name for f in obj._meta.fields if not f.editable]
        return [f.name for f in obj._meta.fields if not f.editable and f.name != "ip_addresses"]
 

admin.site.register(Profile, ProfileAdmin)
