from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Country, City,TypeBusiness,TypeProduct

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "country", "city", "profile_pic_preview")
    list_filter = ("is_staff", "is_superuser", "is_active", "country", "city")
    search_fields = ("username", "email", "phone")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {
            "fields": (
                "first_name", "last_name", "email", "phone", "address",
                "commune", "country", "city", "interests", "profile_pic"
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ("phone", "address", "commune", "country", "city", "interests", "profile_pic")
        }),
    )

    def profile_pic_preview(self, obj):
        if obj.profile_pic:
            return f'<img src="{obj.profile_pic.url}" width="40" height="40" style="border-radius: 50%;" />'
        return "—"
    profile_pic_preview.allow_tags = True
    profile_pic_preview.short_description = "Photo"

# Enregistrer Country et City aussi
admin.site.register(Country)
admin.site.register(City)


from django.contrib import admin
from .models import Store, Typestore, Country, City,StoreSubscription,Testimonial,SpotPubStore

from django.utils.html import format_html

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'typestore', 'typebusiness', 'country', 'city',
        'is_active', 'favoritestore', 'created_at'
    )
    list_filter = ('is_active', 'country', 'city', 'typestore', 'typebusiness')
    search_fields = ('name', 'owner__email', 'city__name', 'country__name')
    prepopulated_fields = {"slug": ("name",)}

    # ✅ Affiche une preview mais permet l'upload
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>', obj.thumbnail.url)
        return "Pas d'image"
    thumbnail_preview.short_description = "Aperçu"

    readonly_fields = ('thumbnail_preview',)  # Pas le champ réel
    fields = (
        'name', 'slug', 'owner', 'typestore', 'typebusiness',
        'country', 'city', 'adresse', 'description',
        'thumbnail_preview', 'thumbnail',
        'latitude', 'longitude', 'is_active', 'favoritestore'
    )


# Register related models if not already
admin.site.register(Typestore)
admin.site.register(TypeBusiness)
admin.site.register(TypeProduct)

@admin.register(StoreSubscription)
class StoreSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'subscribed_at')
    list_filter = ('subscribed_at', 'store')
    search_fields = ('user__username', 'user__email', 'store__name')
    date_hierarchy = 'subscribed_at'

class TestimonialAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la liste d'administration
    list_display = ('store', 'user', 'rating', 'created_at', 'content_snippet')

    # Ajout d'un filtre pour la date de création
    list_filter = ('created_at', 'rating')

    # Ajout d'une barre de recherche (par exemple par le nom de l'utilisateur ou le contenu)
    search_fields = ('user__username', 'content')

    # Ajout d'une fonctionnalité pour trier les témoignages
    ordering = ('-created_at',)

    # Raccourcir l'affichage du contenu (pour ne pas afficher tout le texte dans la liste)
    def content_snippet(self, obj):
        # Limite le texte à 100 caractères
        return obj.content[:100] + '...'
    content_snippet.short_description = 'Extrait du témoignage'

    # Personnaliser le formulaire dans l'admin
    fieldsets = (
        (None, {
            'fields': ('store', 'user', 'content', 'rating')
        }),
        ('Informations supplémentaires', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # Rendre le champ 'created_at' en lecture seule
    readonly_fields = ('created_at',)

# Enregistrement de l'admin
admin.site.register(Testimonial, TestimonialAdmin)


@admin.register(SpotPubStore)
class SpotPubStoreAdmin(admin.ModelAdmin):
    list_display = ('store', 'uploaded_at')
    search_fields = ('store__name',)
    readonly_fields = ('uploaded_at',)

    def has_add_permission(self, request):
        # Empêche l'ajout manuel depuis l'admin, car le lien est OneToOne avec Store
        return False

from django.contrib import admin
from .models import StoreVisit

@admin.register(StoreVisit)
class StoreVisitAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'ip_address', 'date', 'count')
    list_filter = ('date', 'store')
    search_fields = ('store__name', 'user__username', 'ip_address')
    ordering = ('-date',)


from django.contrib import admin
from .models import Notification
from django.utils.html import format_html

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description_preview', 'created_at', 'is_read', 'image_display')
    list_filter = ('is_read', 'created_at')  # Filtrage basé sur 'is_read' maintenant
    search_fields = ('title', 'description')

    # Permet d'afficher une prévisualisation de la description
    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

    # Affichage de l'image dans l'admin
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{0}" width="100" height="100" />', obj.image.url)
        return "Pas d'image"
    image_display.short_description = 'Image'

    # Actions supplémentaires : marquer comme lue ou non lue
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lue"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Marquer comme non lue"

# Enregistrement de l'admin
admin.site.register(Notification, NotificationAdmin)


from django.contrib import admin
from .models import UserNotificationHide

@admin.register(UserNotificationHide)
class UserNotificationHideAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'hidden_at')
    list_filter = ('hidden_at',)
    search_fields = ('user__email', 'notification__title')
    autocomplete_fields = ('user', 'notification')



