from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify # type: ignore
from decimal import Decimal
# Create your models here.

from django_countries.fields import CountryField
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    flag = models.ImageField(upload_to='flags/')

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cities/')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.name} ({self.country.name})"
from django.contrib.auth.models import AbstractUser
from django.db import models
from .models import Country, City  # à adapter selon ton organisation

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to="p_img", blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)

    # Ciblage :
    commune = models.CharField(max_length=50, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    interests = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    # Image compression & affichage inchangé...

class Typestore(models.Model):
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to="typestore_img/", blank=True, null=True)

    def __str__(self):
        return self.nom

class TypeBusiness(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


import os
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Typestore, Country, City

class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stores"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True, unique=True)
    description = models.TextField()
    adresse = models.TextField()

    thumbnail = models.ImageField(
        upload_to="img",
        null=True,
        blank=True,
        verbose_name="Image du Store"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    typestore = models.ForeignKey(
        Typestore,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    typebusiness = models.ForeignKey(
        'TypeBusiness',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stores'
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stores"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stores"
    )

    apply_commission = models.BooleanField(default=True)
    favoritestore = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    from django.utils.text import slugify

    def save(self, *args, **kwargs):
       if not self.slug:
        base_slug = slugify(self.name)
        slug = base_slug
        count = 1
        while Store.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{count}"
            count += 1
        self.slug = slug
       super(Store, self).save(*args, **kwargs)


    @property
    def subscriber_count(self):
        return self.subscribers.count() if hasattr(self, 'subscribers') else 0

    @property
    def average_rating(self):
        from django.db.models import Avg
        average = self.testimonials.aggregate(avg=Avg('rating'))['avg'] or 0
        return round(average / 2, 1)  # Note sur 5 étoiles

    def __str__(self):
        return self.name



class StoreSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store')  # Un utilisateur ne peut s’abonner qu’une seule fois

    def __str__(self):
        return f"{self.user.email} -> {self.store.name}"
from django.db import models
from .models import Store, Country, City  # Assure-toi que les imports sont corrects

class FeaturedStore(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='featured_entries')
    
    show_in_all = models.BooleanField(default=False, help_text="Afficher pour tous les pays et villes")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        from datetime import date
        today = date.today()
        return (self.start_date is None or self.start_date <= today) and \
               (self.end_date is None or self.end_date >= today)

    def __str__(self):
        location = "Global" if self.show_in_all else (
            self.city.name if self.city else self.country.name if self.country else "Indéfini"
        )
        return f"🏬 {self.store.name} en vedette ({location})"
    
class Testimonial(models.Model):
    RATING_CHOICES = [(i, f'{i}/10') for i in range(1, 11)]  # Créer des choix de 1 à 10

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="testimonials")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()  # Le texte du témoignage
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)  # Choix entre 1 et 10
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Testimonial for {self.store.name} by {self.user.username}'
    
    class Meta:
        ordering = ['-created_at']



from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError

class SpotPubStore(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name="spot_pub")
    video = models.FileField(upload_to='spot_pubs/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        max_size = 10 * 1024 * 1024  # 10 Mo

        if self.video and self.video.size > max_size:
            raise ValidationError("La vidéo dépasse la taille maximale autorisée (10 Mo).")

    def save(self, *args, **kwargs):
        self.clean()  # déclenche la validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Spot Pub pour {self.store.name}"


# models.py
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()
class StoreVisit(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='daily_visits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('store', 'user', 'ip_address', 'date')

    def __str__(self):
        return f"{self.store.name} - {self.date} - {self.user or self.ip_address}"


from django.db import models

class DeviseCountry(models.Model):
    country = models.OneToOneField("Country", on_delete=models.CASCADE, related_name="devise_info")
    devise = models.CharField(max_length=10)  # Exemple: 'USD', 'CDF', 'EUR'

    def __str__(self):
        return f"{self.country.name} - {self.devise}"

from django.urls import reverse

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  # Titre de la notification
    description = models.TextField()  # Description de la notification
    image = models.ImageField(upload_to='notifications/', null=True, blank=True)  # Image de la notification (optionnelle)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification pour {self.user.email} - {self.store.name}"

    def get_absolute_url(self):
        return reverse('store_detail', kwargs={'slug': self.store.slug})

# models.py
class UserNotificationHide(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification = models.ForeignKey('Notification', on_delete=models.CASCADE)
    hidden_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')

    def __str__(self):
        return f"{self.user.email} a masqué {self.notification.title}"

class ContactStore(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="contact_requests")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.product.name}"



class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)
   
    def __str__(self):
        return self.name
    
from django.db import models
from decimal import Decimal
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

class TypeProduct(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

from decimal import Decimal
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
import os
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Product(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
    type_product = models.ForeignKey('TypeProduct', on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_with_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    video = models.FileField(upload_to='products/videos/', null=True, blank=True)
    image_galerie = models.ImageField(upload_to='product/galerie/', null=True, blank=True, verbose_name="Image galerie")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        from django.db.models import Avg
        average = self.testimonials.aggregate(avg=Avg('rating'))['avg'] or 0
        return round(average / 2, 1)

    def get_total_price(self, quantity):
        return self.price * quantity

    def image_size_ko(self):
        if self.image and hasattr(self.image, 'size'):
            return f"{self.image.size / 1024:.1f} Ko"
        return "Aucune image"

    def image_galerie_size_ko(self):
        if self.image_galerie and hasattr(self.image_galerie, 'size'):
            return f"{self.image_galerie.size / 1024:.1f} Ko"
        return "Aucune image"

    def compress_image(self, image_field, quality=70):
        if image_field:
            img = Image.open(image_field)
            img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality)
            new_image_file = ContentFile(buffer.getvalue())
            filename = os.path.basename(image_field.name)
            return new_image_file, filename
        return None, None

    @property
    def total_achats(self):
        return self.order_items.count()

    @property
    def total_purchased(self):
        from core.models import OrderItem
        return OrderItem.objects.filter(product=self).aggregate(total=Sum('quantity'))['total'] or 0

    def acheteurs_uniques(self):
        return CustomUser.objects.filter(orders__items__product=self).distinct()

    @property
    def total_buyers(self):
        from core.models import OrderItem
        return OrderItem.objects.filter(product=self).values('order__user').distinct().count()

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.store.apply_commission and self.price is not None:
            commission_rate = Decimal('0.30')
            self.price_with_commission = self.price + (self.price * commission_rate)
        else:
            self.price_with_commission = self.price

        if self.image and not hasattr(self.image, '_compressed'):
            compressed_file, name = self.compress_image(self.image)
            if compressed_file:
                self.image.save(name, compressed_file, save=False)
                self.image._compressed = True

        if self.image_galerie and not hasattr(self.image_galerie, '_compressed'):
            compressed_file, name = self.compress_image(self.image_galerie)
            if compressed_file:
                self.image_galerie.save(name, compressed_file, save=False)
                self.image_galerie._compressed = True

        super().save(*args, **kwargs)


# class Product(models.Model):
#     store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name="products")
#     category = models.ForeignKey('Category', on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
#     type_product = models.ForeignKey(TypeProduct, on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     price_with_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     stock = models.PositiveIntegerField()
#     image = models.ImageField(upload_to='products/', null=True, blank=True)
#     image_galerie = models.ImageField(upload_to='product/galerie/', null=True, blank=True, verbose_name="Image galerie")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
    
#     @property
#     def average_rating(self):
#         from django.db.models import Avg
#         average = self.testimonials.aggregate(avg=Avg('rating'))['avg'] or 0
#         return round(average / 2, 1)

#     def get_total_price(self, quantity):
#         return self.price * quantity

#     def image_size_ko(self):
#         if self.image and hasattr(self.image, 'size'):
#             return f"{self.image.size / 1024:.1f} Ko"
#         return "Aucune image"

#     def image_galerie_size_ko(self):
#         if self.image_galerie and hasattr(self.image_galerie, 'size'):
#             return f"{self.image_galerie.size / 1024:.1f} Ko"
#         return "Aucune image"

#     def compress_image(self, image_field, quality=70):
#         if image_field:
#             img = Image.open(image_field)
#             img = img.convert('RGB')
#             buffer = BytesIO()
#             img.save(buffer, format='JPEG', quality=quality)
#             new_image_file = ContentFile(buffer.getvalue())
#             filename = os.path.basename(image_field.name)
#             return new_image_file, filename
#         return None, None

#     def save(self, *args, **kwargs):
#         if self.store.apply_commission and self.price is not None:
#             commission_rate = Decimal('0.30')
#             self.price_with_commission = self.price + (self.price * commission_rate)
#         else:
#             self.price_with_commission = self.price

#         if self.image and not hasattr(self.image, '_compressed'):
#             compressed_file, name = self.compress_image(self.image)
#             if compressed_file:
#                 self.image.save(name, compressed_file, save=False)
#                 self.image._compressed = True

#         if self.image_galerie and not hasattr(self.image_galerie, '_compressed'):
#             compressed_file, name = self.compress_image(self.image_galerie)
#             if compressed_file:
#                 self.image_galerie.save(name, compressed_file, save=False)
#                 self.image_galerie._compressed = True

#         super().save(*args, **kwargs)



class AssignerCategory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="category_assignment")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="assigned_products")

    def __str__(self):
        return f"{self.product.name} -> {self.category.name}"

from django.db import models

class ContactProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="contact_requests")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.product.name}"



