from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import CustomUser

from django import forms
from .models import CustomUser, Country, City

from django import forms
from core.models import CustomUser, Country, City

from django import forms
from simplemathcaptcha.fields import MathCaptchaField
from core.models import CustomUser, Country, City  # adapte les imports si besoin

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirmer le mot de passe")

    # ✅ Ajout du captcha mathématique
    captcha = MathCaptchaField(label="Captcha de sécurité")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'commune', 'city', 'country', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.all().order_by('name')
        self.fields['city'].queryset = City.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# class RegisterForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput(), label="Mot de passe")
#     confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirmer le mot de passe")

#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'phone', 'commune', 'city', 'country', 'password']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['country'].queryset = Country.objects.all().order_by('name')
#         self.fields['city'].queryset = City.objects.all().order_by('name')

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#         if password and confirm_password and password != confirm_password:
#             raise forms.ValidationError("Les mots de passe ne correspondent pas.")
#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


from django import forms
from .models import Store

from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name', 'description', 'adresse', 'thumbnail',
            'typestore', 'typebusiness', 'country', 'city',
            'latitude', 'longitude'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nom du store'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Description du store'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Adresse du store'
            }),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'typestore': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'typebusiness': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Latitude',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Longitude',
                'step': '0.000001'
            }),
           
           
        }

from .models import StoreSubscription

class StoreSubscriptionForm(forms.ModelForm):
    class Meta:
        model = StoreSubscription
        fields = ['store']  # Le champ "store" est nécessaire pour créer une nouvelle souscription

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Passer l'utilisateur lors de l'initialisation du formulaire
        super().__init__(*args, **kwargs)
        if user:
            # Le formulaire doit seulement permettre l'abonnement à un magasin qui n'est pas encore souscrit par l'utilisateur
            self.fields['store'].queryset = Store.objects.exclude(subscribers=user)
        else:
            self.fields['store'].queryset = Store.objects.none()

from django import forms
from .models import Testimonial,Testimonialproduct # Assurez-vous que le modèle Testimonial est importé

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['content', 'rating']  # Le champ 'store' est exclu car il est automatiquement pris en compte
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Partagez votre témoignage'
            }),
            'rating': forms.Select(choices=Testimonial.RATING_CHOICES, attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }

from .models import SpotPubStore

class SpotPubStoreForm(forms.ModelForm):
    class Meta:
        model = SpotPubStore
        fields = ['video']

    def clean_video(self):
        video = self.cleaned_data.get('video')
        max_size = 10 * 1024 * 1024  # 10 Mo

        if video and video.size > max_size:
            raise forms.ValidationError("La vidéo dépasse la taille maximale autorisée (10 Mo).")
        return video

from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Application de styles uniformes pour les champs
        self.fields['title'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Titre de la notification'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Description de la notification'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })


from .models import ContactStore

class ContactStoreForm(forms.ModelForm):
    class Meta:
        model = ContactStore
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'description']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre adresse email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre numéro de téléphone'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Décrivez votre demande...',
                'rows': 4
            }),
        }


class TestimonialproductForm(forms.ModelForm):
    class Meta:
        model = Testimonialproduct
        fields = ['content', 'rating']  # Le champ 'store' est exclu car il est automatiquement pris en compte
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Partagez votre témoignage'
            }),
            'rating': forms.Select(choices=Testimonial.RATING_CHOICES, attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }


from .models import ContactProduct,Category

class ContactProductForm(forms.ModelForm):
    class Meta:
        model = ContactProduct
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'description']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre adresse email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre numéro de téléphone'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Décrivez votre demande...',
                'rows': 4
            }),
        }

    # Optionnel: validation personnalisée pour le numéro de téléphone
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        return phone_number


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez le nom du store'
            }),
            }

from .models import Product,Photo,CartItem# Assurez-vous que le modèle Product est importé
from django import forms
from .models import Product

from decimal import Decimal

from django import forms
from .models import Product, Category
from django import forms
from .models import Product, Category
from decimal import Decimal
from django import forms
from .models import Product

from django import forms
from decimal import Decimal
from .models import Product


class ProductForm(forms.ModelForm):
    video = forms.FileField(
        required=False,
        help_text="Ajoutez une vidéo (optionnelle, max 10 Mo)",
        widget=forms.FileInput(attrs={'accept': 'video/*'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'image_galerie', 'type_product', 'video']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_class = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'

        self.fields['name'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Entrez le nom du produit'
        })

        self.fields['description'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Décrivez le produit',
            'rows': 4
        })

        self.fields['price'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Entrez le prix'
        })

        self.fields['stock'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Indiquez le stock disponible'
        })

        self.fields['image'].widget.attrs.update({'class': common_class})
        self.fields['image_galerie'].widget.attrs.update({'class': 'hidden'})  # caché, remplacé par input custom
        self.fields['type_product'].widget.attrs.update({'class': common_class})
        self.fields['video'].widget.attrs.update({'class': common_class})

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            max_size_mb = 10
            if video.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"La vidéo ne doit pas dépasser {max_size_mb} Mo.")
        return video


    def save(self, commit=True):
        product = super().save(commit=False)

        if product.price is not None:
            commission = product.price * Decimal('0.30')
            product.price_with_commission = product.price + commission

        if commit:
            product.save()

        return product


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'stock', 'image', 'image_galerie', 'type_product']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         common_class = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'

