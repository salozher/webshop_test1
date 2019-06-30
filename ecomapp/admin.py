from django.contrib import admin
from ecomapp.models import Category, Brand, Product, CartItem, Cart


admin.site.register([Category, Brand, Product, CartItem, Cart])