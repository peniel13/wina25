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
