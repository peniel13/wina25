from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Video(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="videos")
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField()
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    featured = models.BooleanField(default=False)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Video, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    
from core.models import Country,City

class Requete(models.Model):
    TYPE_BIEN_CHOICES = [
        ('maison', 'Maison'),
        ('appartement', 'Appartement'),
        ('hotel', 'Hôtel'),
        ('guesthouse', 'Guesthouse'),
        ('boutique', 'Boutique'),
        ('parcelle vide', 'Parcelle vide'),
        ('terrain agricole', 'Terrain agricole'),
        ('bureau', 'Bureau'),
        ('autres', 'Autres'),
    ]

    nom = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    commune = models.CharField(max_length=100, help_text="Entrez la commune manuellement")
    description = models.TextField()
    type_bien = models.CharField(max_length=50, choices=TYPE_BIEN_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)
    audio = models.FileField(upload_to='audio/requests/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.email}"



class Response(models.Model):
    requete = models.ForeignKey('Requete', on_delete=models.CASCADE, related_name='responses')
    nom = models.CharField(max_length=100)
    post_nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    audio = models.FileField(upload_to='audio/responses/', null=True, blank=True)  # Nouveau champ audio

    def __str__(self):
        return f"Response from {self.nom} {self.post_nom}"



from django.db import models
from django.contrib.auth.models import User

class Immobusiness(models.Model):
    TYPE_BIEN_CHOICES = [
        ('maison', 'Maison'),
        ('appartement', 'Appartement'),
        ('hotel', 'Hôtel'),
        ('guesthouse', 'Guesthouse'),
        ('boutique', 'Boutique'),
        ('parcelle vide', 'Parcelle vide'),
        ('terrain agricole', 'Terrain agricole'),
        ('bureau', 'Bureau'),
        ('autres', 'Autres'),
    ]
      
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='immobusinesses')
    nom = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    commune = models.CharField(max_length=100, help_text="Entrez la commune manuellement")
    description = models.TextField()
    objectif = models.CharField(max_length=20, choices=[('vente','Vente'),('location','Location')], default='vente')
    type_bien = models.CharField(max_length=50, choices=TYPE_BIEN_CHOICES)
    image_principale = models.ImageField(upload_to='immobusiness/main_images/', null=True, blank=True)
    actif = models.BooleanField(default=False)  # L'admin active la publication
    # 🔹 Nouveaux champs
    prix = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Entrez le prix du bien")
    devise = models.CharField(max_length=10, null=True, blank=True, help_text="Exemple : USD, CDF, EUR")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.get_objectif_display()}"

class ImmobusinessGallery(models.Model):
    immobusiness = models.ForeignKey(Immobusiness, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='immobusiness/gallery/')

    def __str__(self):
        return f"Image de {self.immobusiness.nom}"

class ImmobusinessResponse(models.Model):
    immobusiness = models.ForeignKey(Immobusiness, on_delete=models.CASCADE, related_name='responses')
    nom = models.CharField(max_length=100)
    post_nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    message = models.TextField()
    audio = models.FileField(upload_to='audio/immobusiness_responses/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réponse de {self.nom} {self.post_nom} pour {self.immobusiness.nom}"



