from django.urls import path
from .views import IndexView, LoginView, RegisterView, LogoutView

urlpatterns = [
    path("", IndexView, name="index-page"),
    path('login', LoginView, name = 'login-page'),
    path('register', RegisterView, name = 'register-page'), 
    path('logout', LogoutView, name =  'logout-page')
]
