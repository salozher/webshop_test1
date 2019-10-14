from django.utils.text import slugify
import random
import string
import hashlib
import ecdsa
import os
from binascii import hexlify
from base58 import b58encode


def random_secret_exponent(curve_order):
    while True:
        bytes = os.urandom(32)
        random_hex = hexlify(bytes)
        random_int = int(random_hex, 16)
        if random_int >= 1 and random_int < curve_order:
            return random_int


def generate_private_key():
    curve = ecdsa.curves.SECP256k1
    secret_exponent = random_secret_exponent(curve.order)
    from_secret_exponent = ecdsa.keys.SigningKey.from_secret_exponent
    return from_secret_exponent(secret_exponent, curve, hashlib.sha256).to_string()


def get_public_key_uncompressed(private_key):
    key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    return b'\04' + key.get_verifying_key().to_string()  # 0x04 = uncompressed key prefix


def get_bitcoin_address(public_key, prefix=b'\x00'):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(public_key).digest())
    a = prefix + ripemd160.digest()
    checksum = hashlib.sha256(hashlib.sha256(a).digest()).digest()[0:4]
    return b58encode(a + checksum)


def make_btc_account(instance, new_set=None):
    # private_key = generate_private_key()

    #     or:
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1).to_string()

    public_key = get_public_key_uncompressed(private_key)
    address = get_bitcoin_address(public_key)

    print(f'private key: {hexlify(private_key)}')
    print(f'public key uncompressed: {hexlify(public_key)}')
    print(f'btc address: {address}')

    key1 = hexlify(private_key).decode('utf-8')
    key2 = hexlify(public_key).decode('utf-8')
    btc_account = address.decode('utf-8')

    new_set = [
        key1,
        key2,
        btc_account
    ]
    return new_set






def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    # str = instance.title
    # slug = slugify(str)
    new_slug = "{randstr}".format(randstr=random_string_generator(size=6))
    return new_slug


def random_generator(size=40, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def order_id_generator(instance, new_order_id=None):
    new_order_id = "{prefix}{randstr}".format(prefix='order_', randstr=random_string_generator(size=40))
    return new_order_id

