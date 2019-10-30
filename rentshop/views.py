from django.shortcuts import render, redirect
from decimal import Decimal
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import LogoutView
from .models import Category, Art, CartItem, Cart, MyUser
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
    products = Art.objects.all()
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

def check_balance(request):
    pass


def cart_view(request):
    categories = Category.objects.all()
    user = MyUser.objects.get(username=request.user.username)
    btc_user_info = blockexplorer.get_address(user.crypto_wallet)
    btc_balance = btc_user_info.final_balance / 100000000
    btc_rates = exchangerates.get_ticker()
    btc_eur_rate = btc_rates.get('EUR').buy
    eur_btc_rate = '{:09.8f}'.format(1 / btc_eur_rate)
    print(btc_balance)
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
        'btc_balance': btc_balance,
        'eur_btc_rate': eur_btc_rate,

    }
    return render(request, 'cart.html', context)


def add_to_cart_view(request):
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
    cart.save()
    return JsonResponse(
        {'cart_total': cart.items.count()})


def remove_from_cart_view(request):
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
    cart.save()

    return JsonResponse(
        {'cart_total': cart.items.count(),
         'cart_total_price': cart.cart_total})


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
    cart_item.save()
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    return JsonResponse(
        {'cart_total': cart.items.count(),
         'item_total': cart_item.item_total,
         'cart_total_price': cart.cart_total})


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


def send_fancy_email(owner_email):
    sender_email = "sergiyrentshop@gmail.com"
    receiver_email = owner_email['email']
    password = 'Password2019'
    # renter_email = renter_email

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    html = """\
    <html>
      <body>
        <p>Hi,<br>
           How are you?<br>
           <a href="http://www.realpython.com">Real Python</a> 
           has many great tutorials.
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    return HttpResponseRedirect('/cart')


def complete_order(request, pk):
    user = MyUser.objects.get(crypto_wallet=pk)

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

        mailinglist = ()
        message_to_student = ("Sergiy's ArtShop item ordered: " + product_title,
                  "Thank you for ordering an art object " + product_title + " from " +
                  ordered_item_owner + "! You can contact the owner by email: " +
                  owner_email + " to arrange the item delivery to you.",
                  'SergiyRentShop@gmail.com', [renter_email],)

        message_to_owner = ("Sergiy's ArtShop: Your item " + product_title + " is ordered!",
                  "Sergiy's ArtShop: Your item " + product_title + " is ordered by " +
                  renter_name + " for a period of " + order_period + " month! The price amount of $" +
                  price_to_pay + " is transferred to your BTC wallet. Please contact renting person by following email " +
                  renter_email + " to arrange the item delivery.",
                  "SergiyRentShop@gmail.com", [owner_email],)
        mailinglist = mailinglist + (message_to_student, message_to_owner,)

        send_mass_mail(mailinglist, fail_silently=False)
    return HttpResponse('Mail successfully sent')


# return HttpResponseRedirect('/cart')


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