class Testimonialproduct(models.Model):
    RATING_CHOICES = [(i, f'{i}/10') for i in range(1, 11)]  # Créer des choix de 1 à 10

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="testimonials")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()  # Le texte du témoignage
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)  # Choix entre 1 et 10
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
      return f'Testimonial for {self.product.name} by {self.user.username}'

    
    class Meta:
        ordering = ['-created_at']

class Photo(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product/gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.product} - {self.image.name}"




class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Panier de {self.user.email} pour {self.country.name}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())





class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Définir un valeur par défaut de 1

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.product.price_with_commission}"

    def get_total_price(self):
        return self.product.price_with_commission * self.quantity



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)  # 👈 NOUVEAU
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'En attente'), ('paid', 'Payée'), ('shipped', 'Expédiée'), ('served', 'Servie')],
        default='pending'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    activated = models.BooleanField(default=True)

    def __str__(self):
        return f"Commande {self.id} - {self.user.username} - {self.status}"

    def calculate_total(self):
        self.total_amount = sum(item.get_total_price() for item in self.items.all())
        self.save()

    def update_user_points(self):
        if not hasattr(self.user, 'userpoints'):
            self.user.userpoints = UserPoints.objects.create(user=self.user)
        user_points = self.user.userpoints
        user_points.total_purchases += 1
        if user_points.total_purchases % 5 == 0:
            user_points.points += 1
        user_points.save()

    def save(self, *args, **kwargs):
        if self.activated:
            self.update_user_points()
        super().save(*args, **kwargs)

    @property
    def devise(self):
        try:
            return self.country.devise_info.devise
        except:
            return "CDF"  
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.price_at_time_of_order}"

    def get_total_price(self):
        """Retourner le prix total pour cet item"""
        return self.price_at_time_of_order * self.quantity

    def get_store(self):
        """Retourner le store auquel appartient ce produit"""
        return self.product.store  # Accéder au store via le produit lié



