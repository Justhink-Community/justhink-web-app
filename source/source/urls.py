from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static  
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
    re_path(r'media/(?P<path>.*)', serve,{'document_root': settings.MEDIA_ROOT}),
]

handler404 = 'main.views.handle_404' 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