from .models import ContactStore

class ContactStoreAdmin(admin.ModelAdmin):
    # Définir les champs à afficher dans la liste
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'store', 'created_at')
    
    # Ajouter des filtres pour faciliter la recherche
    list_filter = ('created_at', 'store',)
    
    # Ajouter un champ de recherche pour rechercher des contacts par nom ou email
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'store__name')

    # Configurer les champs qui peuvent être édités directement dans la liste (in-line editing)
    list_editable = ('phone_number', 'email')

    # Configuration des actions
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        # Exemple d'action personnalisée pour marquer les demandes comme traitées
        queryset.update(description="Demande traitée")
        self.message_user(request, "Les demandes sélectionnées ont été marquées comme traitées.")

    mark_as_processed.short_description = "Marquer comme traitée"

# Enregistrer le modèle avec l'admin
admin.site.register(ContactStore, ContactStoreAdmin)


from .models import Category

# Define the Category admin class
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'store')  # Columns to display in the list view
    search_fields = ('name',)  # Enable search by name
    list_filter = ('store',)  # Allow filtering categories by store
    ordering = ('store', 'name')  # Order categories by store and name

    # You can add more customization if necessary
    # e.g., make store a read-only field for categories already created
    readonly_fields = ('store',)

# Register the Category model with the CategoryAdmin class
admin.site.register(Category, CategoryAdmin)

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Photo, Testimonialproduct, TypeProduct
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('image',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'type_product', 'price', 'price_with_commission',
        'stock', 'image_tag', 'video_tag', 'total_purchased', 'total_buyers', 'created_at'
    )
    list_filter = (
        'category', 'type_product', 'price', 'stock', 'created_at',
    )
    search_fields = [
        'name', 'category__name', 'type_product__nom', 'price',
        'store__name'
    ]
    inlines = [PhotoInline]
    fields = (
        'name', 'category', 'type_product', 'price', 'price_with_commission',
        'stock', 'image', 'image_galerie', 'video', 'description', 'store',
        'total_purchased', 'total_buyers'
    )
    readonly_fields = (
        'price_with_commission', 'total_purchased', 'total_buyers',
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Pas d'image"
    image_tag.short_description = 'Image'

    def video_tag(self, obj):
        if obj.video:
            return format_html(
                '<video width="80" height="50" controls><source src="{}" type="video/mp4">Votre navigateur ne supporte pas la vidéo.</video>',
                obj.video.url
            )
        return "Pas de vidéo"
    video_tag.short_description = "Vidéo"

    def total_purchased(self, obj):
        return obj.total_purchased
    total_purchased.short_description = "Unités vendues"

    def total_buyers(self, obj):
        return obj.total_buyers
    total_buyers.short_description = "Acheteurs uniques"


admin.site.register(Product, ProductAdmin)

admin.site.register(Photo)





class TestimonialproductAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la liste d'administration
    list_display = ('product', 'user', 'rating', 'created_at', 'content_snippet')

    # Ajout d'un filtre pour la date de création
    list_filter = ('created_at', 'rating')

    # Ajout d'une barre de recherche (par exemple par le nom de l'utilisateur ou le contenu)
    search_fields = ('user__username', 'content')

    # Ajout d'une fonctionnalité pour trier les témoignages
    ordering = ('-created_at',)

    # Raccourcir l'affichage du contenu (pour ne pas afficher tout le texte dans la liste)
    def content_snippet(self, obj):
        # Limite le texte à 100 caractères
        return obj.content[:100] + '...'
    content_snippet.short_description = 'Extrait du témoignage'

    # Personnaliser le formulaire dans l'admin
    fieldsets = (
        (None, {
            'fields': ('product', 'user', 'content', 'rating')
        }),
        ('Informations supplémentaires', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # Rendre le champ 'created_at' en lecture seule
    readonly_fields = ('created_at',)

# Enregistrement de l'admin
admin.site.register(Testimonialproduct, TestimonialproductAdmin)


from .models import ContactProduct

class ContactProductAdmin(admin.ModelAdmin):
    # Définir les champs à afficher dans la liste
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'product', 'created_at')
    
    # Ajouter des filtres pour faciliter la recherche
    list_filter = ('created_at', 'product',)
    
    # Ajouter un champ de recherche pour rechercher des contacts par nom ou email
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'product__name')

    # Configurer les champs qui peuvent être édités directement dans la liste (in-line editing)
    list_editable = ('phone_number', 'email')

    # Configuration des actions
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        # Exemple d'action personnalisée pour marquer les demandes comme traitées
        queryset.update(description="Demande traitée")
        self.message_user(request, "Les demandes sélectionnées ont été marquées comme traitées.")

    mark_as_processed.short_description = "Marquer comme traitée"

# Enregistrer le modèle avec l'admin
admin.site.register(ContactProduct, ContactProductAdmin)


from django.contrib import admin
from .models import AssignerCategory

@admin.register(AssignerCategory)
class AssignerCategoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'category')  # Afficher ces colonnes dans la liste admin
    search_fields = ('product__name', 'category__name')  # Ajouter une recherche
    list_filter = ('category',)  # Ajouter un filtre par catégorie