class UserPoints(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)  # Points actuels utilisables
    total_purchases = models.PositiveIntegerField(default=0)  # Nombre total d'achats effectués
    ad_points = models.PositiveIntegerField(default=0)  # Points gagnés via les publicités
    spent_points = models.PositiveIntegerField(default=0)  # ✅ Suivi des points dépensés

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

    def get_earned_points(self):
        """Calcule le total des points gagnés (likes, commentaires, partages, achats)."""
        likes = AdInteraction.objects.filter(user=self.user, interaction_type='like').count()
        comments = AdInteraction.objects.filter(user=self.user, interaction_type='comment').count()
        shares = AdInteraction.objects.filter(user=self.user, interaction_type='share').count()

        earned_points = likes + (comments * 2) + (shares * 5)  # Points gagnés via interactions
        earned_points += self.total_purchases // 5  # Ajout des points de fidélité (1 point tous les 5 achats)
        
        return earned_points

    def spend_points(self, amount):
        """Déduit des points lors d'un achat et enregistre la dépense."""
        if self.points >= amount:
           self.points -= amount
           self.spent_points += amount  # ✅ Mise à jour correcte
           self.save()
        
        # 🔥 Debugging pour voir les valeurs après sauvegarde
        obj = UserPoints.objects.get(user=self.user)  # Recharge depuis la BD
        print(f"✅ Points actuels : {obj.points} | Spent points : {obj.spent_points}")

        return True
        print("❌ Pas assez de points !")  # 🔥 Debugging
        return False



    def add_ad_points(self, points):
        """Ajoute des points en fonction des interactions publicitaires."""
        self.ad_points += points
        self.points += points  # Ajouter aux points globaux
        self.save()

