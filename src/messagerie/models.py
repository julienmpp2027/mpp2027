from django.db import models
from django.conf import settings


class Message(models.Model):
    # ... (vos champs existants : expediteur, destinataire, sujet, contenu...) ...
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_envoyes', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_recus', on_delete=models.CASCADE)
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    # champs invités
    nom_guest = models.CharField(max_length=100, blank=True)
    email_guest = models.EmailField(blank=True)

    # --- AJOUT POUR LE FIL DE DISCUSSION ---
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reponses'
    )

    class Meta:
        # On trie par date d'envoi pour avoir les discussions dans l'ordre
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.sujet}"

    def get_last_message_date(self):
        """
        Retourne la date du message le plus récent du fil de discussion
        (soit le message lui-même, soit sa dernière réponse).
        """
        last_reponse = self.reponses.all().order_by('-date_envoi').first()
        if last_reponse:
            return last_reponse.date_envoi
        return self.date_envoi

    def is_thread_unread(self, user):
        """
        Retourne Vrai si le fil contient au moins un message non lu DESTINÉ à 'user'.
        """
        # 1. Est-ce que le message racine est pour moi et non lu ?
        if self.destinataire == user and not self.lu:
            return True

        # 2. Est-ce qu'une des réponses est pour moi et non lue ?
        # (Note: dans une réponse, le destinataire est celui qui reçoit la notif)
        if self.reponses.filter(destinataire=user, lu=False).exists():
            return True

        return False