#         self.fields['name'].widget.attrs.update({
#             'class': common_class,
#             'placeholder': 'Entrez le nom du produit'
#         })

#         self.fields['description'].widget.attrs.update({
#             'class': common_class,
#             'placeholder': 'Décrivez le produit',
#             'rows': 4
#         })

#         self.fields['price'].widget.attrs.update({
#             'class': common_class,
#             'placeholder': 'Entrez le prix'
#         })

#         self.fields['stock'].widget.attrs.update({
#             'class': common_class,
#             'placeholder': 'Indiquez le stock disponible'
#         })

#         self.fields['image'].widget.attrs.update({
#             'class': common_class,
#         })

#         self.fields['image_galerie'].widget.attrs.update({
#             'class': 'hidden',  # Champ caché (upload JS peut-être)
#         })

#         self.fields['type_product'].widget.attrs.update({
#             'class': common_class,
#         })

#     def save(self, commit=True, *args, **kwargs):
#         product = super().save(commit=False, *args, **kwargs)

#         # Appliquer la commission de 30%
#         if product.price is not None:
#             commission = product.price * Decimal('0.30')
#             product.price_with_commission = product.price + commission

#         if commit:
#             product.save()

#         return product



from django import forms
from .models import AssignerCategory, Category

class AssignerCategoryForm(forms.ModelForm):
    class Meta:
        model = AssignerCategory
        fields = ['category']

    def __init__(self, *args, **kwargs):
        store = kwargs.pop('store', None)  # Récupérer le store depuis la vue
        super().__init__(*args, **kwargs)

        # Filtrer les catégories disponibles pour ce store uniquement
        if store:
            self.fields['category'].queryset = Category.objects.filter(store=store)

        # Appliquer des styles aux champs
        self.fields['category'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })

    

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })



from .models import Cart, CartItem

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = []  # Le modèle Cart n'a pas de champs directement modifiables via un formulaire

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le formulaire ne manipule pas directement des champs dans Cart, 
        # mais plutôt les CartItems associés au panier
        self.fields['quantity'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Quantité'
        })


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']  # Le champ 'quantity' permet de modifier la quantité d'un produit dans le panier

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Quantité',
        })


from .models import MobileMoneyPayment

class MobileMoneyPaymentForm(forms.ModelForm):
    class Meta:
        model = MobileMoneyPayment
        fields = ['first_name', 'last_name', 'transaction_number', 'transaction_id', 'phone_number', 'delivery_option']

    def clean_transaction_id(self):
        transaction_id = self.cleaned_data['transaction_id']
        if MobileMoneyPayment.objects.filter(transaction_id=transaction_id).exists():
            raise forms.ValidationError("Ce numéro de transaction a déjà été utilisé.")
        return transaction_id




from .models import LotteryParticipation
from django import forms
from .models import LotteryParticipation
class LotteryParticipationForm(forms.ModelForm):
    class Meta:
        model = LotteryParticipation
        fields = ['full_name', 'phone_number', 'id_transaction']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.lottery = kwargs.pop('lottery', None)
        super().__init__(*args, **kwargs)

        # Style unifié pour les champs
        self.fields['full_name'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Votre nom complet'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Votre numéro de téléphone'
        })
        self.fields['id_transaction'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'ID de transaction'
        })

    def clean(self):
        cleaned_data = super().clean()
        if self.lottery.current_participant_count() >= self.lottery.max_participants:
            raise forms.ValidationError("Le nombre maximum de participants a été atteint.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        instance.lottery = self.lottery
        if commit:
            instance.save()
        return instance


from .models import ProductPoints

class ProductPointsForm(forms.ModelForm):
    class Meta:
        model = ProductPoints
        fields = ['name', 'points_required', 'description', 'image']  # Mise à jour du champ 'product' vers 'name'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })
        self.fields['points_required'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Entrez le nombre de points nécessaires'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Décrivez le produit',
            'rows': 4
        })
        self.fields['image'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
        })

from django import forms
from .models import ContactProductPoints

class ContactProductPointsForm(forms.ModelForm):
    class Meta:
        model = ContactProductPoints
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'description']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre adresse email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Votre numéro de téléphone'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Décrivez votre demande...',
                'rows': 4
            }),
        }

    # Optionnel: validation personnalisée pour le numéro de téléphone
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        return phone_number