from .models import Cart,CartItem
class CartAdmin(admin.ModelAdmin):
    # Colonnes affichées dans l'admin
    list_display = (
        'user',
        'country',  # Ajout du pays
        'created_at',
        'total_with_commission',
        'item_count',
        'is_ordered',
        'is_active'
    )

    # Filtres disponibles dans l'admin
    list_filter = (
        'created_at',
        'user',
        'country',  # Ajout du filtre par pays
        'is_ordered',
        'is_active'
    )

    # Recherche dans l'admin
    search_fields = ('user__username', 'country__name')

    # Méthode pour afficher le total avec commission
    def total_with_commission(self, obj):
        return obj.get_total()

    total_with_commission.short_description = 'Total avec commission'

    # Méthode pour afficher le nombre d'articles
    def item_count(self, obj):
        return obj.get_item_count()

    item_count.short_description = 'Nombre d\'articles'

# Enregistrer le modèle Cart avec son admin personnalisé
admin.site.register(Cart, CartAdmin)



# Admin pour CartItem
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'total_price')  # Colonnes affichées
    list_filter = ('cart', 'product')  # Filtres dans l'admin
    search_fields = ('product__name', 'cart__user__username')  # Recherche par produit et utilisateur

    # Méthode pour afficher le prix total d'un article dans le panier
    def total_price(self, obj):
        return obj.get_total_price()  # Appelle la méthode get_total_price du modèle CartItem pour afficher le prix total

    total_price.short_description = 'Prix total'

# Enregistrer le modèle CartItemAdmin
admin.site.register(CartItem, CartItemAdmin)


from django.contrib import admin
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price_at_time_of_order']  # Champs visibles dans l'inline
    readonly_fields = ['get_store']  # Afficher 'get_store' comme champ en lecture seule

    # Méthode pour récupérer le store du produit
    def get_store(self, obj):
        return obj.product.store.name if obj.product and obj.product.store else None  # Accéder au store via le produit
    get_store.short_description = _('Store')

