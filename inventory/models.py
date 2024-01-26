from django.db import models

# Create your models here.


from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from notifications.signals import notify


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    expiry_date = models.DateField()
    responsible_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    low_stock_threshold = models.PositiveIntegerField(default=10)

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    acquisition_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update stock level
        stock, created = Stock.objects.get_or_create(product=self.product)
        stock.quantity += self.quantity
        stock.save()

        # Send notification
        if self.product.expiry_date <= timezone.now().date() + timezone.timedelta(weeks=1):
            notify.send(self.product, recipient=self.product.responsible_user, verb='Expiry Notification: Dispose of',
                        description=f'{self.product.name} is expiring soon and should be disposed of.')
        elif self.product.expiry_date <= timezone.now().date() + timezone.timedelta(weeks=12):
            notify.send(self.product, recipient=self.product.responsible_user,
                        verb='Expiry Notification: Priority Placement for',
                        description=f'{self.product.name} is expiring in 2-3 months and should be given priority '
                                    f'placement.')


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"