from django import forms
from .models import Advertisement
from django import forms
from .models import Advertisement
 # Assure-toi que ce modèle est bien importé
from django import forms
from core.models import Advertisement, Store
from django import forms
from core.models import Advertisement, Store

class AdvertisementForm(forms.ModelForm):
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'data-live-search': 'true'})
    )

    class Meta:
        model = Advertisement
        fields = [
            'title', 'description', 'media_type', 'media_file', 'thumbnail_url',
            'url', 'target_all_users', 'target_country', 'target_city',
            'store',
            'max_likes', 'max_shares', 'max_comments',  # ← tu peux les garder si tu veux un contrôle séparé
            'max_interactions',  # ✅ ajouté ici
            'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'media_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'thumbnail_url': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'target_all_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_country': forms.Select(attrs={'class': 'form-control'}),
            'target_city': forms.Select(attrs={'class': 'form-control'}),
            'max_likes': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_shares': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_comments': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_interactions': forms.NumberInput(attrs={'class': 'form-control'}),  # ✅ widget ajouté
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# class AdvertisementForm(forms.ModelForm):
#     store = forms.ModelChoiceField(
#         queryset=Store.objects.all(),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control', 'data-live-search': 'true'})
#     )

#     class Meta:
#         model = Advertisement
#         fields = [
#             'title', 'description', 'media_type', 'media_file', 'thumbnail_url',
#             'url', 'target_all_users', 'target_country', 'target_city',
#             'store',  # ✅ champ ajouté
#             'max_likes', 'max_shares', 'is_active'
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'media_type': forms.Select(attrs={'class': 'form-control'}),
#             'media_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'thumbnail_url': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'url': forms.URLInput(attrs={'class': 'form-control'}),
#             'target_all_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'target_country': forms.Select(attrs={'class': 'form-control'}),
#             'target_city': forms.Select(attrs={'class': 'form-control'}),
#             'max_likes': forms.NumberInput(attrs={'class': 'form-control'}),
#             'max_shares': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }



from .models import AdInteraction,PopUpAdvertisement

class AdInteractionForm(forms.ModelForm):
    class Meta:
        model = AdInteraction
        fields = ['ad', 'interaction_type']

        widgets = {
            'ad': forms.Select(attrs={'class': 'form-control'}),
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Le champ 'content' pour le texte du commentaire
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Votre commentaire...'})
        }


from django import forms


class PopUpAdvertisementForm(forms.ModelForm):
    class Meta:
        model = PopUpAdvertisement
        fields = '__all__'


from django import forms
from core.models import FeaturedStore

class FeaturedStoreForm(forms.ModelForm):
    class Meta:
        model = FeaturedStore
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }



from .models import CommandeLivraison

class CommandeLivraisonForm(forms.ModelForm):
    class Meta:
        model = CommandeLivraison
        fields = [
            'nom', 'prenom', 'email', 'numero_tel', 'adresse_livraison', 
            'description_colis', 'endroit_recuperation', 'numero_id_colis'
        ]
        
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre nom'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre prénom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre email'
            }),
            'numero_tel': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre numéro de téléphone'
            }),
            'adresse_livraison': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez l\'adresse de livraison'
            }),
            'description_colis': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Description du colis'
            }),
            'endroit_recuperation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Endroit de récupération'
            }),
            'numero_id_colis': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Numéro d\'ID du colis'
            }),
        }

    # Optionnel : Personnaliser la validation
    def clean_numero_tel(self):
        numero_tel = self.cleaned_data.get('numero_tel')
        if not numero_tel.isdigit():
            raise forms.ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
        return numero_tel

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if '@' not in email:
            raise forms.ValidationError("Veuillez entrer un email valide.")
        return email

# forms.py
from django import forms
from django.contrib.auth import get_user_model
from core.models import City, Country

User = get_user_model()

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'profile_pic', 'address', 'phone',
            'commune', 'city', 'country', 'interests'
        ]
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 3}),
        }


from django import forms

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Ancien mot de passe")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if len(password) < 6:
            raise forms.ValidationError("Le nouveau mot de passe doit contenir au moins 6 caractères.")
        return password



from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class TransferPointsForm(forms.Form):
    receiver = forms.CharField(
        label="Choisir un bénéficiaire",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d’utilisateur du bénéficiaire',
            'autocomplete': 'off',
            'id': 'receiver-search-input'
        })
    )

    def clean_receiver(self):
        username = self.cleaned_data['receiver']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("❌ Cet utilisateur n'existe pas.")
        return user  # 🔁 Retourne l'objet `User`, pas juste le texte

# core/forms.py
from django import forms
from .models import PointSharingGroup

class PointSharingGroupForm(forms.ModelForm):
    class Meta:
        model = PointSharingGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du groupe de partage'
            })
        }
        labels = {
            'name': 'Nom du groupe'
        }
