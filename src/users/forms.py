from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail


# -------------------------------------------------------------
# ------------ CLASSE POUR CONNECTION ----------------------
# -------------------------------------------------------------
class UserLoginForm(AuthenticationForm):
    """
    On hérite du formulaire de connexion de Django
    pour simplement ajuster son apparence.
    """

    def __init__(self, *args, **kwargs):
        # On appelle le constructeur parent (super important)
        super().__init__(*args, **kwargs)

        # le champ s'appelle 'username' en interne (à cause de la classe parente), mais on le fait ressembler à un
        # champ "email".

        # 1. Changer l'étiquette
        self.fields['username'].label = "Adresse email"

        # 2. Changer le "placeholder" (le texte en gris)
        self.fields['username'].widget.attrs.update(
            {'autofocus': True, 'placeholder': 'votre@email.com'}
        )

        # 3. On fait pareil pour le mot de passe
        self.fields['password'].label = "Mot de passe"
        self.fields['password'].widget.attrs.update(
            {'placeholder': 'Votre mot de passe'}
        )


# -------------------------------------------------------------
# ------------ CLASSE POUR L'INSCRIPTION ----------------------
# -------------------------------------------------------------
class UserRegisterForm(UserCreationForm):
    """
    Formulaire d'inscription pour un nouvel utilisateur.
    On hérite de UserCreationForm pour avoir la gestion
    automatique et sécurisée du mot de passe.
    """

    class Meta(UserCreationForm.Meta):
        # 1. On dit au formulaire de s'baser sur notre modèle
        model = CustomUser

        # 2. On liste les champs qu'on veut demander à l'utilisateur
        #    lors de son inscription.
        #    On demande l'email (obligatoire) et le pseudo (facultatif).
        #    Le mot de passe est géré par UserCreationForm.
        fields = ('email', 'pseudo')

    def __init__(self, *args, **kwargs):
        """
        On ajuste les étiquettes et les placeholders.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'placeholder': 'votre@email.com'}
        )
        self.fields['pseudo'].widget.attrs.update(
            {'placeholder': 'Votre pseudo (facultatif)'}
        )
        self.fields['pseudo'].help_text = None

# -------------------------------------------------------------
# ------------ CLASSE POUR RENOUVELLEMENT DU MDP CAR BUG ----------------------
# -------------------------------------------------------------

class UserPasswordResetForm(PasswordResetForm):
    """
    On surcharge la méthode save() pour contourner
    un bug apparent avec CustomUser.
    """

    # On n'a plus besoin de get_users() surchargé,
    # on va tout faire dans save().

    def save(self,
             domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='users/password_reset_email.html',  # On force le nôtre
             use_https=False,
             token_generator=default_token_generator,
             from_email=None,
             request=None,
             html_email_template_name=None,
             extra_email_context=None):
        """
        On remplace la méthode save() de Django.
        On va faire le travail nous-mêmes.
        """

        # 1. On récupère l'email du formulaire
        email = self.cleaned_data["email"]

        # 2. On fait la recherche (celle qui MARCHE, on l'a prouvé)
        active_users = CustomUser.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        # 3. On boucle sur les utilisateurs trouvés
        #    (Même si on sait qu'il n'y en a qu'un)
        for user in active_users:

            # 4. On vérifie le mot de passe (double sécurité)
            if not user.has_usable_password():
                # On ignore cet utilisateur
                continue

            # 5. On crée le contexte (les données pour l'email)
            if not domain_override:
                # On récupère le domaine (ex: 127.0.0.1:8000)
                # directement depuis la requête.
                domain = request.get_host()
                # C'est suffisant pour le nom du site
                site_name = domain
            else:
                site_name = domain = domain_override

            context = {
                "email": user.email,
                "domain": domain,
                "site_name": site_name,

                # --- LA PARTIE IMPORTANTE (qu'on fait nous-mêmes) ---
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                # --- FIN DE LA PARTIE IMPORTANTE ---

                "protocol": "https" if use_https else "http",
            }
            if extra_email_context is not None:
                context.update(extra_email_context)

            # 6. On génère l'email
            # On utilise .send_mail() qui est sur la classe parente
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user.email,
                html_email_template_name=html_email_template_name,
            )


# -------------------------------------------------------------
# ------------ CLASSE POUR FORMULAIRE DU PROFIL ----------------------
# -------------------------------------------------------------
class UserProfileForm(forms.ModelForm):
    """
    Formulaire profil utilisateur.
    """

    class Meta:
        model = CustomUser
        fields = ('pseudo', 'description', 'profile_picture')

        # AJOUT : On force le widget simple (FileInput) pour éviter le texte "Currently..."
        widgets = {
            'profile_picture': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 4})
        self.fields['description'].label = "Courte description"
        self.fields['profile_picture'].label = "Photo de profil"
        # On retire les textes d'aide comme demandé
        self.fields['pseudo'].help_text = None
        self.fields['description'].help_text = None
        self.fields['profile_picture'].help_text = None