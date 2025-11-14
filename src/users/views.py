from django.shortcuts import render
# On importe la vue de connexion "prête à l'emploi" de Django
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required  # Pour la sécurité
from django.contrib import messages  # Pour les messages de succès
# On importe notre formulaire personnalisé
from .forms import UserLoginForm, UserRegisterForm, UserProfileForm


# --- VUE DE CONNEXION ---
class UserLoginView(LoginView):
    """
    On utilise la vue de connexion de Django, mais en
    lui disant d'utiliser notre formulaire personnalisé.
    """

    # 1. On pointe vers notre formulaire
    form_class = UserLoginForm

    # 2. On lui dit quel template HTML utiliser (on va le créer)
    template_name = 'users/login.html'

    # 3. (Bonus) Si un utilisateur déjà connecté essaie
    # d'aller sur /login, on le redirige.
    redirect_authenticated_user = True

    # (La redirection après succès sera gérée par settings.py)


# --- VUE DE D'INSCRIPTION ---
def register_view(request):
    """
    Vue "fonction" qui gère l'inscription.
    """

    # On vérifie si la requête est en POST (soumission du formulaire)
    if request.method == 'POST':
        # Si oui, on crée une instance du formulaire AVEC les données envoyées (request.POST)
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            # Le formulaire est valide !
            # 1. Il vérifie les mots de passe
            # 2. Il hashe le mot de passe
            # 3. Il sauvegarde le nouvel utilisateur
            user = form.save()

            # --- NOTRE ACCUEIL ---
            # On connecte le nouvel utilisateur directement
            login(request, user)

            # On le redirige vers l'accueil du blog
            return redirect('blog:liste-articles')

        # Si le formulaire n'est PAS valide (ex: email existe déjà, mdp trop court),
        # le 'form' contient maintenant les erreurs.
        # On ne fait rien et on "tombe" vers le 'render' en bas.

    else:
        # Si c'est une requête GET (simple visite de la page),
        # on crée un formulaire vide.
        form = UserRegisterForm()

    # On prépare le contexte
    context = {
        'form': form
    }
    # Et on affiche le template (soit avec le form vide,
    # soit avec le form rempli d'erreurs)
    return render(request, 'users/register.html', context)


@login_required  # <-- LE GARDE DU CORPS
def profile_view(request):
    """
    Affiche le profil de l'utilisateur connecté et
    permet de le mettre à jour.
    """

    # On récupère l'utilisateur connecté
    user = request.user

    # Logique de soumission (POST)
    if request.method == 'POST':
        # On crée un formulaire AVEC les données envoyées (request.POST) ET les fichiers envoyés (request.FILES) ->
        # important pour la photo ! ET on le lie à l'instance de l'utilisateur (instance=user) pour que Django sache
        # qu'on MODIFIE, et qu'on ne CRÉE PAS.
        form = UserProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()  # Enregistre les modifs dans la BDD

            # C'est bien de confirmer que ça a marché.
            messages.success(request, 'Votre profil a été mis à jour avec succès !')

            # On redirige vers la MÊME page
            return redirect('users:profile')

        # Si le formulaire n'est pas valide, on "tombe" vers le 'render'
        # en bas, et 'form' contiendra les erreurs.

    # Logique d'affichage (GET)
    else:
        # On crée un formulaire pré-rempli avec les
        # infos de l'utilisateur (instance=user).
        form = UserProfileForm(instance=user)

    # On prépare le contexte
    context = {
        'form': form
    }

    return render(request, 'users/profile.html', context)


# =============================================================================
#                       SUPPRESSION DE COMPTE
# =============================================================================

@login_required  # Sécurité avant tout !
def profile_delete_view(request):
    """
    Gère l'affichage de la page de confirmation
    ET la suppression réelle du compte (si POST).
    """

    # On récupère l'utilisateur à supprimer
    user_to_delete = request.user

    # Si l'utilisateur clique sur le bouton "CONFIRMER"
    if request.method == 'POST':
        # 1. On sauvegarde le nom pour le message d'adieu
        user_pseudo = user_to_delete.pseudo or user_to_delete.email

        # 2. On déconnecte l'utilisateur AVANT de le supprimer
        #    C'est plus propre pour la session.
        logout(request)

        # 3. ON SUPPRIME L'UTILISATEUR (L'action irréversible)
        user_to_delete.delete()

        # 4. On affiche un message sur la *prochaine* page
        messages.success(request, f"Le compte de {user_pseudo} a été supprimé avec succès. Au revoir !")

        # 5. On redirige vers l'accueil
        return redirect('blog:liste-articles')

    # Si c'est une requête GET (simple visite),
    # on affiche simplement la page de confirmation.
    return render(request, 'users/profile_delete_confirm.html')