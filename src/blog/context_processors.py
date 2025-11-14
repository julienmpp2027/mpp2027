from django.urls import reverse

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
        {'name': 'Me Contacter', 'url': reverse('blog:contact')},
    ]

    # On vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Si oui, on AJOUTE les liens pour les membres
        links.extend([
            {'name': 'Mon Profil Public', 'url': reverse('blog:auteur-profil', kwargs={'pk': request.user.pk})},
            {'name': 'Modifier mon Profil', 'url': reverse('users:profile')},
            {'name': 'Écrire un article', 'url': reverse('blog:article-create')},
        ])

    # On retourne le dictionnaire.
    # La clé 'main_nav_links' sera le nom de la variable dans les templates.
    return {
        'main_nav_links': links
    }