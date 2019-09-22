from __future__ import unicode_literals
import random, string
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import random_generator, random_string_generator, unique_slug_generator, crypto_wallet_generator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


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

# class ArtObject(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.PROTECT)
#     title = models.CharField(max_length=120)
#     slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, editable=True)
#     description = models.TextField()
#     image = models.ImageField(upload_to=image_folder)
#     price = models.DecimalField(max_digits=9, decimal_places=2)
#     renttime = models.PositiveIntegerField(default=3)
#     available = models.BooleanField(default=True)
#     objects = ProductManager()
#
#     def __str__(self):
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse('product_detail', kwargs={'product_slug': self.slug})
#
#     def save(self, *args, **kwargs):
#         if self.slug:  # edit
#             if slugify(self.title) != self.slug:
#                 self.slug = unique_slug_generator(ArtObject, self.title)
#         else:  # create
#             self.slug = unique_slug_generator(ArtObject, self.title)
#         super(ArtObject, self).save(*args, **kwargs)
#
#
# def pre_save_art_slug(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         slug = unique_slug_generator(sender, instance)
#         # slug = slugify(instance.title)
#         instance.slug = slug
#
#
# pre_save.connect(pre_save_art_slug, sender=ArtObject)


# ----------------------------------------

class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
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
        user.crypto_wallet = 0
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(verbose_name='username', max_length=100, unique=True, )
    email = models.EmailField()
    crypto_wallet = models.CharField(verbose_name='Crypto wallet', max_length=100, unique=True, )
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
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def pre_save_user_wallet(sender, instance, *args, **kwargs):
    if not instance.crypto_wallet:
        wallet = crypto_wallet_generator(sender, instance)
        instance.crypto_wallet = wallet


pre_save.connect(pre_save_user_wallet, sender=MyUser)




class Art(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, editable=True)
    owner = models.ForeignKey(MyUser, related_name='artowner', on_delete=models.CASCADE, blank=True)
    temp_owner = models.ForeignKey(MyUser, null=True, related_name='artrenter', blank=True, on_delete=models.PROTECT)
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


# def pre_save_category_slug(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         slug = unique_slug_generator(sender, instance)
#         instance.slug = slug
#
#
# pre_save.connect(pre_save_category_slug, sender=Art)

class CartItem(models.Model):
    product = models.ForeignKey(Art, on_delete=models.PROTECT)
    rent_length = models.PositiveIntegerField(default=3)
    item_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return "Cart item for product {0}".format(self.product.title)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return str(self.id)

    def add_to_cart(self, product_slug):
        cart = self
        product = Art.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product, item_total=product.price)
        if new_item not in cart.items.all():
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

