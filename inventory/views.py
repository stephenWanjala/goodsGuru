from datetime import datetime

from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from notifications.admin import Notification

from inventory.forms import UserCreationForm, SaleForm, ProductForm
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
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='home')
    else:
        form = ProductForm()

    stock = Stock.objects.all()

    context = {
            'stock': stock,
            'main_title': 'Products Dashboard',
            'form': form
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
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            # Create a LogEntry to log the sale creation action
            content_type = ContentType.objects.get_for_model(sale)
            LogEntry.objects.create(
                user_id=request.user.id,
                content_type_id=content_type.id,
                object_id=sale.id,
                object_repr=str(sale),
                action_flag=ADDITION,
                change_message=f'Sale added - Product: {sale.product}, Quantity: {sale.quantity}, Amount: {sale.selling_price}',
                action_time=sale.sale_date,
            )
            return redirect(to='home')
    else:
        form = SaleForm()
    sales = Sale.objects.all()
    context = {
        'sales': sales,
        'form': form,
        'main_title': 'Sales Dashboard'
    }
    return render(request, 'inventory/sales.html', context)


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect(to='login')
