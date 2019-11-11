from django.shortcuts import render, redirect
from decimal import Decimal
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import LogoutView
from .models import Category, Art, CartItem, Cart, MyUser, OrderHistory
from .forms import ArtObjectForm
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from datetime import *
from django.contrib import messages
import smtplib, ssl, csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse
from blockcypher import get_address_overview, get_address_details
from blockchain import blockexplorer, exchangerates
from dateutil.relativedelta import *
from datetime import date


def home_view(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    categories = Category.objects.all()
    products = Art.objects.all(available=True)
    context = {
        'categories': categories,
        'products': products,
        'cart': cart,
    }
    # returns render(request, template of certain product or element, context dictionary)
    return render(request, 'home.html', context)


def product_view(request, product_slug):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    product = Art.objects.get(slug=product_slug)
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'cart': cart,
    }
    return render(request, 'product.html', context)


def category_view(request, category_slug):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    categories = Category.objects.all()
    category = Category.objects.get(slug=category_slug)
    products_of_category = Art.objects.filter(category=category).filter(available=True)
    context = {
        'category': category,
        'categories': categories,
        'products_of_category': products_of_category,
        'cart': cart,
    }
    return render(request, 'category.html', context)


def btc_current_rates():
    btc_rates = exchangerates.get_ticker()
    btc_eur_rate = btc_rates.get('EUR').buy
    eur_btc_rate = float('{:09.8f}'.format(1 / btc_eur_rate))
    return eur_btc_rate


def user_crypto_balance(request):
    user = MyUser.objects.get(username=request.user.username)
    btc_user_info = blockexplorer.get_address(user.crypto_wallet)
    btc_balance = btc_user_info.final_balance / 100000000
    return btc_balance


def cart_view(request):
    request = request
    categories = Category.objects.all()
    btc_balance = user_crypto_balance(request)
    eur_btc_rate = btc_current_rates()
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id

    user_btc_balance_enough = False
    if (user_crypto_balance(request) >= cart.btc_cart_total):
        user_btc_balance_enough = True

    cart_is_not_empty = False
    if (cart.items.count() > 0):
        cart_is_not_empty = True
        print(cart_is_not_empty)
    else:
        print(cart_is_not_empty)

    context = {
        'cart': cart,
        'categories': categories,
        'btc_balance': btc_balance,
        'eur_btc_rate': eur_btc_rate,
        'user_btc_balance_enough': user_btc_balance_enough,
        'cart_is_not_empty': cart_is_not_empty,
    }
    print(cart_is_not_empty)
    return render(request, 'cart.html', context)


def add_to_cart_view(request):
    eur_btc_rate = btc_current_rates()
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    product_slug = request.GET.get('product_slug')
    product = Art.objects.get(slug=product_slug)
    cart.add_to_cart(product.slug)
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.btc_cart_total = '{:12.8f}'.format(cart.cart_total * eur_btc_rate)
    cart.save()
    return JsonResponse(
        {'cart_total': cart.items.count()})


def remove_from_cart_view(request):
    request = request
    eur_btc_rate = btc_current_rates()
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    product_slug = request.GET.get('product_slug')
    product = Art.objects.get(slug=product_slug)
    cart.remove_from_cart(product.slug)
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.btc_cart_total = '{:12.8f}'.format(cart.cart_total * eur_btc_rate)
    cart.save()

    user_btc_balance_enough = False
    balance = float(user_crypto_balance(request))
    total = float(cart.btc_cart_total)
    if (balance >= total):
        user_btc_balance_enough = True
    else:
        user_btc_balance_enough = False
    print(user_btc_balance_enough)

    cart_is_not_empty = False
    if (cart.items.count() > 0):
        cart_is_not_empty = True
        print(cart_is_not_empty)
    else:
        print(cart_is_not_empty)

    return JsonResponse(
        {'cart_total_items': cart.items.count(),
         'cart_total_price': cart.cart_total,
         'cart_btc_total_price': cart.btc_cart_total,
         'user_btc_balance_enough': user_btc_balance_enough,
         'cart_is_not_empty': cart_is_not_empty
         })


