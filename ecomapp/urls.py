from django.conf.urls import url
from django.urls import path
from ecomapp.views import base_view, product_view, category_view, cart_view, add_to_cart_view

urlpatterns = [
    # url(r'^category/(?P<category_slug>[-\W]+)/S', category_view, name='category_detail'),
    path('category/<str:category_slug>/', category_view, name='category_detail'),

    path('product/<str:product_slug>/', product_view, name='product_detail'),
    # url(r'^product/(?P<product_slug>[-\W]+)/S', product_view, name='product_detail'),

    path('cart/', cart_view, name='cart'),
    # url(r'^cart/$', cart_view, name='cart'),

    # url(r'^add_to_cart/(?P<product_slug>[-\W]+)/S', add_to_cart_view, name='add_to_cart'),
    # path('cart/', add_to_cart_view, name='add_to_cart'),
    path('add_to_cart/<str:product_slug>/', add_to_cart_view, name='add_to_cart'),

    # url(r'^$', base_view, name='base'),
    path('', base_view, name='base')
]