from decimal import Decimal, ROUND_HALF_UP
class PointConversion(models.Model):
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=5, default=Decimal('0.00125'))  # 1 point = 0.00143 USD

    def __str__(self):
        return f"1 point = {self.conversion_rate} USD"

    def convert_points_to_usd(self, points):
        """Convertit les points en dollars avec un arrondi à 2 décimales."""
        result = Decimal(points) * self.conversion_rate
        return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Q
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
class Advertisement(models.Model):
    MEDIA_CHOICES = [
        ('image', 'Image'),
        ('video', 'Vidéo'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='advertisements'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    media_file = models.FileField(upload_to='ads/')
    thumbnail_url = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    visits_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    target_all_users = models.BooleanField(default=True)
    target_country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='ads_targeted')
    target_city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='ads_targeted')
    store = models.ForeignKey('Store', on_delete=models.SET_NULL, null=True, blank=True, related_name='ads')

    max_likes = models.PositiveIntegerField(blank=True, null=True)
    max_shares = models.PositiveIntegerField(blank=True, null=True)
    max_comments = models.PositiveIntegerField(blank=True, null=True)
    max_interactions = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Valeur identique appliquée à chaque type : likes, shares, comments"
    )
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
      return reverse('advertisement_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_max_value(self, field_name):
        # Si max_interactions est défini, il domine sur les 3 champs
        if self.max_interactions is not None:
            return self.max_interactions
        return getattr(self, field_name)

    def check_deactivation_by_likes(self):
        max_val = self.get_max_value('max_likes')
        if max_val and self.likes_count >= max_val:
            self.check_deactivation_by_all_max_reached()

    def check_deactivation_by_shares(self):
        max_val = self.get_max_value('max_shares')
        if max_val and self.shares_count >= max_val:
            self.check_deactivation_by_all_max_reached()

    def check_deactivation_by_comments(self):
        max_val = self.get_max_value('max_comments')
        if max_val and self.comments_count >= max_val:
            self.check_deactivation_by_all_max_reached()

    def check_deactivation_by_all_max_reached(self):
        max_val = self.max_interactions

        if max_val is not None:
            if (
                self.likes_count >= max_val and
                self.shares_count >= max_val and
                self.comments_count >= max_val
            ):
                self.is_active = False
                self.save(update_fields=["is_active"])
        else:
            if (
                self.max_likes is not None and self.likes_count >= self.max_likes and
                self.max_shares is not None and self.shares_count >= self.max_shares and
                self.max_comments is not None and self.comments_count >= self.max_comments
            ):
                self.is_active = False
                self.save(update_fields=["is_active"])

    def __str__(self):
        return self.title




class PhotoAds(models.Model):
    ads = models.ForeignKey(Advertisement, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ads/galerie/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.ads} - {self.image.name}"


class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} a partagé {self.ad.title}"



