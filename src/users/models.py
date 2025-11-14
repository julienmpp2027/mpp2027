from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone


# -----------------------------------------------------------------------------
# 1. LE MANAGER : "Comment créer l'utilisateur"
# -----------------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    """
    Manager pour notre modèle CustomUser.
    On redéfinit create_user et create_superuser.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe.
        """
        if not email:
            raise ValueError("L'adresse email est obligatoire")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Important pour hacher le mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un super-utilisateur.
        """
        # Définit les champs par défaut pour un superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le super-utilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le super-utilisateur doit avoir is_superuser=True.')

        # On utilise create_user pour faire le travail
        return self.create_user(email, password, **extra_fields)


# -----------------------------------------------------------------------------
# 2. LE MODÈLE : "Qu'est-ce que l'utilisateur"
# -----------------------------------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle d'utilisateur personnalisé.
    Login par email.
    """
    # --- Champs requis par Django ---
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Définit si l'utilisateur peut se connecter au site d'administration."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Désactivez ceci au lieu de supprimer des comptes."
    )
    date_joined = models.DateTimeField(default=timezone.now)

    # --- Vos champs personnalisés ---
    pseudo = models.CharField(
        max_length=150,
        blank=True,
        help_text="Facultatif. Le pseudo affiché sur le site."
    )
    description = models.TextField(
        blank=True,
        max_length=500,
        help_text="Facultatif. Une courte description de vous-même."
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Facultatif. Votre photo de profil."
    )

    # --- Configuration ---
    objects = CustomUserManager()  # Dit à Django d'utiliser notre Manager

    USERNAME_FIELD = 'email'  # Définit 'email' comme champ de connexion
    REQUIRED_FIELDS = []  # Champs requis lors de 'createsuperuser' (aucun en plus de l'email/mdp)

    def __str__(self):
        return self.email

    # (PermissionsMixin s'occupe de is_superuser et des groupes/permissions)