# models.py
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from notifications.signals import notify


class InventoryUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class InventoryUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = InventoryUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


User = get_user_model()


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        verbose_name_plural = "Suppliers"
        verbose_name = "Supplier"

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Groceries', 'Groceries'),
        ('Clothing', 'Clothing'),
        ('Home and Furniture', 'Home and Furniture'),
        ('Books', 'Books'),
        ('Beauty and Personal Care', 'Beauty and Personal Care'),
        ('Sports and Outdoors', 'Sports and Outdoors'),
        # Add more categories as needed
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    responsible_user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def expiration_date(self):
        # Retrieve the latest purchase and its expiration date for the product
        latest_purchase = self.purchase_set.order_by('-purchase_date').first()
        if latest_purchase:
            return latest_purchase.expiration_date
        return None

    def is_expired(self):
        expiration_date = self.expiration_date
        return expiration_date is not None and expiration_date < timezone.now().date()

    class Meta:
        verbose_name_plural = "Products"
        verbose_name = "Product"

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    class Meta:
        verbose_name_plural = "Stocks"
        verbose_name = "Stock"

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    acquisition_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField()  # New field for the expiration date

    class Meta:
        verbose_name_plural = "Purchases"
        verbose_name = "Purchase"

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # The update_stock signal will take care of updating the stock and sending notifications


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Sales"
        verbose_name = "Sale"

    def __str__(self):
        return f"{self.product.name} - Quantity: {self.quantity}"

    def save(self, *args, **kwargs):
        # Check if there is enough stock available for the sale
        stock, created = Stock.objects.get_or_create(product=self.product)
        if stock.quantity >= self.quantity:
            super().save(*args, **kwargs)

            # Update stock level after a sale
            stock.quantity -= self.quantity
            stock.save()

            # Check and notify if stock is low after the sale
            if stock.is_low_stock():
                notify.send(stock, recipient=self.product.responsible_user, verb='Low Stock Notification',
                            description=f'The stock of {self.product.name} is low. Please order more.')

        else:
            raise ValueError(f"Not enough stock available for {self.product.name} - Quantity: {self.quantity}")
