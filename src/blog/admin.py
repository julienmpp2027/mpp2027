from django.contrib import admin
from .models import Categorie, Article, Commentaire


# -----------------------------------------------------------------------------
# 1. Configuration pour Categorie
# -----------------------------------------------------------------------------
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Categorie.
    """
    # Ce qu'on voit dans la liste des catégories
    list_display = ('nom', 'slug')

    # Permet de rechercher par nom
    search_fields = ('nom',)

    # LA FONCTION MAGIQUE :
    # Quand vous écrirez "Python et Django" dans le champ 'nom',
    # le champ 'slug' se remplira en temps réel avec "python-et-django".
    # Fini la saisie manuelle des slugs !
    prepopulated_fields = {'slug': ('nom',)}


# -----------------------------------------------------------------------------
# 2. Configuration pour Article
# -----------------------------------------------------------------------------
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Article.

    """
    # Colonnes à afficher dans la liste des articles
    list_display = ('titre', 'auteur', 'statut', 'date_creation')

    # Ajoute un panneau de filtre sur la droite
    list_filter = ('statut', 'date_creation', 'auteur')

    # Barre de recherche
    search_fields = ('titre', 'contenu')

    # Magie N°1 : Auto-remplissage du slug
    prepopulated_fields = {'slug': ('titre',)}

    # Magie N°2 : Une belle interface pour choisir les catégories
    filter_horizontal = ('categories',)

    # Nous avons retiré 'auteur' du fieldset.
    # Le titre de la section a aussi été simplifié.
    fieldsets = (
        (None, {
            'fields': ('titre', 'slug', 'contenu', 'image_banniere')
        }),
        ('Publication', {  # C'était "Publication et Auteur"
            'fields': ('statut', 'categories')  # 'auteur' a été retiré
        }),
    )

    # --- FONCTION ---
    def save_model(self, request, obj, form, change):
        """
        Cette fonction est appelée à chaque sauvegarde d'un Article
        depuis l'interface d'administration.

        request = L'objet requête (contient l'utilisateur connecté)
        obj = L'objet Article qui est en train d'être sauvegardé
        form = Le formulaire
        change = Un booléen (True si c'est une modification, False si c'est une création)
        """

        # Si l'objet (l'article) n'a pas encore d'auteur
        # (ce qui est le cas lors de la création)...
        if not obj.auteur:
            # On définit l'auteur comme étant l'utilisateur connecté
            obj.auteur = request.user

        # On appelle la méthode 'save_model' de la classe parente
        # pour que la sauvegarde se fasse normalement.
        super().save_model(request, obj, form, change)

# -----------------------------------------------------------------------------
# 3. Configuration pour Commentaire
# -----------------------------------------------------------------------------
@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Commentaire.
    On se concentre sur la MODÉRATION.
    """
    list_display = ('auteur', 'article', 'date_creation', 'approuve')
    list_filter = ('approuve', 'date_creation')
    search_fields = ('contenu', 'auteur__email', 'article__titre')

    # On ne veut pas que l'admin puisse *modifier* le contenu
    # d'un commentaire, seulement l'approuver ou le supprimer.
    # On rend les champs "lecture seule".

    readonly_fields = ('article', 'auteur', 'contenu', 'date_creation')

    # On n'affiche que le champ 'approuve' pour la modification
    fields = ('approuve', 'article', 'auteur', 'contenu', 'date_creation')

    # MAGIE N°3 : LES ACTIONS D'ADMINISTRATION
    # Ajoute un menu déroulant pour "Approuver" ou "Désapprouver"
    # des commentaires en masse.

    def approve_comments(self, request, queryset):
        queryset.update(approuve=True)

    approve_comments.short_description = "Approuver les commentaires sélectionnés"

    def unapprove_comments(self, request, queryset):
        queryset.update(approuve=False)

    unapprove_comments.short_description = "Désapprouver les commentaires sélectionnés"

    # On ajoute nos actions au menu
    actions = [approve_comments, unapprove_comments]

    # On empêche l'admin de "Créer" un commentaire (ça n'a pas de sens)
    def has_add_permission(self, request):
        return False