class AdInteraction(models.Model):
    INTERACTION_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('share', 'Share'),
        ('visit', 'Visit'),
        ('bonus_1_point', 'Bonus 1 Point'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=16, choices=INTERACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad', 'interaction_type')

    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.ad.title}"

    def toggle_like(self):
        # 🔁 Permet de liker une pub si pas encore likée
        if self.interaction_type == 'like':
            self.delete()
            if self.ad.likes_count > 0:
                self.ad.likes_count -= 1
        else:
            self.interaction_type = 'like'
            self.save()
            self.ad.likes_count += 1

            # Ajout de points
            user_points, _ = UserPoints.objects.get_or_create(user=self.user)
            user_points.points += 1
            user_points.ad_points += 1
            user_points.save()

        self.ad.save()
        self.ad.check_deactivation_by_likes()
        self.ad.check_deactivation_by_all_max_reached()  # 👈 logique finale stricte

    def add_comment(self, content):
        if not Comment.objects.filter(user=self.user, ad=self.ad).exists():
            Comment.objects.create(user=self.user, ad=self.ad, content=content)
            self.ad.comments_count += 1
            self.ad.save()

            user_points, _ = UserPoints.objects.get_or_create(user=self.user)
            user_points.points += 2
            user_points.ad_points += 2
            user_points.save()

            self.ad.check_deactivation_by_comments()
            self.ad.check_deactivation_by_all_max_reached()

    def share_ad(self):
        share_exists = AdInteraction.objects.filter(
            user=self.user, ad=self.ad, interaction_type='share'
        ).exists()

        if not share_exists:
            AdInteraction.objects.create(
                user=self.user,
                ad=self.ad,
                interaction_type='share'
            )
            self.ad.shares_count += 1
            self.ad.save()

            user_points, _ = UserPoints.objects.get_or_create(user=self.user)
            user_points.points += 3
            user_points.ad_points += 3
            user_points.save()

            self.ad.check_deactivation_by_shares()
            self.ad.check_deactivation_by_all_max_reached()

    def get_comments(self):
        return Comment.objects.filter(ad=self.ad)


# class AdInteraction(models.Model):
#     INTERACTION_CHOICES = [
#         ('like', 'Like'),
#         ('comment', 'Comment'),
#         ('share', 'Share'),
#         ('visit', 'Visit'),
#         ('bonus_1_point', 'Bonus 1 Point'),
#     ]

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="interactions")
#     interaction_type = models.CharField(max_length=16, choices=INTERACTION_CHOICES)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'ad', 'interaction_type')

#     def __str__(self):
#         return f"{self.user.username} {self.interaction_type} {self.ad.title}"

#     def toggle_like(self):
#         if self.interaction_type == 'like':
#             self.delete()
#             if self.ad.likes_count > 0:
#                 self.ad.likes_count -= 1
#         else:
#             self.interaction_type = 'like'
#             self.save()
#             self.ad.likes_count += 1

#         self.ad.save()
#         self.ad.check_deactivation_by_total_interactions()

#     def add_comment(self, content):
#         if not Comment.objects.filter(user=self.user, ad=self.ad).exists():
#             Comment.objects.create(user=self.user, ad=self.ad, content=content)
#             self.ad.comments_count += 1
#             self.user.userpoints.points += 2
#             self.ad.save()
#             self.user.userpoints.save()
#             self.ad.check_deactivation_by_total_interactions()

#     def share_ad(self):
#         share_count = AdInteraction.objects.filter(user=self.user, ad=self.ad, interaction_type='share').count()

#         if share_count < 1:
#             self.interaction_type = 'share'
#             self.save()
#             self.ad.shares_count += 1
#             self.user.userpoints.points += 3
#             self.ad.save()
#             self.user.userpoints.save()
#             self.ad.check_deactivation_by_total_interactions()

#     def get_comments(self):
#         return Comment.objects.filter(ad=self.ad)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')

    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.ad.title}"

