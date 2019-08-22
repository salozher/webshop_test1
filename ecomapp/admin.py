from django.contrib import admin
from ecomapp.models import Category, Brand, ArtObject, CartItem, Cart, Product_alternative


admin.site.register([Category, ArtObject, CartItem, Cart])