class OrderAdmin(admin.ModelAdmin):
    # ✅ Affichage avec country
    list_display = (
        'id', 'user', 'country', 'get_stores', 'status', 'activated',
        'total_amount', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'country', 'created_at', 'activated')  # ✅ Ajout de 'country'
    search_fields = ('user__username', 'status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

    actions = ['mark_as_shipped', 'calculate_total', 'activate_order', 'update_user_points']

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, _("Les commandes ont été marquées comme expédiées."))
    mark_as_shipped.short_description = _("Marquer comme expédiée")

    def calculate_total(self, request, queryset):
        for order in queryset:
            order.calculate_total()
        self.message_user(request, _("Les montants totaux ont été recalculés."))
    calculate_total.short_description = _("Calculer le montant total")

    def activate_order(self, request, queryset):
        queryset.update(activated=True)
        self.message_user(request, _("Les commandes ont été activées."))
    activate_order.short_description = _("Activer les commandes Mobile Money")

    def get_stores(self, obj):
        stores = set(item.product.store.name for item in obj.items.all() if item.product.store)
        return ", ".join(stores)
    get_stores.short_description = _("Magasins associés")

    def update_user_points(self, request, queryset):
        for order in queryset:
            order.update_user_points()
        self.message_user(request, _("Les points des utilisateurs ont été mis à jour."))
    update_user_points.short_description = _("Mettre à jour les points des utilisateurs")
   
    # def update_user_points(self, request, queryset):
    #     """Action pour mettre à jour les points de l'utilisateur après 5 achats"""
    #     for order in queryset:
    #         order.update_user_points()  # Appel de la méthode pour chaque commande sélectionnée
    #     self.message_user(request, _("Les points des utilisateurs ont été mis à jour après l'achat."))
    # update_user_points.short_description = _("Mettre à jour les points des utilisateurs")


# Enregistrement des modèles dans l'admin
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)

from django.contrib import admin
from .models import UserPoints
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'ad_points', 'total_purchases', 'spent_points', 'get_user_email')
    search_fields = ('user__username', 'user__email')
    list_filter = ('points', 'ad_points', 'total_purchases', 'spent_points')  # Ajout du filtre sur spent_points
    ordering = ('user',)

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "Email de l'utilisateur"

    def total_points(self, obj):
        return obj.points
    total_points.short_description = "Total des points"

    def has_add_permission(self, request):
        return False  # Empêche l'ajout manuel

    def has_delete_permission(self, request, obj=None):
        return False  # Empêche la suppression des UserPoints

    def reset_all_points(self, request, queryset):
        queryset.update(points=0, ad_points=0, spent_points=0)  # Réinitialisation complète
        self.message_user(request, "Les points ont été réinitialisés pour les utilisateurs sélectionnés.")
    reset_all_points.short_description = "Réinitialiser tous les points"

    def reset_ad_points(self, request, queryset):
        queryset.update(ad_points=0)
        self.message_user(request, "Les points publicitaires ont été réinitialisés.")
    reset_ad_points.short_description = "Réinitialiser uniquement les points publicitaires"

    actions = ['reset_all_points', 'reset_ad_points']

admin.site.register(UserPoints, UserPointsAdmin)

from .utils import get_or_create_cart 
from .models import MobileMoneyPayment
from .models import Cart, Order, OrderItem,DeviseCountry,NumeroPaye
# admin.py
from django.utils.translation import gettext_lazy as _

class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'transaction_number', 'transaction_id',
        'first_name', 'last_name', 'country', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at', 'country')  # ajout du filtre par pays
    search_fields = ('transaction_number', 'user__username', 'transaction_id')
    actions = ['validate_payment']

    def validate_payment(self, request, queryset):
        # Marquer les paiements comme validés
        queryset.update(status='validated')

        # Créer la commande pour chaque paiement validé
        for payment in queryset:
            cart = get_or_create_cart(payment.user)

            # Filtrer les cart items du pays correspondant au paiement
            cart_items = cart.items.filter(product__store__country=payment.country)

            if not cart_items.exists():
                continue  # Rien à commander si aucun item pour ce pays

            order = Order.objects.create(
                user=payment.user,
                status='paid',
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_time_of_order=cart_item.product.price
                )

            order.calculate_total()
            cart_items.delete()  # Ne supprime que les items de ce pays

        self.message_user(request, _("Les paiements ont été validés et les commandes ont été créées."))

    validate_payment.short_description = _("Valider les paiements et créer les commandes")

