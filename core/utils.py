

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
