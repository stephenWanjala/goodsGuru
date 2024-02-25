from datetime import datetime

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from notifications.admin import Notification

from inventory.forms import UserCreationForm


# Create your views here.
class RegisterView(CreateView):
    template_name = 'inventory/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redirect to login page upon successful registration

    def form_valid(self, form):
        # Log the user in upon successful registration
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(to='/admin')
        redirect(to='home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect(to='/admin')
            return redirect(to='home')
        else:
            messages.info(request, 'Email or password is incorrect')
    context = {'messages': messages.get_messages(request=request), 'currentYear': datetime.now().year}
    return render(request=request, template_name='inventory/login.html', context=context)


@login_required(login_url='login')
def home(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    recent_actions = LogEntry.objects.all().order_by('-action_time')[:10]  # Fetching 10 most recent actions
    context = {
        'user': request.user,
        'notifications': user_notifications,
        'unread_notifications': user_notifications.filter(unread=True),
        'resent_actions': recent_actions,
    }
    return render(request, 'inventory/home.html', context)


def logout_view(request):
    logout(request)
    return redirect(to='login')
