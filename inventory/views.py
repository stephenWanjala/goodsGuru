from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from notifications.admin import Notification

from inventory.forms import UserCreationForm, SaleForm
from inventory.models import Sale, Stock


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
    stock = Stock.objects.all()

    context = {
        'stock': stock,
        'main_title': 'Products Dashboard'
    }
    return render(request, 'inventory/home.html', context)


@login_required(login_url='login')
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    context = {
        'notifications': user_notifications,
        'unread_notifications': user_notifications.filter(unread=True),
        'currentYear': datetime.now().year,
        'main_title': 'Notifications'
    }
    return render(request, 'inventory/notifications.html', context)


@login_required(login_url='login')
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.unread = False
    notification.save()
    return redirect(to='notifications')


@login_required(login_url='login')
def mark_all_as_read(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    for notification in user_notifications:
        notification.unread = False
        notification.save()
    return redirect(to='notifications')


@login_required(login_url='login')
def sales(request):
    sales = Sale.objects.all()
    # recent_actions = LogEntry.objects.all().order_by('-action_time')[:10]  # Fetching 10 most recent actions
    context = {
        'sales': sales,
        # 'recent_actions': recent_actions,
        'currentYear': datetime.now().year,
        'main_title': 'Sales'
    }
    return render(request, 'inventory/sales.html', context)


@login_required(login_url='login')
def make_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            try:
                sale.save()
                return redirect('sales')  # Redirect to sales page after successful sale
            except Exception as e:
                # Handle database-related exceptions, if necessary
                form.add_error(None, "An error occurred while processing the sale. Please try again later.")
    else:
        form = SaleForm()

    return render(request, 'inventory/make_sale_form.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect(to='login')
