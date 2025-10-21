from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Video
from .forms import VideoForm

class VideoAdmin(admin.ModelAdmin):
    form = VideoForm  # Utilise notre formulaire personnalisé pour l'administration

    list_display = ('title', 'user', 'created', 'updated', 'featured', )
    list_filter = ('featured', 'created')
    search_fields = ('title', 'description', 'user__username')  # Recherche par titre, description ou utilisateur
    prepopulated_fields = {'slug': ('title',)}  # Génère automatiquement le slug à partir du titre
    ordering = ('-created',)  # Tri par date de création (descendant)

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'slug', 'description', 'video_file', 'thumbnail', 'featured')
        }),
        ('Dates', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created', 'updated')  # Ces champs sont en lecture seule dans l'admin

    # Personnalisation de l'affichage dans la liste des vidéos
    def video_file_link(self, obj):
        return f'<a href="{obj.video_file.url}" target="_blank">Voir la vidéo</a>'
    video_file_link.allow_tags = True
    video_file_link.short_description = 'Vidéo'

    # Ajouter la colonne 'video_file_link' à l'affichage dans l'admin
    list_display = ('title', 'user', 'video_file_link', 'created', 'updated', 'featured',)

# Enregistrer le modèle et son interface d'administration
admin.site.register(Video, VideoAdmin)


from django.contrib import admin
from .models import Requete,Response

@admin.register(Requete)
class RequeteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'country', 'city', 'commune', 'type_bien', 'created_at', 'contacted')
    list_filter = ('country', 'city', 'type_bien', 'contacted', 'created_at')
    search_fields = ('nom', 'email', 'telephone', 'commune', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('nom', 'email', 'telephone')
        }),
        ('Localisation', {
            'fields': ('country', 'city', 'commune')
        }),
        ('Détails de la requête', {
            'fields': ('type_bien', 'description', 'audio')
        }),
        ('Suivi', {
            'fields': ('contacted', 'created_at')
        }),
    )


class ReponseInline(admin.TabularInline):
    model = Response
    extra = 1
    fields = ('nom', 'post_nom', 'email', 'telephone', 'message', 'created_at', 'audio')  # Ajouter 'audio'
    readonly_fields = ('created_at',)

# Admin pour le modèle Response
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'post_nom', 'email', 'created_at', 'audio')  # Ajouter 'audio'
    
    # Affichage des fichiers audio dans la liste des réponses
    def audio_tag(self, obj):
        if obj.audio:
            return f'<a href="{obj.audio.url}" target="_blank">Écouter</a>'
        return "Pas de fichier audio"
    audio_tag.allow_tags = True

# Enregistrement de Response avec son admin personnalisé
admin.site.register(Response, ResponseAdmin)



from django.contrib import admin
from .models import Immobusiness, ImmobusinessGallery, ImmobusinessResponse
from django.utils.html import format_html
# Inline pour afficher les images de la galerie dans Immobusiness
class ImmobusinessGalleryInline(admin.TabularInline):  # ou StackedInline pour plus grand affichage
    model = ImmobusinessGallery
    extra = 1  # Nombre de formulaires vides supplémentaires
    readonly_fields = ('image_preview',)

    # Afficher un aperçu de l'image
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height:auto;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Aperçu'

@admin.register(Immobusiness)
class ImmobusinessAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'type_bien', 'objectif', 'prix', 'devise',  # 🔹 Champs ajoutés ici
        'commune', 'city', 'country', 'actif', 'created_at'
    )
    list_filter = ('type_bien', 'objectif', 'actif', 'country', 'devise')  # 🔹 ajout de 'devise'
    search_fields = (
        'nom', 'commune', 'city__name', 'country__name', 
        'type_bien', 'objectif', 'devise'  # 🔹 ajout de 'devise' ici aussi
    )
    readonly_fields = ('created_at',)
    inlines = [ImmobusinessGalleryInline]
 # <-- Ajout de l'inline ici

@admin.register(ImmobusinessResponse)
class ImmobusinessResponseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'post_nom', 'email', 'telephone', 'immobusiness', 'created_at')
    list_filter = ('immobusiness', 'created_at')
    search_fields = ('nom', 'post_nom', 'email', 'immobusiness__nom')
    readonly_fields = ('created_at',)
