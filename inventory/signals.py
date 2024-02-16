# inventory/signals.py
from django.core.mail import send_mail
from django.db.models import F
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from notifications.signals import notify

from inventory.models import Purchase, Stock, Sale


@receiver(post_save, sender=Purchase)
def handle_purchase(sender, instance, created, **kwargs):
    with transaction.atomic():
        stock, _ = Stock.objects.get_or_create(product=instance.product)
        stock.quantity = F('quantity') + instance.quantity
        stock.save()

        if instance.expiration_date <= timezone.now().date() + timezone.timedelta(weeks=1):
            notify.send(instance.product, recipient=instance.product.responsible_user,
                        verb='Expiry Notification: Dispose of',
                        description=f'{instance.product.name} is expiring soon and should be disposed of.')


@receiver(post_save, sender=Sale)
def handle_sale(sender, instance, created, **kwargs):
    with transaction.atomic():
        stock, _ = Stock.objects.get_or_create(product=instance.product)
        stock.quantity = F('quantity') - instance.quantity
        stock.save()

        if stock.is_low_stock():
            notify.send(stock, recipient=instance.product.responsible_user, verb='Low Stock Notification',
                        description=f'The stock of {instance.product.name} is low. Please order more.')

            # Send email notification to responsible user
            send_email_notification(instance.product.responsible_user.email, 'Low Stock Notification',
                                    f'The stock of {instance.product.name} is low. Please order more.')

            # Send email notification to supplier
            latest_purchase = instance.product.purchase_set.order_by('-purchase_date').first()
            if latest_purchase:
                send_email_notification(latest_purchase.supplier.email, 'Low Stock Notification',
                                        f'The stock of {instance.product.name} is low. Please supply more.')


def send_email_notification(recipient_email, subject, message):
    html_message = render_to_string('inventory/email_notification_template.html',
                                    {'subject': subject, 'message': message})
    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, 'devwanjala148@gmail.com', [recipient_email], html_message=html_message)
