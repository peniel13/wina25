from rest_framework import serializers
from .models import CustomUser

from rest_framework import serializers
from .models import CustomUser


from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password',
            'first_name', 'last_name', 'phone',
            'address', 'commune', 'profile_pic',
            'city', 'country', 'interests'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},  # ✅ rendre email obligatoire
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'address': {'required': False},
            'commune': {'required': False},
            'profile_pic': {'required': False},
            'city': {'required': False},
            'country': {'required': False},
            'interests': {'required': False},
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance





from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = CustomUserSerializer(self.user).data
        data['user'] = user_data
        return data


from rest_framework import serializers
from .models import Typestore, TypeBusiness, Country, City

class TypestoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Typestore
        fields = ['id', 'nom','image']

class TypeBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBusiness
        fields = ['id', 'nom']


class CountrySerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'currency', 'flag']  # ajoute "currency"

    def get_currency(self, obj):
        try:
            return obj.devise_info.devise  # via ton modèle DeviseCountry
        except AttributeError:
            return ''

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name','image']

from rest_framework import serializers
from .models import Store
from .serializers import TypestoreSerializer, TypeBusinessSerializer, CountrySerializer, CitySerializer

from rest_framework import serializers
from .models import Store, StoreSubscription
from django.db.models import Avg
from rest_framework import serializers
from core.models import Store, Testimonial, StoreSubscription
from core.serializers import (
    CountrySerializer, CitySerializer, TypestoreSerializer, TypeBusinessSerializer
)

class StoreSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    typestore = TypestoreSerializer(read_only=True)
    typebusiness = TypeBusinessSerializer(read_only=True)

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'description', 'adresse',
            'thumbnail', 'typestore', 'typebusiness',
            'country', 'city', 'latitude', 'longitude',
            'created_at', 'updated_at', 'owner',
            'is_subscribed', 'subscribers_count',
            'average_rating',  # ← ✅ Ajout ici
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'owner']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoreSubscription.objects.filter(user=request.user, store=obj).exists()
        return False

    def get_subscribers_count(self, obj):
        return obj.subscribers.count()

    def get_average_rating(self, obj):
        result = Testimonial.objects.filter(store=obj).aggregate(avg=Avg('rating'))
        if result['avg']:
             return round(result['avg'] / 2, 1)  # ✅ division par 2
        return 0.0




from rest_framework import serializers
from .models import StoreSubscription

class StoreSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Affiche l'email de l'utilisateur
    store = serializers.StringRelatedField(read_only=True)  # Affiche le nom du store
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        source='store',
        write_only=True
    )

    class Meta:
        model = StoreSubscription
        fields = ['id', 'user', 'store', 'store_id', 'subscribed_at']
        read_only_fields = ['id', 'user', 'store', 'subscribed_at']


from rest_framework import serializers
from .models import SpotPubStore

from rest_framework import serializers
from .models import SpotPubStore

class SpotPubStoreSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = SpotPubStore
        fields = ['id', 'store', 'video', 'uploaded_at']

    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        return None

# serializers.py
from rest_framework import serializers
from .models import StoreVisit

class StoreVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreVisit
        fields = ['store', 'user', 'ip_address', 'date', 'count']



from rest_framework import serializers
from .models import Notification
class NotificationSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source='store.id', read_only=True)
    store_slug = serializers.CharField(source='store.slug', read_only=True)
    is_read = serializers.BooleanField(read_only=True)  # ✅ Ajout du champ is_read

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'description', 'image',
            'created_at', 'store_id', 'store_slug', 'is_read'
        ]
        read_only_fields = ['id', 'created_at', 'is_read']



from rest_framework import serializers
from .models import ContactStore

class ContactStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactStore
        fields = ['id', 'store', 'first_name', 'last_name', 'email', 'phone_number', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


from rest_framework import serializers
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'product']
        read_only_fields = ['id']

from rest_framework import serializers
from decimal import Decimal
from .models import Product,TypeProduct
from decimal import Decimal
from rest_framework import serializers
from .models import Product, TypeProduct
from .serializers import PhotoSerializer

from decimal import Decimal
from rest_framework import serializers
from core.models import Product, TypeProduct
from core.serializers import PhotoSerializer