# class Advertisement(models.Model):
#     MEDIA_CHOICES = [
#         ('image', 'Image'),
#         ('video', 'Video'),
#     ]
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='advertisements'
#     )
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
#     media_file = models.FileField(upload_to='ads/')  # Image ou vidéo
#     url = models.URLField(blank=True, null=True)  # Lien externe (ex: site de l’annonceur)
#     thumbnail_url = models.ImageField(upload_to='thumbnails/', null=True, blank=True)  # Miniature de la vidéo
#     slug = models.SlugField(unique=True, blank=True)  
#     likes_count = models.PositiveIntegerField(default=0)
#     comments_count = models.PositiveIntegerField(default=0)
#     shares_count = models.IntegerField(default=0)
#     visits_count = models.PositiveIntegerField(default=0) 
#     created_at = models.DateTimeField(auto_now_add=True)
#     # Autres champs...
#     # Nouveaux champs pour le ciblage
    
#     target_all_users = models.BooleanField(default=True)

#     # 🔽 Tu ajoutes ici :
#     target_country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='ads_targeted')
#     target_city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='ads_targeted')
#     # models.py
#     store = models.ForeignKey(
#         Store,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='ads'
#     )
    
#     max_likes = models.PositiveIntegerField(blank=True, null=True, help_text="Nombre maximum de likes autorisé avant désactivation.")
#     is_active = models.BooleanField(default=True, help_text="Si désactivé, la pub ne sera plus affichée.")
#     max_shares = models.PositiveIntegerField(blank=True, null=True)
#     def get_absolute_url(self):
#       return reverse('advertisement_detail', kwargs={'slug': self.slug})

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         super().save(*args, **kwargs)
    
#     def check_deactivation_by_likes(self):
#         if self.max_likes and self.likes_count >= self.max_likes:
#             self.is_active = False
#             self.save(update_fields=["is_active"])
#     def check_deactivation_by_shares(self):
#         if self.max_shares and self.shares_count >= self.max_shares:
#            self.is_active = False
#            self.save(update_fields=["is_active"])
#     def __str__(self):
#         return self.title

# class PhotoAds(models.Model):
#     ads = models.ForeignKey(Advertisement, related_name='photos', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='ads/galerie/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Photo for {self.ads} - {self.image.name}"

# class Share(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Utilisation de AUTH_USER_MODEL
#     ad = models.ForeignKey('core.Advertisement', on_delete=models.CASCADE)  # Remplace 'Advertisement' si besoin
#     shared_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} a partagé {self.ad.title}"



# class AdInteraction(models.Model):
#     INTERACTION_CHOICES = [
#         ('like', 'Like'),
#         ('comment', 'Comment'),
#         ('share', 'Share'),
#         ('visit', 'Visit'),
#         ('bonus_1_point', 'Bonus 1 Point'),
#     ]

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="interactions")
#     interaction_type = models.CharField(max_length=16, choices=INTERACTION_CHOICES)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'ad', 'interaction_type')  # Empêche les doublons

#     def __str__(self):
#         return f"{self.user.username} {self.interaction_type} {self.ad.title}"

#     def toggle_like(self):
#         if self.interaction_type == 'like':
#          self.delete()  # Si c'est un "like", on supprime l'interaction pour "dislike"
#         if self.ad.likes_count > 0:
#             self.ad.likes_count -= 1  # Empêche de réduire à une valeur négative
#         else:
#          self.interaction_type = 'like'
#          self.save()
#          self.ad.likes_count += 1
#         self.ad.save()

    

#     def add_comment(self, content):
#         """ Ajouter un commentaire à la publicité et gérer les points """
#         if not Comment.objects.filter(user=self.user, ad=self.ad).exists():
#             Comment.objects.create(user=self.user, ad=self.ad, content=content)
#             self.ad.comments_count += 1
#             self.user.userpoints.points += 2  # Ajouter 2 points pour un commentaire
#             self.ad.save()
#             self.user.userpoints.save()

   
#     def share_ad(self):
#         """ Ajouter un partage et gérer les points """
#         # Vérifier combien de fois l'utilisateur a partagé cette annonce
#         share_count = AdInteraction.objects.filter(user=self.user, ad=self.ad, interaction_type='share').count()

