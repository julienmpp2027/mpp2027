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
    # On définit le champ 'contenu' avec l'éditeur riche
    contenu = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)

    class Meta:
        model = Article
        fields = ('titre', 'contenu', 'image_banniere', 'categories')

        widgets = {
            'categories': forms.CheckboxSelectMultiple,
            'titre': forms.TextInput(
                attrs={'class': 'form-control-large', 'placeholder': 'Le titre de votre article...'}
            ),
        }
        labels = {
            'image_banniere': "Image de bannière (facultatif)",
        }

    def clean_image_banniere(self):
        """
        Validation personnalisée pour l'image de bannière.
        Vérifie que le fichier ne dépasse pas une certaine taille (ex: 5 Mo).
        """
        image = self.cleaned_data.get('image_banniere')

        if image:
            # On définit la limite (5 Mo = 5 * 1024 * 1024 octets)
            limit_mb = 5
            if image.size > limit_mb * 1024 * 1024:
                raise forms.ValidationError(f"L'image est trop volumineuse. La taille maximale est de {limit_mb} Mo.")

        return image

    def save(self, commit=True, user=None):
        # ... (Votre méthode save existante reste identique) ...
        article = super().save(commit=False)
        if user:
            article.auteur = user
        article.statut = Article.Status.DRAFT
        if commit:
            article.save()
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