class ProductSerializer(serializers.ModelSerializer):
    type_product = serializers.PrimaryKeyRelatedField(queryset=TypeProduct.objects.all(), required=False)
    photos = PhotoSerializer(many=True, read_only=True)
    store = serializers.PrimaryKeyRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    currency = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()  # ✅ ajouté

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'price_with_commission',
            'stock', 'image', 'image_galerie', 'type_product', 'store',
            'category', 'photos', 'created_at', 'currency', 'average_rating',  # ✅ ici
        ]
        read_only_fields = ['price_with_commission', 'created_at']

    def get_currency(self, obj):
        try:
            return obj.store.country.devise_info.devise
        except AttributeError:
            return ''

    def get_average_rating(self, obj):
        testimonials = obj.testimonials.all()
        if not testimonials.exists():
            return 0.0
        total = sum(t.rating for t in testimonials)
        average = total / testimonials.count()
        return round(average / 2, 1)

    def create(self, validated_data):
        store = self.context['request'].user.stores.first()
        price = validated_data.get('price', Decimal('0.00'))

        if store and not store.apply_commission:
            validated_data['price_with_commission'] = price
        else:
            validated_data['price_with_commission'] = price + (price * Decimal('0.30'))

        validated_data['store'] = store
        return super().create(validated_data)

    def update(self, instance, validated_data):
        store = instance.store
        price = validated_data.get('price', instance.price)

        if store and store.apply_commission:
            instance.price_with_commission = price + (price * Decimal('0.30'))
        else:
            instance.price_with_commission = price

        return super().update(instance, validated_data)




# serializers.py
# serializers.py
class TypeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeProduct
        fields = ['id', 'nom']




# serializers.py
from rest_framework import serializers
from .models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Récupère username
    store = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Testimonial
        fields = ['id', 'store', 'user', 'content', 'rating', 'created_at']
        read_only_fields = ['id', 'store', 'user', 'created_at']

    def get_user(self, obj):
        return {
            "username": obj.user.username,
            "profile_pic": obj.user.profile_pic.url if obj.user.profile_pic else None,
        }


# serializers.py
from rest_framework import serializers
from .models import Category, AssignerCategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'store']


class AssignerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignerCategory
        fields = ['id', 'product', 'category']

# serializers.py
from rest_framework import serializers
from .models import ContactProduct

# serializers.py
class ContactProductSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = ContactProduct
        fields = ['product', 'first_name', 'last_name', 'email', 'phone_number', 'description']



# serializers.py
from rest_framework import serializers
from .models import Testimonialproduct

class TestimonialProductSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Testimonialproduct
        fields = ['id', 'product', 'user', 'content', 'rating', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def get_user(self, obj):
        return {
            "username": obj.user.username,
            "profile_pic": obj.user.profile_pic.url if obj.user.profile_pic else None
        }


# serializers.py

from rest_framework import serializers
from .models import Cart, CartItem
 # Assurez-vous que le modèle Product est bien importé

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price_with_commission', read_only=True, max_digits=10, decimal_places=2)
    product_image = serializers.ImageField(source='product.image', read_only=True)  # ✅ Nouveau champ
    product_currency = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'product_image', 'product_currency']
    
    def get_product_currency(self, obj):
        try:
            return getattr(obj.product.store.country.devise_info, 'devise', '')
        except AttributeError:
            return ''

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    country = CountrySerializer(read_only=True)  # Donne id + name

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'country',
            'created_at',
            'is_ordered',
            'is_active',
            'items',
            'total_price',
            'item_count'
        ]
        read_only_fields = ['user']

    def get_total_price(self, obj):
        return obj.get_total()

    def get_item_count(self, obj):
        return obj.get_item_count()
    
# serializers.py

from rest_framework import serializers
from .models import MobileMoneyPayment

class MobileMoneyPaymentSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = MobileMoneyPayment
        fields = [
            'id',
            'user',
            'transaction_number',
            'transaction_id',
            'first_name',
            'last_name',
            'phone_number',
            'delivery_option',
            'status',
            'created_at',
            'country',
        ]
        read_only_fields = ['user', 'status', 'created_at']


# serializers.py

from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.ImageField(source='product.image', read_only=True)
    store_name = serializers.CharField(source='product.store.name')
    store_id = serializers.IntegerField(source='product.store.id')

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_name',
            'product_image',
            'quantity',
            'price_at_time_of_order',
            'store_name',
            'store_id',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(source='get_total', max_digits=10, decimal_places=2, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_username', 'user_email',
            'status', 'activated', 'created_at', 'updated_at',
            'total', 'items'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'total', 'items']


# serializers.py

from rest_framework import serializers
from .models import UserPoints,NumeroPaye,StoreCoManager

class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['points', 'ad_points', 'spent_points', 'total_purchases']


# serializers.py
class NumeroPayeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumeroPaye
        fields = ['nom', 'image', 'numero_paye']

class StoreCoManagerSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    added_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)  # pour format ISO

    class Meta:
        model = StoreCoManager
        fields = ['id', 'store', 'user', 'user_email', 'added_at']