admin.site.register(MobileMoneyPayment, MobileMoneyPaymentAdmin)

admin.site.register(DeviseCountry)
admin.site.register(NumeroPaye)

from django.contrib import admin
from .models import StoreCoManager

@admin.register(StoreCoManager)
class StoreCoManagerAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'added_at')
    search_fields = ('store__name', 'user__email')
    list_filter = ('added_at',)



from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Lottery, LotteryParticipation
import random

@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ['title', 'max_participants', 'is_active', 'current_participant_count', 'created_at', 'participation_fee', 'number_of_winners','target_country', 'target_city',]
    list_filter = ['is_active', 'created_at', 'target_country', 'target_city']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'current_participant_count']

    def display_winner(self, obj):
        winner = obj.pick_winner()  # Appel de la méthode pour obtenir le gagnant
        return winner.username if winner else "Aucun gagnant"
    display_winner.short_description = "Gagnant"

    # Affichage du bouton dans le détail de la loterie
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pick-winner/<int:lottery_id>/', self.admin_site.admin_view(self.pick_random_winner), name='pick_random_winner')
        ]
        return custom_urls + urls

    def pick_random_winner(self, request, lottery_id):
        lottery = self.get_object(request, lottery_id)
        
        # Vérifie si la loterie est complète et si un gagnant n'a pas encore été tiré
        if lottery.is_full():
            participants = list(LotteryParticipation.objects.filter(lottery=lottery, is_active=True))
            if participants:
                # Choisir un gagnant au hasard
                winner_participant = random.choice(participants)
                winner_participant.is_winner = True
                winner_participant.winner_rank = 1
                winner_participant.save()
                self.message_user(request, f"Gagnant tiré pour {lottery.title}: {winner_participant.user.username}")
            else:
                self.message_user(request, f"Aucun participant pour {lottery.title}")
        else:
            self.message_user(request, f"La loterie {lottery.title} n'est pas encore complète.")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Ajouter un bouton dans le formulaire de détail
    def change_view(self, request, object_id, form_url='', extra_context=None):
        lottery = self.get_object(request, object_id)
        if lottery.is_full():
            extra_context = extra_context or {}
            extra_context['show_pick_winner_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if "_pick_winner" in request.POST:
            return HttpResponseRedirect(f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/pick-winner/{obj.id}/')
        return super().response_change(request, obj)
    
@admin.register(LotteryParticipation)
class LotteryParticipationAdmin(admin.ModelAdmin):
    list_display = ['user', 'lottery', 'full_name','id_transaction', 'phone_number', 'submitted_at', 'is_active','is_winner','winner_rank']
    list_filter = ['lottery', 'is_active']
    search_fields = ['user__username', 'full_name','id_transaction', 'phone_number']
    actions = ['activate_participations']

    def activate_participations(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} participations activées avec succès.")
    activate_participations.short_description = "Activer les participations sélectionnées"


from .models import PointConversion

@admin.register(PointConversion)
class PointConversionAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversion_rate', 'display_conversion')  # Afficher les informations pertinentes
    search_fields = ('conversion_rate',)  # Permet de chercher par taux de conversion
    list_filter = ('conversion_rate',)  # Permet de filtrer par taux de conversion
    ordering = ('-conversion_rate',)  # Trier par taux de conversion de manière décroissante

    def display_conversion(self, obj):
        """Affiche un message avec le taux de conversion en USD."""
        return f"1 point = {obj.conversion_rate} USD"
    
    display_conversion.short_description = 'Taux de Conversion'




from django.contrib import admin
from .models import ProductPoints,PhotoPoints

class PhotoPointsInline(admin.TabularInline):  # Permet d'afficher les images associées dans la page d'une publicité
    model = PhotoPoints
    extra = 1  # Nombre de champs vides supplémentaires pour l'ajout de nouvelles images
    fields = ('image',) 

class ProductPointsAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'description', 'created_at')  # Afficher le nom du produit, les points nécessaires, la description et la date de création
    search_fields = ('name',)  # Recherche par nom de produit
    list_filter = ('points_required', 'created_at')  # Filtrer par nombre de points et par date de création
    ordering = ('name',)  # Trier par nom du produit
    list_per_page = 10  # Afficher 10 produits récompenses par page
    inlines = [PhotoPointsInline]
admin.site.register(ProductPoints, ProductPointsAdmin)

class PhotoPointsAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'uploaded_at')  # Afficher le produit et l'image
    search_fields = ('product__name',)  # Recherche par nom de produit
    list_filter = ('uploaded_at',)  # Filtrer par date de téléchargement
    ordering = ('-uploaded_at',) 

