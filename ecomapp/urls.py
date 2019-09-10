from django.conf.urls import url
from django.contrib.auth import views
from django.urls import path
from .views import home_view, product_view, category_view, cart_view, add_to_cart_view, remove_from_cart_view

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # url(r'^category/(?P<category_slug>[-\W]+)/S', category_view, name='category_detail'),
    path('category/<str:category_slug>/', category_view, name='category_detail'),

    path('product/<str:product_slug>/', product_view, name='product_detail'),
    # url(r'^product/(?P<product_slug>[-\W]+)/S', product_view, name='product_detail'),

    path('cart/', cart_view, name='cart'),
    # url(r'^cart/$', cart_view, name='cart'),

    # url(r'^add_to_cart/(?P<product_slug>[-\W]+)/S', add_to_cart_view, name='add_to_cart'),
    # path('cart/', add_to_cart_view, name='add_to_cart'),
    path('add_to_cart/<str:product_slug>/', add_to_cart_view, name='add_to_cart'),

    path('remove_from_cart/<str:product_slug>/', remove_from_cart_view, name='remove_from_cart'),

    # url(r'^$', base_view, name='base'),
    path('', home_view, name='home')
]
