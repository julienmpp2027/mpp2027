from django import template

register = template.Library()

@register.filter
def split_title(value):
    """
    Coupe la chaîne au premier ':' et renvoie la première partie.
    Exemple: "Titre : Sous-titre" -> "Titre"
    """
    if ':' in value:
        return value.split(':')[0].strip()
    return value