# myapp/context_processors.py

from .models import Cart
from .utils import get_or_create_cart  # Assurez-vous que vous avez une fonction get_or_create_cart

def cart(request):
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)
    else:
        cart = None
    return {'cart': cart}


# core/context_processors.py

from .models import Notification, StoreSubscription
# core/context_processors.py
from .models import Notification, UserNotificationHide

def unread_notifications_count(request):
    if request.user.is_authenticated:
        hidden_ids = UserNotificationHide.objects.filter(user=request.user).values_list('notification_id', flat=True)
        count = Notification.objects.filter(user=request.user, is_read=False).exclude(id__in=hidden_ids).count()
        return {'unread_notifications_count': count}
    return {}

# def unread_notifications_count(request):
#     if request.user.is_authenticated:
#         # Récupère les stores auxquels l'utilisateur est abonné
#         subscribed_stores = StoreSubscription.objects.filter(user=request.user).values_list('store', flat=True)

#         # Récupère les notifications non lues de ces stores
#         count = Notification.objects.filter(user=request.user, store_id__in=subscribed_stores, is_read=False).count()
#     else:
#         count = 0

#     return {'unread_notifications_count': count}

