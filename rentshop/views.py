from datetime import date
from decimal import Decimal
from blockchain import blockexplorer
from django.core.mail import send_mass_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .forms import ArtObjectForm
from .models import Category, Art, CartItem, Cart, MyUser, OrderHistory
from .utils import btc_current_rates, rent_enddate_calculator, btc_gate_simulator


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


def home_view(request):
    cart = cart_create(request)
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
    cart = cart_create(request)
    product = Art.objects.get(slug=product_slug)
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'cart': cart,
    }
    return render(request, 'product.html', context)


def category_view(request, category_slug):
    cart = cart_create(request)
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
    cart = cart_create(request)

    user_btc_balance_enough = False
    if (user_crypto_balance(request) >= cart.btc_cart_total):
        user_btc_balance_enough = True

    cart_is_not_empty = False
    if (cart.items.count() > 0):
        cart_is_not_empty = True
    else:
        cart_is_not_empty = False
    context = {
        'cart': cart,
        'categories': categories,
        'btc_balance': btc_balance,
        'eur_btc_rate': eur_btc_rate,
        'user_btc_balance_enough': user_btc_balance_enough,
        'cart_is_not_empty': cart_is_not_empty,
    }
    return render(request, 'cart.html', context)


def add_to_cart_view(request):
    eur_btc_rate = btc_current_rates()
    cart = cart_create(request)
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
    cart = cart_create(request)
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

    cart_is_not_empty = False
    if (cart.items.count() > 0):
        cart_is_not_empty = True
    else:
        cart_is_not_empty = False
    return JsonResponse(
        {'cart_total_items': cart.items.count(),
         'cart_total_price': cart.cart_total,
         'cart_btc_total_price': cart.btc_cart_total,
         'user_btc_balance_enough': user_btc_balance_enough,
         'cart_is_not_empty': cart_is_not_empty
         })


def remove_from_cart_all_view(request):
    cart = cart_create(request)
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


class ArtsOfOwnerInRent(ListView):
    template_name = 'class_art_list_in_use.html'

    # context_object_name = 'products'
    def get(self, request, *args, **kwargs):
        cart = cart_create(request)
        categories = Category.objects.all()
        current_user = MyUser.objects.get(username=request.user.username)
        if (current_user.is_employee):
            products_in_rent = Art.objects.filter(owner=current_user).filter(available=False)
        elif (current_user.is_student):
            products_in_rent = Art.objects.filter(temp_owner=current_user).filter(available=False)
        context = {
            'categories': categories,
            'products': products_in_rent,
            'cart': cart,
        }
        return render(request, self.template_name, context)


class ArtsOfOwner(ListView):
    model = Art
    template_name = 'class_art_list.html'
    context_object_name = 'products'
    def get(self, request, *args, **kwargs):
        cart = cart_create(request)
        categories = Category.objects.all()
        products = Art.objects.filter(owner=request.user)
        context = {
            'categories': categories,
            'products': products,
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
            art.payment_successful = False
            art.temp_owner = None
            art.save()
        else:
            pass
    return redirect('class_art_list_in_use')


def change_rent_period(request):
    request = request
    eur_btc_rate = btc_current_rates()
    cart = cart_create(request)

    period = request.GET.get('period')
    if (int(period) < 3):
        period = 3
    elif (int(period) >12):
        period = 12
    item_id = request.GET.get('item_id')
    cart_item = CartItem.objects.get(id=int(item_id))
    cart_item.rent_length = int(period)
    cart_item.item_total = int(period) * Decimal(cart_item.product.price)
    cart_item.btc_item_total = '{:12.8f}'.format(float(cart_item.item_total) * eur_btc_rate)
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
    cart = cart_create(request)
    context = {
        'cart': cart,
        'categories': categories,
    }
    return render(request, 'order.html', context)


def complete_order(request):
    # user = MyUser.objects.get(crypto_wallet=pk)
    user = MyUser.objects.get(username=request.user.username)
    cart_id = request.session['cart_id']
    cart = Cart.objects.get(id=cart_id)
    mailinglist = ()
    for ordered_item in cart.items.all():
        product = Art.objects.get(slug=ordered_item.product.slug)
        # product = ordered_item.product
        product_title = product.title
        ordered_item_owner = product.owner.username
        owner_email = product.owner.email
        price_to_pay = str(ordered_item.item_total)
        btc_price_to_pay = float(ordered_item.btc_item_total)
        order_period = str(ordered_item.rent_length)
        renter_email = user.email
        renter_name = user.username
        order = OrderHistory()
        order.item_title = product.title
        order.slug = product.slug
        order.owner_email = owner_email
        order.temp_owner_email = renter_email
        order.rent_start_date = date.today()
        enddate = rent_enddate_calculator(int(order_period))
        order.rent_end_date = enddate
        order.payment_amount = price_to_pay
        order.save()

        payment_successfull = btc_gate_simulator(user.crypto_wallet, product.owner.crypto_wallet, btc_price_to_pay)

        if (payment_successfull):
            product.payment_successful = True
            product.available = False
            product.rent_end_date = enddate
            product.temp_owner = user
            cart.items.remove(ordered_item)
            cart.save()
            product.save()

            message_to_student = ("Sergiy's ArtShop item ordered: " + product_title,
                                  "Thank you for ordering an art object " + product_title + " from " +
                                  ordered_item_owner + "! You can contact the owner by email: " +
                                  owner_email + " to arrange the item delivery to you.",
                                  'SergiyRentShop@gmail.com', [renter_email],)

            message_to_owner = ("Sergiy's ArtShop: Your item " + product_title + " is ordered!",
                                "Sergiy's ArtShop: Your item " + product_title + " is ordered by " +
                                renter_name + " for a period of " + order_period + " month! The price amount of $" +
                                price_to_pay + " (BTC " + str(btc_price_to_pay) + ") is transferred to your BTC wallet. Please contact renting person by following email " +
                                renter_email + " to arrange the item delivery.",
                                "SergiyRentShop@gmail.com", [owner_email],)
            mailinglist = mailinglist + (message_to_student, message_to_owner,)
        else:
            return HttpResponseRedirect('/orderfailed')
        send_mass_mail(mailinglist, fail_silently=False)
    # return HttpResponse('Mail successfully sent')
    return HttpResponseRedirect('/ordersuccess')


def order_history(request):
    request = request
    current_user = MyUser.objects.get(username=request.user.username)

    categories = Category.objects.all()
    if (current_user.is_student):
        orders = OrderHistory.objects.all().filter(temp_owner_email=current_user.email)
    else:
        orders = OrderHistory.objects.all().filter(owner_email=current_user.email)
    cart = cart_create(request)

    context = {
        'cart': cart,
        'categories': categories,
        'orders': orders,
    }
    return render(request, 'order_history.html', context)


def order_success(request):
    current_user = MyUser.objects.get(username=request.user.username)
    if (current_user.is_student):
        orders = OrderHistory.objects.all().filter(temp_owner_email=current_user.email)
    else:
        orders = OrderHistory.objects.all().filter(owner_email=current_user.email)
    cart = cart_create(request)
    categories = Category.objects.all()
    context = {
        'cart': cart,
        'categories': categories,
        'orders': orders,
    }

    return render(request, 'order_success.html', context)


def order_failed(request):
    return render(request, 'order_failed.html')
