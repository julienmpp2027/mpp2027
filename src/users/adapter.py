from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adaptateur pour les connexions classiques.
    """
    pass


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptateur qui gère la connexion Google/Sociale.
    Il connecte automatiquement un compte Google à un utilisateur local existant,
    si les emails correspondent (et si l'email Google est vérifié).
    """

    def pre_social_login(self, request, sociallogin):

        email = sociallogin.user.email

        # 1. Vérification minimale
        if not email:
            messages.error(request, "Google n'a pas pu fournir votre adresse email.")
            raise ImmediateHttpResponse(redirect('/comptes/login/'))

        is_verified = sociallogin.account.extra_data.get('verified_email', False)
        if not is_verified:
            # Ne pas faire confiance à un email non vérifié par Google
            return

        # 2. On cherche si un utilisateur local AVEC CET EMAIL existe
        User = get_user_model()
        try:
            existing_user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # L'utilisateur n'existe pas en local. On le laisse s'inscrire normalement.
            return

        # 3. L'utilisateur local (ex: le superuser) existe. On connecte les deux comptes.
        #    Ceci empêche la page de conflit "Sign Up" d'apparaître.
        sociallogin.connect(request, existing_user)

        # On peut optionally ajouter un message de succès (cela sera affiché à l'accueil)
        messages.success(request,
                         f"Connexion réussie ! Votre compte Google a été lié à votre compte {existing_user.email}.")

        # On coupe le flow d'inscription et on redirige directement
        raise ImmediateHttpResponse(redirect('blog:liste-articles'))