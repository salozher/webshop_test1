from django.utils.text import slugify
import random
import string

# def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
#     return ''.join(random.choice(chars) for _ in range(size))

# def generate_unique_slug(klass, field):
#     """
#     return unique slug if origin slug is exist.
#     eg: `foo-bar` => `foo-bar-1`
#
#     :param `klass` is Class model.
#     :param `field` is specific field for title.
#     """
#     origin_slug = slugify(field)
#     unique_slug = origin_slug
#     numb = random_string_generator(size=6)
#     while klass.slug.filter(slug=unique_slug).exists():
#         unique_slug = '%s-%d' % (origin_slug, numb)
#     return unique_slug


# def unique_slug_generator(instance, new_slug=None):
#     if new_slug is not None:
#         slug = new_slug
#     else:
#         # We are using .lower() method for case insensitive
#         # you can use instance.<fieldname> if you want to use another field
#         str = instance.title.lower()
#         slug = slugify(str)
#
#     new_slug = "{slug}-{randstr}".format(slug=slug, randstr=random_string_generator(size=6))
#     # return unique_slug_generator(instance, new_slug=new_slug)
#     return new_slug







def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    # str = instance.title
    # slug = slugify(str)
    new_slug = "{randstr}".format(randstr=random_string_generator(size=6))
    return new_slug


def random_generator(size=40, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def crypto_wallet_generator(instance, new_wallet=None):
    new_wallet = "{prefix}{randstr}".format(prefix='0x', randstr=random_string_generator(size=40))
    return new_wallet

