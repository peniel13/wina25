from django import template
from urllib.parse import quote

register = template.Library()

@register.simple_tag
def share_url(network, url):
    encoded_url = quote(url, safe='')

    social_networks = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'twitter': f"https://twitter.com/intent/tweet?url={encoded_url}&text=Découvrez cette publicité !",
        'whatsapp': f"https://api.whatsapp.com/send?text={encoded_url}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
    }
    
    return social_networks.get(network, "#")
