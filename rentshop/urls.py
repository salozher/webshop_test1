from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from rentshop.views import home_view, product_view, category_view, cart_view, add_to_cart_view, remove_from_cart_view, \
    ArtsOfOwnerInRent, ArtsOfOwner, UploadArtView, delete_art, remove_from_cart_all_view, return_art

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # url(r'^category/(?P<category_slug>[-\W]+)/S', category_view, name='category_detail'),
    path('category/<str:category_slug>/', category_view, name='category_detail'),

    path('product/<str:product_slug>/', product_view, name='product_detail'),
    # url(r'^product/(?P<product_slug>[-\W]+)/S', product_view, name='product_detail'),

    path('class/artsinrent/', ArtsOfOwnerInRent.as_view(), name='class_art_list_in_use'),
    path('class/arts/', ArtsOfOwner.as_view(), name='class_art_list'),

    path('class/arts/upload/', UploadArtView.as_view(), name='class_upload_art'),
    path('arts/<int:pk>/', delete_art, name='delete_art'),
    path('artsreturn/<int:pk>/', return_art, name='return_art'),

    path('cart/', cart_view, name='cart'),
    # url(r'^cart/$', cart_view, name='cart'),

    # url(r'^add_to_cart/(?P<product_slug>[-\W]+)/S', add_to_cart_view, name='add_to_cart'),
    # path('cart/', add_to_cart_view, name='add_to_cart'),
    path('add_to_cart/<str:product_slug>/', add_to_cart_view, name='add_to_cart'),

    path('remove_from_cart/<str:product_slug>/', remove_from_cart_view, name='remove_from_cart'),
    path('remove_all_and_logout/', remove_from_cart_all_view, name='remove_all_and_logout'),

    # url(r'^$', base_view, name='base'),
    path('', home_view, name='home')
]
