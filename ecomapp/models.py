from __future__ import unicode_literals
import random, string
from .utils import random_string_generator, unique_slug_generator
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse


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



class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def image_folder(instance, filename):
    filename = instance.title + '-' + instance.slug + '.' + filename.split('.')[1]
    foldername = instance.slug
    return "{0}/{1}".format(foldername, filename)
    # return "{instance.slug - for folder name}/{filename}".format(instance.slug, filename)


class ProductManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(ProductManager, self).get_queryset().filter(available=True)


class ArtObject(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, editable=True)
    description = models.TextField()
    image = models.ImageField(upload_to=image_folder)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    available = models.BooleanField(default=True)
    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    def save(self, *args, **kwargs):
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = unique_slug_generator(ArtObject, self.title)
        else:  # create
            self.slug = unique_slug_generator(ArtObject, self.title)
        super(ArtObject, self).save(*args, **kwargs)


def pre_save_art_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = unique_slug_generator(sender, instance)
        # slug = slugify(instance.title)
        instance.slug = slug


pre_save.connect(pre_save_art_slug, sender=ArtObject)



def pre_save_category_wallet(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = unique_slug_generator(sender, instance)
        # slug = slugify(instance.title)
        instance.slug = slug


pre_save.connect(pre_save_category_wallet, sender=ArtObject)


# class TestModel(models.Model):
#     name = models.CharField(max_length=150)
#     slug = models.SlugField(unique=True, null=True, blank=True)
#
# pre_save.connect(models.signals.pre_save, sender=ArtObject)
#
# def auto_slug_generator(sender, instance, **kwargs):
#     """
#     Creates a slug if there is no slug.
#     """
#     if not instance.slug:
#         instance.slug = unique_slug_generator(instance)


# class Product_alternative(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.PROTECT)
#     brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
#     title = models.CharField(max_length=120)
#     slug = models.SlugField(max_length=200, unique=False, default=(random_string_generator(10)), editable=False)
#     description = models.TextField()
#     image = models.ImageField(upload_to=image_folder)
#     price = models.DecimalField(max_digits=9, decimal_places=2)
#     available = models.BooleanField(default=True)
#     objects = ProductManager()
#
#     def __str__(self):
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse('product_detail', kwargs={'product_slug': self.slug})


class CartItem(models.Model):
    product = models.ForeignKey(ArtObject, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=3)
    item_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return "Cart item for product {0}".format(self.product.title)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return str(self.id)
