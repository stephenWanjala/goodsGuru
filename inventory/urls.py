from django.urls import path

from .views import RegisterView, home, loginPage, logout_view, notifications, sales

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginPage, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
    path('notifications/', notifications, name='notifications'),
    path('sales/', sales, name='sales'),
]
