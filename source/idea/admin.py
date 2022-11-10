from django.contrib import admin
from .models import Idea, Comment, Topic

# Register your models here.

admin.site.register(Topic)
admin.site.register(Idea)
admin.site.register(Comment)
