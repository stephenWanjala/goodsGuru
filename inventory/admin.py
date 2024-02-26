from django.contrib import admin

from inventory.models import Supplier, Product, Stock, Purchase, Sale, InventoryUser


# Register your models here.

@admin.register(InventoryUser)
class InventoryUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_staff', 'is_active']
    search_fields = ['email', 'is_staff', 'is_active']
    list_filter = ['email']
    list_per_page = 10
    ordering = ['email']
    fieldsets = [
        ('User Information', {'fields': ['email', 'is_staff', 'is_active']}),
    ]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email']
    search_fields = ['name', 'contact_person', 'email']
    list_filter = ['name']
    list_per_page = 10
    ordering = ['name']
    fieldsets = [
        ('Supplier Information', {'fields': ['name', 'contact_person', 'email']}),
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'responsible_user', 'selling_price']
    search_fields = ['name', 'category', 'responsible_user']
    list_filter = ['name']
    list_per_page = 10
    ordering = ['name']
    fieldsets = [
        ('Product Information', {'fields': ['name', 'category', 'responsible_user', 'selling_price']}),
    ]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'low_stock_threshold']
    search_fields = ['product', 'quantity', 'low_stock_threshold']
    list_filter = ['product']
    list_per_page = 10
    ordering = ['product']
    fieldsets = [
        ('Stock Information', {'fields': ['product', 'quantity', 'low_stock_threshold']}),
    ]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'quantity', 'acquisition_price','expiration_date', 'purchase_date']
    search_fields = ['product', 'supplier', 'quantity', 'acquisition_price', 'purchase_date']
    list_filter = ['product']
    list_per_page = 10
    ordering = ['product']
    fieldsets = [
        ('Purchase Information',
         {'fields': ['product', 'supplier', 'quantity', 'acquisition_price', 'expiration_date', 'purchase_date']}),
    ]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'selling_price', 'sale_date']
    search_fields = ['product', 'quantity', 'selling_price', 'sale_date']
    list_filter = ['product']
    list_per_page = 10
    ordering = ['product']
    fieldsets = [
        ('Sale Information', {'fields': ['product', 'quantity',  'sale_date']}),
    ]
