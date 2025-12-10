from django import forms
from .context_simulator import DEFAUT_MPP, CONSTANTES_CHARGES


class SimulateurRDCForm(forms.Form):
    # Nous utilisons des champs "NumberInput" stylisés
    # Les labels correspondent aux colonnes de votre tableau PDF

    rdc_actif = forms.IntegerField(
        label="Adulte Actif (Socle)",
        initial=DEFAUT_MPP['RDC_ACTIF'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    rdc_enfant = forms.IntegerField(
        label="Enfant (Universel)",
        initial=DEFAUT_MPP['RDC_ENFANT'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    rdc_retraite = forms.IntegerField(
        label="Retraité (Bonus)",
        initial=DEFAUT_MPP['RDC_RETRAITE'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    rdc_etudiant = forms.IntegerField(
        label="Étudiant (RUE)",
        initial=DEFAUT_MPP['RDC_ETUDIANT'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    rdc_parent_isole = forms.IntegerField(
        label="Bonus Parent Isolé",
        initial=DEFAUT_MPP['RDC_PARENT_ISOLE'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    rdc_handicap = forms.IntegerField(
        label="Complément Handicap",
        initial=DEFAUT_MPP['RDC_HANDICAP_COMPLEMENT'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    filet_securite = forms.DecimalField(
        label="Filet Sécurité (Mds €)",
        initial=DEFAUT_MPP['FILET_SECURITE'],
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'simu-input', 'step': '0.1'})
    )


class SimulateurChargesForm(forms.Form):
    # TRANCHE 1
    t1_taux = forms.IntegerField(
        label="Taux Tranche 1 (%)",
        initial=CONSTANTES_CHARGES['T1_TAUX'],  # Sera 6
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    t1_limit = forms.FloatField(
        label="Limite Tranche 1 (x SMIC)",
        initial=CONSTANTES_CHARGES['T1_LIMIT'],  # Sera 1.2
        widget=forms.NumberInput(attrs={'class': 'simu-input', 'step': '0.1'})
    )

    # TRANCHE 2 (Solidarité)
    t2_taux = forms.IntegerField(
        label="Taux Tranche 2 (%)",
        initial=CONSTANTES_CHARGES['T2_TAUX'],  # Sera 30
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    t2_limit = forms.FloatField(
        label="Limite Tranche 2 (x SMIC)",
        initial=CONSTANTES_CHARGES['T2_LIMIT'],  # Sera 2.5
        widget=forms.NumberInput(attrs={'class': 'simu-input', 'step': '0.1'})
    )

    # TRANCHE 3
    t3_taux = forms.IntegerField(
        label="Taux Tranche 3 (%)",
        initial=CONSTANTES_CHARGES['T3_TAUX'],  # Sera 42
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )


class SimulateurTVAForm(forms.Form):
    taux_normal = forms.IntegerField(
        label="Taux Normal (%)",
        initial=26,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )
    taux_reduit = forms.IntegerField(
        label="Taux Réduit / Inter. (%)",
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'simu-input'})
    )

    # Niches (Checkboxes)
    suppress_restau = forms.BooleanField(
        label="Supprimer Taux Réduit Restauration",
        required=False,
        initial=True,  # Coché par défaut
        widget=forms.CheckboxInput(attrs={'class': 'simu-checkbox'})
    )
    suppress_batiment = forms.BooleanField(
        label="Supprimer Taux Réduit Bâtiment",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'simu-checkbox'})
    )