def remove_from_cart_all_view(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    # product = Art.objects.get(slug=product_slug)
    for cart_item in cart.items.all():
        if cart_item:
            prod = cart_item.product
            cart.items.remove(cart_item)
            cart.save()
            prod.available = True
            prod.save()
        else:
            pass
    return HttpResponseRedirect('/logout')


def cart_create(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    return cart


def products_in_rent(request):
    return Art.objects.filter(owner=request.user).filter(available=False)


def products(request):
    return Art.objects.filter(owner=request.user)


class ArtsOfOwnerInRent(ListView):
    template_name = 'class_art_list_in_use.html'
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        try:
            cart_id = request.session['cart_id']
            cart = Cart.objects.get(id=cart_id)
            request.session['total'] = cart.items.count()
        except:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            request.session['cart_id'] = cart_id
            cart = Cart.objects.get(id=cart_id)
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'products': products_in_rent(request),
            'cart': cart,
        }
        return render(request, self.template_name, context)


class ArtsOfOwner(ListView):
    model = Art
    template_name = 'class_art_list.html'
    context_object_name = 'products'

    # def get_queryset(self):
    #     return Art.objects.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            cart_id = request.session['cart_id']
            cart = Cart.objects.get(id=cart_id)
            request.session['total'] = cart.items.count()
        except:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            request.session['cart_id'] = cart_id
            cart = Cart.objects.get(id=cart_id)
        categories = Category.objects.all()
        # products = Art.objects.filter(owner=self.request.user)
        context = {
            'categories': categories,
            'products': products(request),
            'cart': cart,
        }
        return render(request, self.template_name, context)


class UploadArtView(CreateView):
    model = Art
    form_class = ArtObjectForm
    success_url = reverse_lazy('class_art_list')
    template_name = 'add_new_art.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(UploadArtView, self).form_valid(form)


def delete_art(request, pk):
    if request.method == 'POST':
        art = Art.objects.get(pk=pk)
        art.delete()
    return redirect('class_art_list')


def return_art(request, pk):
    present = date.today()
    if request.method == 'POST':
        art = Art.objects.get(pk=pk)
        if (art.rent_end_date <= present):
            art.available = True
            art.temp_owner = None
            art.save()
        else:
            pass
    return redirect('class_art_list_in_use')


def change_rent_period(request):
    request = request
    eur_btc_rate = btc_current_rates()
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)

    period = request.GET.get('period')
    item_id = request.GET.get('item_id')
    cart_item = CartItem.objects.get(id=int(item_id))
    cart_item.rent_length = int(period)
    cart_item.item_total = int(period) * Decimal(cart_item.product.price)
    cart_item.btc_item_total = '{:12.8f}'.format(float(cart_item.item_total) * eur_btc_rate)
    print(cart_item.btc_item_total)

    cart_item.save()
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.btc_cart_total = '{:12.8f}'.format(cart.cart_total * eur_btc_rate)
    cart.save()

    user_btc_balance_enough = False
    balance = float(user_crypto_balance(request))
    total = float(cart.btc_cart_total)
    if (balance >= total):
        user_btc_balance_enough = True
    else:
        user_btc_balance_enough = False
    print(user_btc_balance_enough)


    cart_is_empty = True
    if (int(cart.items.count()) > 0):
        cart_is_empty = False

    return JsonResponse(
        {'cart_total_items': cart.items.count(),
         'item_total': cart_item.item_total,
         'cart_total_price': cart.cart_total,
         'cart_btc_total_price': cart.btc_cart_total,
         'user_btc_balance_enough': user_btc_balance_enough,
         'balance': balance,
         'total': total,
         'cart_is_empty': cart_is_empty,

         })


def make_order(request):
    categories = Category.objects.all()
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
    context = {
        'cart': cart,
        'categories': categories,
    }
    return render(request, 'order.html', context)

def rent_enddate_calculator(period_month):
    start_date = date.today()
    end_date = start_date+relativedelta(months= +period_month)
    return end_date

def complete_order(request):
    # user = MyUser.objects.get(crypto_wallet=pk)
    user = MyUser.objects.get(username=request.user.username)

    cart_id = request.session['cart_id']
    cart = Cart.objects.get(id=cart_id)

    for ordered_item in cart.items.all():
        product = ordered_item.product
        product_title = product.title
        ordered_item_owner = product.owner.username
        owner_email = product.owner.email
        price_to_pay = str(ordered_item.item_total)
        order_period = str(ordered_item.rent_length)
        renter_email = user.email
        renter_name = user.username
        order = OrderHistory()
        order.item_title = product.title
        order.slug = product.slug
        order.owner_email = owner_email
        order.temp_owner_email = renter_email
        order.rent_start_date = date.today()
        order.rent_end_date = rent_enddate_calculator(int(order_period))
        order.payment_amount = price_to_pay
        order.save()

        # mailinglist = ()
        # message_to_student = ("Sergiy's ArtShop item ordered: " + product_title,
        #                       "Thank you for ordering an art object " + product_title + " from " +
        #                       ordered_item_owner + "! You can contact the owner by email: " +
        #                       owner_email + " to arrange the item delivery to you.",
        #                       'SergiyRentShop@gmail.com', [renter_email],)
        #
        # message_to_owner = ("Sergiy's ArtShop: Your item " + product_title + " is ordered!",
        #                     "Sergiy's ArtShop: Your item " + product_title + " is ordered by " +
        #                     renter_name + " for a period of " + order_period + " month! The price amount of $" +
        #                     price_to_pay + " is transferred to your BTC wallet. Please contact renting person by following email " +
        #                     renter_email + " to arrange the item delivery.",
        #                     "SergiyRentShop@gmail.com", [owner_email],)
        # mailinglist = mailinglist + (message_to_student, message_to_owner,)
        #
        # send_mass_mail(mailinglist, fail_silently=False)
    # return HttpResponse('Mail successfully sent')
    return HttpResponseRedirect('/orderhistory')


def sendmail(request):
    to_addr = 'sergiy.piano@gmail.com'
    send_mail(
        'Subject',
        'Email message',
        'sergiyrentshop@gmail.com',
        [to_addr],
        fail_silently=False,
    )

    return HttpResponse('Mail successfully sent')



def order_history(request):
    request = request
    current_user = MyUser.objects.get(username=request.user.username)

    categories = Category.objects.all()
    if(current_user.is_student):
        orders = OrderHistory.objects.all().filter(temp_owner_email=current_user.email)
    else:
        orders = OrderHistory.objects.all().filter(owner_email=current_user.email)
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id


    context = {
        'cart': cart,
        'categories': categories,
        'orders': orders,
    }
    return render(request, 'order_history.html', context)


