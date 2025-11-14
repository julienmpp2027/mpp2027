from django.db import models
from django.utils import timezone
from django.conf import settings  # Pour l'auteur (FK vers CustomUser)
from django.utils.text import slugify  # Pour générer les slugs
from django.urls import reverse  # Pour retourner l'adresse


# =============================================================================
# 1. Modèle CATEGORIE
# =============================================================================
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, help_text="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="URL (généré automatiquement)")

    class Meta:
        verbose_name = "Catégorie"  # Nom singulier dans l'admin
        verbose_name_plural = "Catégories"  # Nom pluriel dans l'admin
        ordering = ['nom']  # Ordonner par nom alphabétique

    def save(self, *args, **kwargs):
        # Génère automatiquement le slug à partir du nom
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom  # Ce qui s'affiche dans l'admin (ex: "Python")


# =============================================================================
# 2. Modèle ARTICLE
# =============================================================================
class Article(models.Model):
    # Choix pour le champ statut
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        PUBLISHED = 'PUBLISHED', 'Publié'

    # --- Champs principaux ---
    titre = models.CharField(max_length=250, help_text="Titre de l'article")
    slug = models.SlugField(max_length=270, unique=True, blank=True, help_text="URL (généré automatiquement)")
    contenu = models.TextField(help_text="Contenu de l'article (Markdown ou texte brut)")
    image_banniere = models.ImageField(
        upload_to='article_banners/',
        blank=True,
        null=True,
        help_text="Facultatif. Image d'en-tête."
    )
    statut = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Statut de l'article (Brouillon ou Publié)"
    )

    # --- Dates ---
    date_creation = models.DateTimeField(auto_now_add=True)  # Date de création (automatique)
    date_modification = models.DateTimeField(auto_now=True)  # Mise à jour (automatique)

    # --- Relations (Connexions) ---

    # Auteur (un-à-plusieurs)
    # AUTH_USER_MODEL vient de notre settings.py
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Si l'auteur est supprimé, on garde l'article (auteur = null)
        null=True,  # Permet à l'auteur d'être null dans la BDD
        related_name='articles_ecrits',  # Nom pour retrouver les articles depuis un User
        help_text="L'auteur de l'article"
    )

    # Catégories (plusieurs-à-plusieurs)
    categories = models.ManyToManyField(
        Categorie,
        related_name='articles',  # Nom pour retrouver les articles depuis une Categorie
        blank=True,  # Un article peut n'avoir aucune catégorie
        help_text="Catégories de l'article"
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        # Ordonner par défaut : les plus récents en premier
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        # Génère automatiquement le slug à partir du titre
        if not self.slug:
            self.slug = slugify(self.titre)
            # Assurer l'unicité (rare mais possible)
            # Si un slug "mon-titre" existe, on crée "mon-titre-2"
            original_slug = self.slug
            count = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{count}'
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre  # Ce qui s'affiche dans l'admin

    def get_absolute_url(self):
        """
        Retourne l'URL complète pour un article.
        C'est une convention Django très importante.
        """
        # On utilise le 'name' de notre URL de détail
        # et on lui passe le 'slug' de l'article actuel.
        return reverse('blog:detail-article', kwargs={'slug': self.slug})

# =============================================================================
# 3. Modèle COMMENTAIRE
# =============================================================================
class Commentaire(models.Model):
    # --- Relations (Connexions) ---

    # Article (un-à-plusieurs)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,  # Si l'article est supprimé, supprime les commentaires
        related_name='commentaires',
        help_text="L'article auquel ce commentaire est lié"
    )

    # Auteur (un-à-plusieurs)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Si l'auteur est supprimé, on garde le commentaire
        null=True,
        related_name='commentaires_ecrits',
        help_text="L'auteur du commentaire"
    )

    # --- Champs principaux ---
    contenu = models.TextField(max_length=2000, help_text="Le contenu du commentaire")
    date_creation = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(
        default=True,  # Approuvé par défaut, comme demandé
        help_text="Statut d'approbation du commentaire"
    )

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        # Ordonner : les plus anciens en premier (ordre de lecture)
        ordering = ['date_creation']

    def __str__(self):
        # Texte d'aide dans l'admin
        return f'Commentaire par {self.auteur} sur {self.article.titre}'
