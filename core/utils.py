

from .models import Cart

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    return cart

# utils.py

# from hashlib import sha256
# from django.http import HttpRequest

# def get_client_ip(request: HttpRequest) -> str:
#     """Récupère l'IP réelle de l'utilisateur."""
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

# def get_device_fingerprint(request: HttpRequest) -> str:
#     """Génère une empreinte unique pour l'appareil."""
#     user_agent = request.META.get('HTTP_USER_AGENT', '')  # User agent de l'utilisateur
#     ip = get_client_ip(request)  # Récupère l'IP
#     fingerprint = f"{user_agent}{ip}"  # Combine l'IP et l'user agent pour générer une empreinte
#     return sha256(fingerprint.encode()).hexdigest()  # Retourne l'empreinte hashée

# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
import hashlib

def get_client_ip(request):
    """Récupère l'IP réelle de l'utilisateur (utile pour autre chose si besoin)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def get_device_fingerprint(request):
#     """Génère une empreinte fiable basée sur plusieurs caractéristiques du navigateur."""
#     user_agent = request.META.get('HTTP_USER_AGENT', '')
#     accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
#     accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
#     connection = request.META.get('HTTP_CONNECTION', '')
#     referer = request.META.get('HTTP_REFERER', '')
#     accept = request.META.get('HTTP_ACCEPT', '')

#     raw_fingerprint = f"{user_agent}|{accept_language}|{accept_encoding}|{connection}|{referer}|{accept}"
#     return hashlib.sha256(raw_fingerprint.encode()).hexdigest()


from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
import datetime

def get_online_users():
    User = get_user_model()
    online_users = []
    now = timezone.now()
    for user in User.objects.filter(is_active=True):
        last_seen = cache.get(f'seen_{user.id}')
        if last_seen and (now - last_seen).seconds < 600:  # Moins de 10 minutes
            online_users.append(user)
    return online_users

from django.contrib.auth import get_user_model
from django.core.cache import cache

def count_online_users():
    User = get_user_model()
    return sum(1 for user in User.objects.all() if cache.get(f'online-{user.id}'))


from core.models import Cart
from core.models import Cart
from core.serializers import CartItemSerializer
from core.models import Cart
from core.serializers import CartItemSerializer

def build_carts_by_country(user, request):
    """
    Regroupe les paniers actifs par pays et renvoie une structure adaptée à Flutter.
    """
    # ⚡ Récupère les paniers actifs
    carts = (
        Cart.objects.filter(user=user, is_ordered=False, is_active=True)
        .select_related("country__devise")
        .select_related("items__product__store__country")
        .prefetch_related("items__product")
    )

    carts_by_country = {}
    for c in carts:
        country = c.country
        if not country:
            continue

        country_id = country.id
        country_name = country.name
        currency = country.devise.code if hasattr(country, "devise") else "USD"

        if country_id not in carts_by_country:
            carts_by_country[country_id] = {
                "countryId": country_id,
                "countryName": country_name,
                "currency": currency,
                "items": [],
                "totalPrice": 0.0,
                "itemCount": 0,
            }

        # Sérialise les items du panier
        items_serializer = CartItemSerializer(
            c.items.all(), many=True, context={"request": request}
        )
        carts_by_country[country_id]["items"].extend(items_serializer.data)

        # Calcule le total et le nombre d'items
        total_price = sum(float(item.price) * item.quantity for item in c.items.all())
        total_count = sum(item.quantity for item in c.items.all())
        carts_by_country[country_id]["totalPrice"] += total_price
        carts_by_country[country_id]["itemCount"] += total_count

    return carts_by_country
