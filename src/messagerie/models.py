from django.db import models
from django.conf import settings


class Message(models.Model):
    # Qui envoie ? (Peut être vide si c'est un visiteur non inscrit via le formulaire de contact)
    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages_envoyes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Pour les visiteurs non inscrits (Formulaire de contact)
    nom_guest = models.CharField(max_length=100, blank=True, help_text="Nom si non inscrit")
    email_guest = models.EmailField(blank=True, help_text="Email si non inscrit")

    # Qui reçoit ? (Obligatoire)
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages_recus',
        on_delete=models.CASCADE
    )

    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']  # Les plus récents en premier

    def __str__(self):
        sender = self.expediteur.pseudo if self.expediteur else self.email_guest
        return f"De {sender} à {self.destinataire}"