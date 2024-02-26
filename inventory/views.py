from datetime import datetime, date

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import F, Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from notifications.admin import Notification

from inventory.forms import UserCreationForm
from inventory.models import Product, Sale, Stock


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
    # Summary Statistics
    total_products = Product.objects.count()
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total_revenue=models.Sum('selling_price'))[
                        'total_revenue'] or 0  # Handle NULL case

    # Stock Overview
    low_stock_products = Product.objects.filter(stock__quantity__lte=F('stock__low_stock_threshold'))

    # Sales Overview
    recent_sales = Sale.objects.order_by('-sale_date')[:10]  # Get the 10 most recent sales

    # Sales Trends
    current_month_revenue = \
        Sale.objects.filter(sale_date__month=timezone.now().month).aggregate(total_revenue=models.Sum('selling_price'))[
            'total_revenue'] or 0
    previous_month_revenue = \
        Sale.objects.filter(sale_date__month=timezone.now().month - 1).aggregate(
            total_revenue=models.Sum('selling_price'))[
            'total_revenue'] or 0

    today_sales = Sale.objects.filter(sale_date=date.today())

    trend = None
    percentage_change = 0

    if current_month_revenue > previous_month_revenue:
        trend = "Up"
        if previous_month_revenue != 0:
            percentage_change = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
        else:
            percentage_change = 100
    elif current_month_revenue < previous_month_revenue:
        trend = "Down"
        if previous_month_revenue != 0:
            percentage_change = ((previous_month_revenue - current_month_revenue) / previous_month_revenue) * 100
        else:
            percentage_change = 100

    product_sales_percentage = {}
    total_stock_quantity = Stock.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    for sale in today_sales:
        product_stock = Stock.objects.get(product=sale.product)
        product_sales_percentage[sale.product] = (sale.quantity / product_stock.quantity) * 100

    stock = Stock.objects.all()
    product_quantities = {}
    products = Product.objects.all()

    for product in products:
        total_quantity = Stock.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))[
            'total_quantity']
        product_quantities[product.name] = total_quantity

    context = {
        'user': request.user,
        'notifications': user_notifications,
        'unread_notifications': user_notifications.filter(unread=True),
        'resent_actions': recent_actions,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'currentYear': datetime.now().year,
        'trend': trend,
        'percentage_change': percentage_change,
        'today_sales': today_sales,
        'product_sales_percentage': product_sales_percentage,
        'total_stock_quantity': total_stock_quantity,
        'product_quantities': product_quantities,
        'stock': stock
    }
    return render(request, 'inventory/home.html', context)


def logout_view(request):
    logout(request)
    return redirect(to='login')
