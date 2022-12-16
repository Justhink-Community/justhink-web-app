from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static  
from django.conf import settings
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),

]

handler404 = 'main.views.handle_404' 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += i18n_patterns(path("admin/", admin.site.urls))
