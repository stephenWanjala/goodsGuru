# inventory/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from notifications.signals import notify

from .models import Product


@receiver(post_save, sender=Product)
def send_disposal_notification(sender, instance, **kwargs):
    if instance.expiry_date <= timezone.now().date() + timezone.timedelta(weeks=1):
        notify.send(instance, recipient=instance.responsible_user, verb='Expiry Notification: Dispose of',
                    description=f'{instance.name} is expiring soon and should be disposed of.')


@receiver(post_save, sender=Product)
def send_priority_placement_notification(sender, instance, **kwargs):
    if instance.expiry_date <= timezone.now().date() + timezone.timedelta(weeks=12):
        notify.send(instance, recipient=instance.responsible_user, verb='Expiry Notification: Priority Placement for',
                    description=f'{instance.name} is expiring in 2-3 months and should be given priority placement.')
