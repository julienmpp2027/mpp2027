from django.urls import reverse
from messagerie.models import Message

#######################################################################################################################
# ##                             FONCTION POUR GERER LES LIEN DU MENU DE LA NAVBAR                                 ## #
#######################################################################################################################
def nav_links(request):
    """
    Crée la liste des liens pour le menu principal (déroulant).
    S'exécute sur chaque requête.
    """

    # On commence par une liste de liens que TOUT LE MONDE voit
    links = [
        {'name': 'Accueil', 'url': reverse('blog:liste-articles')},
        # --- AJOUT ICI ---
        {'name': 'Simulateurs', 'url': reverse('simulateur:accueil')},
        # -----------------
        {'name': 'Le Projet', 'url': reverse('blog:articles-par-categorie', kwargs={'slug_categorie': 'programme'})},
        {'name': 'Actualités', 'url': reverse('blog:toutes-actualites')},
        {'name': 'Contact', 'url': reverse('blog:contact')},
    ]

    # On vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Si oui, on AJOUTE les liens pour les membres
        links.extend([
            {'name': 'Mon Profil Public', 'url': reverse('blog:auteur-profil', kwargs={'pk': request.user.pk})},
            {'name': 'Modifier mon Profil', 'url': reverse('users:profile')},
            {'name': 'Écrire un article', 'url': reverse('blog:article-create')},
            {'name': 'Ma Messagerie', 'url': reverse('messagerie:inbox')},
        ])

    # On retourne le dictionnaire.
    # La clé 'main_nav_links' sera le nom de la variable dans les templates.
    return {
        'main_nav_links': links
    }


def unread_messages_count(request):
    """
    Ajoute le nombre de messages non lus au contexte global.
    Disponible partout sous la variable {{ unread_count }}
    """
    if request.user.is_authenticated:
        # On compte les messages reçus qui ne sont pas lus
        count = Message.objects.filter(destinataire=request.user, lu=False).count()
        return {'unread_count': count}

    # Si pas connecté, 0 message
    return {'unread_count': 0}