from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class MyAccountAdapter(DefaultAccountAdapter):
    """
    On garde cet adaptateur pour les réglages du compte local.
    (On n'en a pas besoin pour l'instant).
    """
    pass


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    C'est ici qu'on gère la connexion sociale.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Cette fonction est appelée juste après une connexion Google
        réussie, mais AVANT que Django ne crée ou ne connecte
        l'utilisateur.
        """
        if not sociallogin.user.email:
            messages.error(request, "Google n'a pas fourni votre adresse email. Veuillez contacter le support.")
            raise ImmediateHttpResponse(redirect('/comptes/login/'))
        # 1. On récupère l'email de Google
        # (il est dans sociallogin.user.email)
        email = sociallogin.user.email

        if not email:
            # Pas d'email ? On laisse allauth gérer le problème.
            return

        # 2. On vérifie que Google a bien VÉRIFIÉ cet email
        is_verified = sociallogin.account.extra_data.get('verified_email', False)
        if not is_verified:
            # Si non vérifié, on ne fait pas confiance.
            return

        # 3. On cherche si un utilisateur LOCAL (votre superuser)
        #    existe déjà avec cet email.
        User = get_user_model()  # C'est notre CustomUser
        try:
            existing_user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Pas d'utilisateur local ? Parfait.
            # On laisse allauth continuer son flux normal
            # (qui va créer un nouvel utilisateur).
            return

        # 4. LE CAS MAGIQUE :
        # On a trouvé un utilisateur local (existing_user) !

        # On vérifie si ce compte Google est déjà lié à quelqu'un
        if sociallogin.is_existing:
            # C'est juste un login normal. On ne fait rien.
            return

        # 5. C'est le cas de votre screenshot :
        # L'email existe localement, mais ce compte Google
        # n'est pas encore lié. On les connecte de force !
        sociallogin.connect(request, existing_user)

class MyAccountAdapter(DefaultAccountAdapter):
    pass  # On le remplira plus tard si besoin


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    pass  # On le remplira plus tard si besoin
