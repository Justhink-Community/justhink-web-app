from django.contrib import admin
from .models import Idea, Comment, Topic, Update, Product

# Register your models here.

admin.site.register(Topic)
admin.site.register(Idea)
admin.site.register(Comment)
admin.site.register(Update)
admin.site.register(Product)
