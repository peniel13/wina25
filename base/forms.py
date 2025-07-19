
from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['user', 'title', 'description', 'video_file', 'thumbnail', 'featured']

    # Tu peux ajouter des validations personnalisées ici si nécessaire
    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            if video_file.size > 100 * 1024 * 1024:  # Limite de taille à 100MB
                raise forms.ValidationError("La taille de la vidéo ne doit pas dépasser 100 MB.")
        return video_file

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            if thumbnail.size > 5 * 1024 * 1024:  # Limite de taille de l'image miniature à 5MB
                raise forms.ValidationError("La taille de l'image miniature ne doit pas dépasser 5 MB.")
        return thumbnail



from django import forms
from .models import Requete, Response
from core.models import  Country, City

class RequeteForm(forms.ModelForm):
    class Meta:
        model = Requete
        fields = [
            'nom', 'email', 'telephone',
            'country', 'city', 'commune',
            'description', 'type_bien', 'audio'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre email'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre téléphone'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'commune': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Entrez votre commune'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Décrivez votre requête',
                'rows': 4
            }),
            'type_bien': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'audio': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': 'audio/*'
            }),
        }


   
class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['nom', 'post_nom', 'email', 'telephone', 'message', 'audio']
    audio = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'accept': 'audio/*'}))