#         if share_count < 1:  # L'utilisateur n'a pas encore partagé cette annonce
#             self.interaction_type = 'share'
#             self.save()
#             self.ad.shares_count += 1
#             self.user.userpoints.points += 3  # Ajouter 5 points pour chaque partage
#             self.ad.save()
#             self.user.userpoints.save()
#         else:
#             # Si l'utilisateur a déjà partagé cette publicité, il ne peut pas gagner de points pour un deuxième partage
#             print("L'utilisateur a déjà partagé cette publicité.")

   


#     def get_comments(self):
#         from .models import Comment  # Importation locale pour éviter la circularité
#         return Comment.objects.filter(ad=self)


# class Comment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # L'utilisateur qui commente
#     ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="comments")  # La publicité à laquelle appartient le commentaire
#     content = models.TextField()  # Le contenu du commentaire
#     created_at = models.DateTimeField(auto_now_add=True)  # La date de création du commentaire

#     class Meta:
#         unique_together = ('user', 'ad')  # Un utilisateur ne peut commenter qu'une fois une même publicité

#     def __str__(self):
#         return f"Commentaire de {self.user.username} sur {self.ad.title}"




class CommandeLivraison(models.Model):
    # Informations du client
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    numero_tel = models.CharField(max_length=15)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Détails de la livraison
    adresse_livraison = models.TextField()
    description_colis = models.TextField()
    endroit_recuperation = models.CharField(max_length=255)
    numero_id_colis = models.CharField(max_length=100)

    # Statut de la commande
    statut = models.CharField(
        max_length=20,
        choices=[('en_attente', 'En attente'), ('en_cours', 'En cours'), ('livree', 'Livrée')],
        default='en_attente'
    )
    
    # Dates
    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.numero_id_colis} par {self.nom} {self.prenom}"

    class Meta:
        permissions = [
            ("peut_marquer_comme_livree", "Peut marquer les commandes comme livrées"),
        ]

class Classe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
from django.db import models

from django.db import models
from core.models import Store, Country, City  # ajuste selon ton app
class PopUpAdvertisement(models.Model):
    IMAGE = 'image'
    VIDEO = 'video'
    MEDIA_TYPE_CHOICES = [
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='ads/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    url = models.URLField(blank=True, null=True)

    # ✅ Ajoute des related_name uniques pour éviter le conflit avec Advertisement
    store = models.ForeignKey(
        'Store',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='popup_ads'
    )
    target_country = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='popup_ads_targeted'
    )
    target_city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='popup_ads_targeted'
    )

    def __str__(self):
        return f"PopUp Pub {'Active' if self.is_active else 'Inactive'} - {self.media_type}"



from django.utils import timezone

# models.py
 # adapte selon ton app

class MobileMoneyPayment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_number = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    delivery_option = models.CharField(max_length=100, choices=[('home', 'A domicile'), ('pickup', 'Récupérer soi-même')])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)  # 🔥 ajouté

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.transaction_id}"


from django.db import models

class NumeroPaye(models.Model):
    country = models.OneToOneField("Country", on_delete=models.CASCADE, related_name="numero_paye")
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to='numeropaye/')
    numero_paye = models.CharField(max_length=30)  # Ex: numéro Airtel, M-Pesa, Orange...

    def __str__(self):
        return f"{self.nom} ({self.country.name})"


class StoreCoManager(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='co_managers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_stores')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'user')

    def __str__(self):
        return f"{self.user.email} gère {self.store.name}"



import random
from django.conf import settings
from django.db import models
from django.db import models

