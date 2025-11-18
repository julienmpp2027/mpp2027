from django.urls import path, reverse_lazy
# On importe notre vue de connexion personnalisée
from .views import UserLoginView, register_view, profile_view, profile_delete_view
from .forms import UserPasswordResetForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # On définit l'URL pour la connexion
    path('login/', UserLoginView.as_view(), name='login'),
    # On définit l'URL pour la déconnexion
    path('logout/', LogoutView.as_view(), name='logout'),
    # On définit l'URL pour l'inscription
    path('register/', register_view, name='register'),
    # On définit l'URL pour la suppression du compte.
    path('profil/supprimer/', profile_delete_view, name='profile-delete'),

    # -------------- MDP OUBLIE --------------------------
    # Formulaire oubli du mdp
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset_form.html',
             email_template_name='users/password_reset_email.html',
             form_class=UserPasswordResetForm,
             success_url=reverse_lazy('users:password_reset_done'),
         ),
         name='password_reset'),
    # La page "Email envoyé"
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    # Le lien dans l'email (capture l'email et le token)
    # <uidb64> et <token> sont des codes magiques gérés par Django
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete'),
         ),
         name='password_reset_confirm'),

    # La page "C'est bon, c'est changé"
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    # ----------------------------------------------------------------------------------------------------------
    path('profil/', profile_view, name='profile'),
]
