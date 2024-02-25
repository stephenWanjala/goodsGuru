from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegisterView, home, loginPage, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginPage, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
]
