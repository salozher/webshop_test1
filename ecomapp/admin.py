from django.contrib import admin
from ecomapp.models import Category, ArtObject, CartItem, Cart


admin.site.register([Category, ArtObject, CartItem, Cart])