# Enregistrer le modèle des images associées aux publicités
admin.site.register(PhotoPoints, PhotoPointsAdmin)

from django.contrib import admin
from .models import ContactProductPoints

class ContactProductPointsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'product_reward', 'created_at')  # Afficher les champs pertinents
    search_fields = ('first_name', 'last_name', 'email', 'product_reward__product__name')  # Recherche par prénom, nom, email ou nom du produit
    list_filter = ('product_reward',)  # Filtrer par produit récompense
    ordering = ('-created_at',)  # Trier par date de création (ordre décroissant)
    list_per_page = 10  # Afficher 10 demandes par page

admin.site.register(ContactProductPoints, ContactProductPointsAdmin)

from django.contrib import admin
from .models import  Purchase

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'points_used', 'purchase_date')
    list_filter = ('purchase_date', 'user')  # Vous pouvez filtrer par date et utilisateur
    search_fields = ('user__username', 'product__name')  # Recherche par utilisateur et produit
    ordering = ('-purchase_date',)  # Trier par date d'achat décroissante

admin.site.register(Purchase, PurchaseAdmin)




from django.contrib import admin
from .models import Advertisement, PhotoAds,Comment
from django.contrib import admin
from .models import Advertisement, PhotoAds

class PhotoAdsInline(admin.TabularInline):
    model = PhotoAds
    extra = 1
    readonly_fields = ['uploaded_at']
    verbose_name = "Image galerie"
    verbose_name_plural = "Galerie d'images"
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'media_type', 'is_active', 'created_at',
        'target_all_users', 'target_country', 'target_city',
        'likes_count', 'shares_count', 'visits_count', 'store'
    )
    list_filter = ('media_type', 'is_active', 'target_country', 'target_city', 'created_at')
    search_fields = ('title', 'description', 'user__email', 'user__username')
    readonly_fields = ('slug', 'likes_count', 'shares_count', 'visits_count', 'comments_count')
    ordering = ('-created_at',)
    inlines = [PhotoAdsInline]

    fieldsets = (
        (None, {
            'fields': (
                'title', 'user', 'description', 'media_type', 'media_file', 'thumbnail_url', 'url'
            )
        }),
        ('Ciblage', {
            'fields': (
                'target_all_users', 'target_country', 'target_city', 'store'
            )
        }),
        ('Options', {
            'fields': (
                'max_likes', 'max_shares', 'max_comments', 'max_interactions', 'is_active'  # ✅ Ajouté max_comments
            )
        }),
        ('Infos système', {
            'fields': (
                'slug', 'likes_count', 'shares_count', 'visits_count', 'comments_count'
            )
        }),
    )


@admin.register(PhotoAds)
class PhotoAdsAdmin(admin.ModelAdmin):
    list_display = ('ads', 'image', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('ads__title',)



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'content', 'created_at')
    search_fields = ('user__username', 'ad__title', 'content')
    list_filter = ('created_at',)
    readonly_fields = ['user', 'ad', 'content', 'created_at']



from django.contrib import admin
from .models import AdInteraction

class AdInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'interaction_type', 'timestamp')
    search_fields = ('user__username', 'ad__title')
    list_filter = ('interaction_type', 'timestamp')
    ordering = ('-timestamp',)

admin.site.register(AdInteraction, AdInteractionAdmin)

from django.contrib import admin
from .models import Share

@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'shared_at')  # Colonnes visibles dans la liste
    list_filter = ('shared_at', 'user')  # Filtres sur la barre latérale
    search_fields = ('user__username', 'ad__title')  # Champ de recherche
    ordering = ('-shared_at',)  # Trie par date de partage décroissante


