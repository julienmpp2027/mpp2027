from django import forms
from .models import Message
from users.models import CustomUser

class MessageInterneForm(forms.ModelForm):
    # Un champ pour choisir le destinataire
    destinataire = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        label="À qui envoyer ?",
        widget=forms.Select(attrs={'class': 'form-control-large'})
    )

    class Meta:
        model = Message
        fields = ['destinataire', 'sujet', 'contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 5}),
        }