from django import forms
from .context_simulator import CONSTANTES_MPP


class GlobalSimulationForm(forms.Form):
    # On définit les champs modifiables
    rdc_actif = forms.IntegerField(
        label="RDC Actif (Net/Mois)",
        initial=CONSTANTES_MPP['RDC_ACTIF'],
        min_value=0, max_value=2000,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
    rdc_enfant = forms.IntegerField(
        label="RDC Enfant",
        initial=CONSTANTES_MPP['RDC_ENFANT'],
        min_value=0, max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
    rdc_retraite = forms.IntegerField(
        label="RDC Retraité (Bonus)",
        initial=CONSTANTES_MPP['RDC_RETRAITE_BONUS'],
        min_value=0, max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
    rdc_etudiant = forms.IntegerField(
        label="RDC Étudiant",
        initial=CONSTANTES_MPP['RDC_ETUDIANT'],
        min_value=0, max_value=1500,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
    rdc_parent_isole = forms.IntegerField(
        label="Bonus Parent Isolé",
        initial=CONSTANTES_MPP['RDC_PARENT_ISOLE'],
        min_value=0, max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
    rdc_handicap = forms.IntegerField(
        label="RDC Handicap Total",
        initial=CONSTANTES_MPP['RDC_HANDICAP_TOTAL'],
        min_value=0, max_value=3000,
        widget=forms.NumberInput(attrs={'class': 'input-simu'})
    )
