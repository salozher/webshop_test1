from __future__ import unicode_literals
from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from .utils import unique_slug_generator, order_id_generator, \
    make_btc_account
from blockchain import blockexplorer, exchangerates
# from rentshop.views import btc_current_rates


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})


def pre_save_category_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        # slug = unique_slug_generator(sender, instance)
        slug = slugify(instance.name)
        instance.slug = slug


pre_save.connect(pre_save_category_slug, sender=Category)


def image_folder(instance, filename):
    filename = instance.title + '-' + instance.slug + '.' + filename.split('.')[1]
    foldername = instance.slug
    return "{0}/{1}".format(foldername, filename)
    # return "{instance.slug - for folder name}/{filename}".format(instance.slug, filename)


class ProductManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(ProductManager, self).get_queryset().filter(available=True)


class OrderManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(OrderManager, self).get_queryset().all()


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not username:
            raise ValueError('Users must have a user name')
        if not email:
            raise ValueError('User must have a valid email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.is_admin = False
        user.is_employee = False
        user.is_student = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email and password.
        """
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_admin = True
        user.is_employee = True
        user.is_student = True
        user.crypto_balanse = 0
        user.private_key = 0
        user.public_key = 0
        user.crypto_wallet = 0
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(verbose_name='username', max_length=100, unique=True, )
    email = models.EmailField()
    private_key = models.CharField(verbose_name='Crypto wallet private (secret) key', max_length=100, unique=True)
    public_key = models.CharField(verbose_name='Crypto wallet public key', max_length=130, unique=True)
    crypto_wallet = models.CharField(verbose_name='Public Bitcoin Address', max_length=100, unique=True)
    crypto_balanse = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


def pre_save_user_btc_account_set(sender, instance, *args, **kwargs):
    if not instance.private_key:
        btc_account_set = make_btc_account(sender, instance)
        instance.private_key = btc_account_set[0]
        instance.public_key = btc_account_set[1]
        instance.crypto_wallet = btc_account_set[2]


pre_save.connect(pre_save_user_btc_account_set, sender=MyUser)



class Art(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, editable=True)
    owner = models.ForeignKey(MyUser, related_name='artowner', on_delete=models.CASCADE, blank=True)
    temp_owner = models.ForeignKey(MyUser, null=True, related_name='art_renter', blank=True, on_delete=models.PROTECT)
    cover = models.ImageField(upload_to=image_folder, null=True, blank=True)
    rent_start_date = models.DateField(default=timezone.now(), blank=True)
    rent_end_date = models.DateField(default=timezone.now(), blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    objects = ProductManager()

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.cover.delete()
        super(Art, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})


def pre_save_art_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = unique_slug_generator(sender, instance)
        # slug = slugify(instance.title)
        instance.slug = slug


pre_save.connect(pre_save_art_slug, sender=Art)


class CartItem(models.Model):
    product = models.ForeignKey(Art, on_delete=models.CASCADE)
    rent_length = models.PositiveIntegerField(default=3)
    item_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    btc_item_total = models.DecimalField(max_digits=12, decimal_places=8, default=0.00000000)

    def __unicode__(self):
        return "Cart item for product {0}".format(self.product.title)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    btc_cart_total = models.DecimalField(max_digits=12, decimal_places=8, default=0.00000000)

    def __unicode__(self):
        return str(self.id)

    def add_to_cart(self, product_slug):
        btc_rates = exchangerates.get_ticker()
        btc_eur_rate = btc_rates.get('EUR').buy
        eur_btc_rate = float('{:09.8f}'.format(1 / btc_eur_rate))
        cart = self
        product = Art.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product, item_total=product.price)
        if new_item not in cart.items.all():
            new_item.rent_length = 3
            new_item.item_total = new_item.item_total*3
            new_item.btc_item_total = '{:12.8f}'.format(float(new_item.item_total) * eur_btc_rate)
            new_item.save()
            cart.items.add(new_item)
            cart.save()
            product.available = False
            product.save()

    def remove_from_cart(self, product_slug):
        cart = self
        product = Art.objects.get(slug=product_slug)
        for cart_item in cart.items.all():
            if cart_item.product == product:
                cart.items.remove(cart_item)
                cart.save()
                product.available = True
                product.save()


class Order(models.Model):
    order_id = models.CharField(verbose_name='Order id', max_length=100, unique=True, editable=True, blank=True)
    art_item = models.CharField(verbose_name='Art item', max_length=200, unique=False, editable=True, blank=True)
    renting_person = models.CharField(verbose_name='Renting person email', max_length=200, unique=False, editable=False,
                                      blank=True)
    order_start_date = models.DateField(default=timezone.now(), blank=True)
    order_end_date = models.DateField(default=timezone.now(), blank=True)
    transaction_complete = models.BooleanField(default=False)
    amount_payed = models.DecimalField(max_digits=10, decimal_places=7)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=7)
    objects = OrderManager()

    def __str__(self):
        return "Order Number{0}:".format(str(self.id))


def pre_save_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        order_id = order_id_generator(sender, instance)
        instance.order_id = order_id


pre_save.connect(pre_save_order_id, sender=Order)
