from django import forms
from .models import Commentaire, Article
from django_ckeditor_5.widgets import CKEditor5Widget


# =============================================================================
#                FORMULAIRE POUR LES COMMENTAIRES
# =============================================================================
class CommentaireForm(forms.ModelForm):
    """
    Un formulaire simple basé sur notre modèle Commentaire.
    """

    class Meta:
        # 1. De quel modèle ce formulaire s'inspire-t-il ?
        model = Commentaire

        # 2. Quels champs l'utilisateur doit-il voir ?
        #    On ne demande QUE le contenu.
        #    L'auteur et l'article seront gérés en coulisses (par la vue).
        fields = ('contenu',)

    def __init__(self, *args, **kwargs):
        """
        Un peu de cosmétique pour améliorer le formulaire.
        """
        super().__init__(*args, **kwargs)

        # On veut que le champ 'contenu' soit un <textarea>
        # et non un simple <input>
        self.fields['contenu'].widget = forms.Textarea(attrs={'rows': 4})

        # On peut aussi changer son "étiquette"
        self.fields['contenu'].label = "Votre commentaire"

        # On lui dit de "zapper" le texte d'aide du modèle.
        self.fields['contenu'].help_text = None


# =============================================================================
#                FORMULAIRE DE CRÉATION D'ARTICLE
# =============================================================================

class ArticleForm(forms.ModelForm):
    # On définit le champ 'contenu' ici comme avant
    contenu = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)

    class Meta:
        model = Article
        fields = ('titre', 'contenu', 'image_banniere', 'categories')

        # --- LA SOLUTION EST ICI ---
        # On définit les widgets directement dans la Meta
        # C'est plus propre et ça évite le bug de __init__
        widgets = {
            'categories': forms.CheckboxSelectMultiple,
            'titre': forms.TextInput(
                attrs={'class': 'form-control-large', 'placeholder': 'Le titre de votre article...'}),
        }

        # On peut aussi définir les labels ici
        labels = {
            'image_banniere': "Image de bannière (facultatif)",
        }

    def save(self, commit=True, user=None):
        """
        On surcharge la méthode save() pour forcer l'auteur
        et le statut brouillon.
        """
        #  On récupère l'objet article "en mémoire" (commit=False)
        article = super().save(commit=False)

        #  On assigne l'auteur (s'il est fourni par la vue)
        if user:
            article.auteur = user

        #  On force le statut (c'est notre règle de modération)
        article.statut = Article.Status.DRAFT

        # On sauvegarde l'objet principal (si commit=True)
        if commit:
            article.save()
            # On sauvegarde les M2M (très important !)
            self.save_m2m()

        return article


# =============================================================================
#                        FORMULAIRE DE CONTACT
# =============================================================================
class ContactForm(forms.Form):
    """
    Formulaire pour que les visiteurs envoient un email.
    """
    # Ce n'est pas un ModelForm, on définit les champs à la main.
    nom = forms.CharField(
        max_length=100,
        label="Votre nom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom complet'})
    )
    email = forms.EmailField(
        label="Votre email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com'})
    )
    sujet = forms.CharField(
        max_length=150,
        label="Sujet",
        widget=forms.TextInput(attrs={'placeholder': 'La raison de votre message'})
    )
    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={'rows': 6, 'placeholder': 'Écrivez votre message ici...'})
    )