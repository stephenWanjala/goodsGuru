from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegisterView, home, loginPage

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginPage, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]
