# context_processors.py

from datetime import datetime

from django.contrib.admin.models import LogEntry
from django.db.models import Sum, F
from django.utils import timezone
from notifications.models import Notification

from inventory.models import Sale, Product, Stock


def inventory_context(request):
    if request.user.is_authenticated:
        # Notification data
        user_notifications = Notification.objects.filter(recipient=request.user)
        unread_notifications = user_notifications.filter(unread=True)

        recent_actions = LogEntry.objects.filter(user=request.user).order_by('-action_time')[:10]

        # Summary statistics
        total_sales = Sale.objects.count()
        total_revenue = round(Sale.objects.aggregate(total_revenue=Sum('selling_price'))['total_revenue'] or 0, 2)
        low_stock_products = Product.objects.filter(stock__quantity__lte=F('stock__low_stock_threshold'))
        recent_sales = Sale.objects.order_by('-sale_date')[:10]

        # Sales trends
        current_month_revenue = round(
            Sale.objects.filter(sale_date__month=timezone.now().month).aggregate(total_revenue=Sum('selling_price'))[
                'total_revenue'] or 0, 2
        )
        previous_month_revenue = round(
            Sale.objects.filter(sale_date__month=timezone.now().month - 1).aggregate(
                total_revenue=Sum('selling_price'))[
                'total_revenue'] or 0, 2
        )

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

        # Today's sales
        today_sales = Sale.objects.filter(sale_date=timezone.now().date())
        percentage_change = round(percentage_change, 2)

        # Product sales percentage
        product_sales_percentage = {}
        for sale in today_sales:
            product_stock = Stock.objects.get(product=sale.product)
            product_sales_percentage[sale.product] = (sale.quantity / product_stock.quantity) * 100

        # Total stock quantity and product quantities
        total_stock_quantity = Stock.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        product_quantities = {
            product.name: Stock.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))[
                              'total_quantity'] or 0 for product in Product.objects.all()}

        return {
            'user_notifications': user_notifications,
            'unread_notifications': unread_notifications,
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
            'resent_actions': recent_actions,
        }
    return {}