from rest_framework import serializers
from .models import CustomUser  # ou adapte si le modèle s’appelle différemment

from rest_framework import serializers
from core.models import CustomUser  # remplace selon ton projet

class UserSimpleSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_pic']

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.profile_pic:
            url = obj.profile_pic.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None



from rest_framework import serializers
from .models import Lottery, LotteryParticipation
from django.contrib.auth import get_user_model

User = get_user_model()
class LotterySerializer(serializers.ModelSerializer):
    current_participant_count = serializers.SerializerMethodField()
    top_winner = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Lottery
        fields = [
            'id', 'title', 'description', 'image', 'created_at',
            'max_participants', 'is_active', 'number_of_winners',
            'participation_fee', 'current_participant_count', 'top_winner'
        ]

    def get_current_participant_count(self, obj):
        return obj.current_participant_count()

    def get_top_winner(self, obj):
        winner = obj.participations.filter(winner_rank=1).select_related('user').first()
        if winner and winner.user:
           user = winner.user
           request = self.context.get('request')
           profile_pic_url = (
            request.build_absolute_uri(user.profile_pic.url)
              if user.profile_pic and request else None
           )
           return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_pic': profile_pic_url,
            'full_name': winner.full_name,  # ✅ AJOUT ICI
        }
        return None


    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




from rest_framework import serializers
from .models import LotteryParticipation
 # à adapter selon ton projet

class LotteryParticipationSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = LotteryParticipation
        fields = [
            'id', 'lottery', 'user', 'full_name',
            'id_transaction', 'phone_number', 'is_winner',
            'winner_rank', 'submitted_at', 'is_active'
        ]



 # adapte selon ton projet
# serializers.py
from rest_framework import serializers
from .models import ProductPoints, PhotoPoints, Purchase, PointConversion

class PhotoPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoPoints
        fields = ['id', 'image']

class ProductPointsSerializer(serializers.ModelSerializer):
    photos = PhotoPointsSerializer(many=True, read_only=True)
    usd_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductPoints
        fields = ['id', 'name', 'description', 'points_required', 'image', 'photos', 'created_at', 'usd_price']

    def get_usd_price(self, obj):
        try:
            conversion = PointConversion.objects.latest('id')
            return round(obj.points_required * float(conversion.conversion_rate), 2)
        except PointConversion.DoesNotExist:
            return 0.0


class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'product_name', 'product_image', 'points_used', 'purchase_date']


from rest_framework import serializers
from .models import Advertisement, Country, City
from rest_framework import serializers
from .models import Advertisement, PhotoAds
 # si tu veux une version détaillée

class PhotoAdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoAds
        fields = ['id', 'ads', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']



class AdvertisementSerializer(serializers.ModelSerializer):
    photos = PhotoAdsSerializer(many=True, read_only=True)
    store = StoreSerializer(read_only=True)
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source='store', write_only=True, required=False
    )

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'media_type', 'media_file',
            'thumbnail_url', 'url', 'slug', 'likes_count', 'comments_count',
            'shares_count', 'visits_count', 'created_at', 'is_active',
            'target_all_users', 'target_country', 'target_city',
            'max_likes', 'max_shares',
            'store', 'store_id',  # 👈 affichage + création
            'photos'  # 👈 galerie d'images
        ]
        read_only_fields = ['slug', 'likes_count', 'comments_count', 'shares_count', 'visits_count', 'created_at']


from rest_framework import serializers
from .models import AdInteraction, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'ad', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AdInteractionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AdInteraction
        fields = ['id', 'user', 'ad', 'interaction_type', 'timestamp']
        read_only_fields = ['id', 'timestamp']

# serializers.py
class UserMiniSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_pic']

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.profile_pic and request:
            return request.build_absolute_uri(obj.profile_pic.url)
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'ad', 'content', 'created_at', 'user']

    def get_user(self, obj):
        request = self.context.get('request')  # Pour générer une URL absolue
        avatar_url = (
            request.build_absolute_uri(obj.user.profile_pic.url)
            if obj.user.profile_pic and request
            else None
        )
        return {
            "username": obj.user.username,
            "avatar": avatar_url
        }


from rest_framework import serializers
from core.models import PopUpAdvertisement

class PopUpAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopUpAdvertisement
        fields = '__all__'


from rest_framework import serializers
from core.models import FeaturedStore
  # Suppose que tu as déjà un StoreSerializer

class FeaturedStoreSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    
    class Meta:
        model = FeaturedStore
        fields = ['id', 'store', 'show_in_all', 'country', 'city', 'start_date', 'end_date', 'created_at']