class Lottery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='lottery_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_participants = models.PositiveIntegerField(help_text="Nombre maximum de participants")
    is_active = models.BooleanField(default=True)
    number_of_winners = models.PositiveIntegerField(default=1)
    draw_done = models.BooleanField(default=False)
    participation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Frais de participation en monnaie locale"
    )

    # ✅ Ciblage intelligent
    target_country = models.ForeignKey(
        'Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_lotteries'
    )
    target_city = models.ForeignKey(
        'City', on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_lotteries'
    )

    def __str__(self):
        return self.title

    def current_participant_count(self):
        from .models import LotteryParticipation
        return LotteryParticipation.objects.filter(lottery=self, is_active=True).count()

    def is_full(self):
        return self.current_participant_count() >= self.max_participants

    def pick_winner(self):
        from .models import LotteryParticipation
        if self.is_full():
            participants = list(LotteryParticipation.objects.filter(lottery=self, is_active=True))
            if participants:
                chosen = random.choice(participants)
                chosen.is_winner = True
                chosen.winner_rank = 1
                chosen.save()
                return chosen.user
        return None



class LotteryParticipation(models.Model):
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name="participations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    id_transaction = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    is_winner = models.BooleanField(default=False)
    winner_rank = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  # Doit être activé manuellement

     

    def __str__(self):
        return f"{self.user} - {self.lottery}"



class ProductPoints(models.Model):
    name = models.CharField(max_length=255)
    points_required = models.PositiveIntegerField()  # Nombre de points nécessaires pour l'acheter
    description = models.TextField()  # Description du produit
    image = models.ImageField(upload_to='product_rewards/', blank=True, null=True)  # Image pour le produit
    created_at = models.DateTimeField(auto_now_add=True)  # Champ de date de création

    def __str__(self):
        return f"{self.name} - {self.points_required} points"


class PhotoPoints(models.Model):
    product = models.ForeignKey(ProductPoints, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photopoints/galerie/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.product} - {self.image.name}"

from django.db import models

class ContactProductPoints(models.Model):
    product_reward = models.ForeignKey('ProductPoints', on_delete=models.CASCADE, related_name="contact_requests")  # Lien vers le produit récompense
    first_name = models.CharField(max_length=255)  # Prénom de la personne
    last_name = models.CharField(max_length=255)  # Nom de la personne
    email = models.EmailField()  # Email de la personne
    phone_number = models.CharField(max_length=20)  # Numéro de téléphone
    description = models.TextField(blank=True, null=True)  # Message ou description (optionnel)
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création de la demande

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.product_reward.product.name}"



from decimal import Decimal, ROUND_HALF_UP

class PointConversion(models.Model):
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=5, default=Decimal('0.00125'))  # 1 point = 0.00143 USD

    def __str__(self):
        return f"1 point = {self.conversion_rate} USD"

    def convert_points_to_usd(self, points):
        """Convertit les points en dollars sans arrondi."""
        return Decimal(points) * self.conversion_rate





class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Utilisateur qui a acheté
    product = models.ForeignKey(ProductPoints, on_delete=models.CASCADE)  # Produit acheté
    points_used = models.PositiveIntegerField()  # Nombre de points utilisés pour l'achat
    purchase_date = models.DateTimeField(auto_now_add=True)  # Date de l'achat

    def __str__(self):
        return f"Achat de {self.product.name} par {self.user.username} le {self.purchase_date}"



class AdvertisementPayment(models.Model):
    advertisement = models.OneToOneField("Advertisement", on_delete=models.CASCADE, related_name="payment")
    transaction_id = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)  # à cocher par l’admin

    def __str__(self):
        return f"Paiement pub #{self.advertisement.id} - {self.transaction_id}"


class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Utilisation de AUTH_USER_MODEL
    ad = models.ForeignKey('core.Advertisement', on_delete=models.CASCADE)  # Remplace 'Advertisement' si besoin
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} a partagé {self.ad.title}"
    


class PointsTransfer(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_transfers', on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='received_transfers', on_delete=models.CASCADE
    )
    points = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.points} points)"


class PointTransferHistory(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_history_sent_transfers'  # nom unique
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_history_received_transfers'  # nom unique
    )
    points_transferred = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.points_transferred} points)"

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class PointSharingGroup(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_point_groups')
    members = models.ManyToManyField(User, related_name='point_sharing_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def member_count(self):
        return self.members.count()

    def __str__(self):
        return f"Groupe {self.name} (Membres: {self.member_count()})"
