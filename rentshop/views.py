from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LogoutView
from .models import Category, Art, CartItem, Cart
from .forms import ArtObjectForm
from django.views.generic import TemplateView, ListView, CreateView, DetailView


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


def cart_view(request):
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
    return render(request, 'cart.html', context)


def add_to_cart_view(request, product_slug):
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
    new_item, _ = CartItem.objects.get_or_create(product=product, item_total=product.price)
    if new_item not in cart.items.all():
        cart.items.add(new_item)
        cart.save()
        product.available = False
        product.save()
        return HttpResponseRedirect('/cart/')


def remove_from_cart_view(request, product_slug):
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
    for cart_item in cart.items.all():
        if cart_item.product == product:
            cart.items.remove(cart_item)
            cart.save()
            product.available = True
            product.save()
            return HttpResponseRedirect('/cart/')


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
    if request.method == 'POST':
        art = Art.objects.get(pk=pk)
        art.available = True
        art.temp_owner = None
        art.save()
    return redirect('class_art_list')
