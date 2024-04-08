from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from inventory.models import Sale, Product


class UserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', "last_name", 'email', 'password1', 'password2')
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }
        help_texts = {
            'email': 'Required. Please enter a valid email address.',
        }


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        labels = {
            'email': 'Email',
            'password': 'Password',
        }
        help_texts = {
            'email': 'Required. Please enter a valid email address.',
        }


class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset for the product field to only include products with non-zero stock
        self.fields['product'].queryset = Product.objects.filter(stock__quantity__gt=0)

    class Meta:
        model = Sale
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select mb-3 form-control', 'placeholder': 'Select a product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control mb-2 ', 'min': '1'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'responsible_user', 'selling_price']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'category': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select category'}),
            'responsible_user': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Select responsible user'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter selling price'}),
        }