from django.contrib import admin
from core.models import PopUpAdvertisement
from core.forms import PopUpAdvertisementForm  # seulement si tu utilises le form custom

@admin.register(PopUpAdvertisement)
class PopUpAdvertisementAdmin(admin.ModelAdmin):
    form = PopUpAdvertisementForm  # optionnel
    list_display = ('__str__', 'is_active', 'media_type', 'store', 'target_country', 'target_city', 'created_at')
    list_filter = ('is_active', 'media_type', 'target_country', 'target_city')
    search_fields = ('store__name',)


from django.contrib import admin
from core.models import FeaturedStore
from core.forms import FeaturedStoreForm  # Assure-toi que le chemin est correct

@admin.register(FeaturedStore)
class FeaturedStoreAdmin(admin.ModelAdmin):
    form = FeaturedStoreForm
    list_display = ('store', 'show_in_all', 'country', 'city', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('show_in_all', 'country', 'city')
    search_fields = ('store__name',)
    ordering = ('-created_at',)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Actif ?'



from .models import CommandeLivraison,AdvertisementPayment

class CommandeLivraisonAdmin(admin.ModelAdmin):
    # Afficher les champs dans la liste de l'admin
    list_display = ('nom', 'prenom', 'email', 'numero_tel', 'numero_id_colis', 'statut', 'date_commande', 'user')
    
    # Ajouter des filtres par statut, utilisateur et date
    list_filter = ('statut', 'user', 'date_commande')
    
    # Recherche par nom, email, numéro ID colis
    search_fields = ('nom', 'prenom', 'email', 'numero_id_colis')
    
    # Permettre de modifier les champs directement depuis la liste des objets
    list_editable = ('statut',)
    
    # Afficher les détails dans la vue d'édition
    fieldsets = (
        (None, {
            'fields': ('nom', 'prenom', 'email', 'numero_tel', 'user')
        }),
        ('Détails de la livraison', {
            'fields': ('adresse_livraison', 'description_colis', 'endroit_recuperation', 'numero_id_colis')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_commande')
        }),
    )
    
    # Empêcher la modification de la date de commande
    readonly_fields = ('date_commande',)
    
    # Tris par défaut sur la date de commande (tri par date décroissante)
    ordering = ('-date_commande',)
    
    # Ajouter un bouton pour changer de statut rapidement
    actions = ['marquer_comme_livree']

    def marquer_comme_livree(self, request, queryset):
        """Action pour marquer la commande comme livrée."""
        queryset.update(statut='livree')
    marquer_comme_livree.short_description = "Marquer comme livrée"

# Enregistrer le modèle et son admin
admin.site.register( CommandeLivraison, CommandeLivraisonAdmin)


@admin.register(AdvertisementPayment)
class AdvertisementPaymentAdmin(admin.ModelAdmin):
    list_display = ('advertisement', 'transaction_id', 'phone_number', 'user', 'created_at', 'is_validated')
    search_fields = ('transaction_id', 'user__email', 'advertisement__title')
    list_filter = ('is_validated', 'created_at')



from django.contrib import admin
from .models import Share,PopUpAdvertisement


class ShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'shared_at')  # Colonnes visibles dans la liste
    list_filter = ('shared_at', 'user')  # Filtres sur la barre latérale
    search_fields = ('user__username', 'ad__title')  # Champ de recherche
    ordering = ('-shared_at',)  # Trie par date de partage décroissante



from django.contrib import admin
from .models import PointsTransfer

@admin.register(PointsTransfer)
class PointsTransferAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'points', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username')

from django.contrib import admin
from .models import PointTransferHistory

@admin.register(PointTransferHistory)
class PointTransferHistoryAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'points_transferred', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username')
    ordering = ('-timestamp',)

# core/admin.py
from django.contrib import admin
from .models import PointSharingGroup

@admin.register(PointSharingGroup)
class PointSharingGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'created_at', 'member_count']
    filter_horizontal = ['members']
    search_fields = ['name', 'creator__username']
