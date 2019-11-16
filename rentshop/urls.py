from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from rentshop.views import (
    home_view,
    product_view,
    category_view,
    cart_view,
    add_to_cart_view,
    remove_from_cart_view,
    ArtsOfOwnerInRent,
    ArtsOfOwner,
    UploadArtView,
    delete_art,
    remove_from_cart_all_view,
    return_art, change_rent_period,
    make_order, complete_order,
    order_success,
    order_failed,
    order_history
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('category/<str:category_slug>/', category_view, name='category_detail'),
    path('product/<str:product_slug>/', product_view, name='product_detail'),

    path('artsinrent/', ArtsOfOwnerInRent.as_view(), name='class_art_list_in_use'),
    path('arts/', ArtsOfOwner.as_view(), name='class_art_list'),

    path('arts/upload/', UploadArtView.as_view(), name='class_upload_art'),
    path('arts/<int:pk>/', delete_art, name='delete_art'),
    path('artsreturn/<int:pk>/', return_art, name='return_art'),
    path('change_rent_period/', change_rent_period, name='change_rent_period'),

    path('makeorder/', make_order, name='make_order'),
    path('complete_order/', complete_order, name='complete_order'),
    path('orderhistory/', order_history, name='order_history'),
    path('ordersuccess/', order_success, name='order_success'),
    path('orderfailed/', order_failed, name='order_failed'),

    path('cart/', cart_view, name='cart'),
    path('add_to_cart/', add_to_cart_view, name='add_to_cart'),
    path('remove_from_cart/', remove_from_cart_view, name='remove_from_cart'),
    path('remove_all_and_logout/', remove_from_cart_all_view, name='remove_all_and_logout'),

    path('', home_view, name='home')
]
