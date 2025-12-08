from django.shortcuts import render
from django.http import JsonResponse
from .regles_retraite import calculer_pension_complete, CONSTANTES
from .forms import GlobalSimulationForm
from .context_simulator import DEMOGRAPHIE, CONSTANTES_MPP

def accueil(request):
    """Page hub qui liste les simulateurs disponibles"""
    return render(request, 'simulateur/accueil.html')


def index(request):
    # On passe toujours les constantes pour l'affichage statique (textes d'aide)
    return render(request, 'simulateur/retraite.html', {'config': CONSTANTES})


def api_calcul(request):
    """
    API appelée par le JavaScript en AJAX.
    Elle récupère les paramètres GET, lance le calcul Python et renvoie du JSON.
    """
    try:
        # Récupération et conversion des paramètres (avec valeurs par défaut)
        salaire = float(request.GET.get('salaire', 2000))
        annees = float(request.GET.get('annees', 43))
        enfants = int(request.GET.get('enfants', 0))
        penibilite = float(request.GET.get('penibilite', 0))
        age_depart = int(request.GET.get('age_depart', 64))

        # Appel du fichier de règles
        resultats = calculer_pension_complete(
            salaire, annees, enfants, penibilite, age_depart
        )

        return JsonResponse(resultats)

    except ValueError:
        return JsonResponse({'error': 'Données invalides'}, status=400)


# ... imports existants ...
from .regles_pouvoir_achat import calculer_pouvoir_achat, CONSTANTES_PA


# ... Vues existantes (Retraite) ...

# --- VUES POUVOIR D'ACHAT ---

def index_pa(request):
    """Affiche la page du simulateur PA"""
    return render(request, 'simulateur/pa_index.html', {'config': CONSTANTES_PA})


def api_calcul_pa(request):
    try:
        revenu = float(request.GET.get('revenu', 2000))
        adultes = int(request.GET.get('adultes', 1))
        enfants = int(request.GET.get('enfants', 0))
        conso = float(request.GET.get('conso', 90))

        # Nouveaux paramètres
        statut = request.GET.get('statut', 'actif')  # actif, retraite, etudiant
        parent_isole = request.GET.get('parent_isole') == 'true'

        resultats = calculer_pouvoir_achat(revenu, adultes, enfants, statut, parent_isole, conso)
        return JsonResponse(resultats)
    except ValueError:
        return JsonResponse({'error': 'Valeurs invalides'}, status=400)

########################################################################################################################
# ######################                      SIMULATEUR GLOBAL                  #######################################
########################################################################################################################


def simulateur_global(request):
    """
    Vue du Cockpit Budgétaire (Version 1 : Coûts uniquement).
    Permet de modifier les paramètres du RDC et de voir l'impact sur la dépense publique.
    """

    # 1. Initialisation du formulaire
    if request.method == 'POST':
        form = GlobalSimulationForm(request.POST)
    else:
        form = GlobalSimulationForm()

    # 2. Récupération des valeurs (Formulaire OU Constantes par défaut)
    if form.is_valid():
        data = form.cleaned_data
    else:
        # Valeurs par défaut du programme MPP 2027
        data = {
            'rdc_actif': CONSTANTES_MPP['RDC_ACTIF'],
            'rdc_enfant': CONSTANTES_MPP['RDC_ENFANT'],
            'rdc_retraite': CONSTANTES_MPP['RDC_RETRAITE_BONUS'],
            'rdc_etudiant': CONSTANTES_MPP['RDC_ETUDIANT'],
            'rdc_parent_isole': CONSTANTES_MPP['RDC_PARENT_ISOLE'],
            'rdc_handicap': CONSTANTES_MPP['RDC_HANDICAP_TOTAL'],
        }

    # 3. CALCUL DES DÉPENSES (En Milliards d'Euros)

    # Population cible Actifs (Adultes - Retraités - Etudiants)
    nb_actifs_eligibles = DEMOGRAPHIE["NB_ADULTES_TOTAL"] - DEMOGRAPHIE["NB_RETRAITES"] - DEMOGRAPHIE["NB_ETUDIANTS"]

    couts = {
        'actifs': (nb_actifs_eligibles * data['rdc_actif'] * 12) / 1e9,
        'enfants': (DEMOGRAPHIE["NB_ENFANTS"] * data['rdc_enfant'] * 12) / 1e9,
        'retraites': (DEMOGRAPHIE["NB_RETRAITES"] * data['rdc_retraite'] * 12) / 1e9,
        'etudiants': (DEMOGRAPHIE["NB_ETUDIANTS"] * data['rdc_etudiant'] * 12) / 1e9,

        # Estimation : 2 millions de parents isolés
        'parents_isoles': (2_000_000 * data['rdc_parent_isole'] * 12) / 1e9,

        # Surcoût Handicap (Total - Base Actif) pour 1.2M de personnes
        'handicap': (1_200_000 * (data['rdc_handicap'] - data['rdc_actif']) * 12) / 1e9,

        # Le filet de sécurité (12 Mds)
        'filet_zero_perdant': CONSTANTES_MPP['BUDGET_GARANTIE_ZERO_PERDANT']
    }

    total_depenses = sum(couts.values())

    # Context envoyé au template (Pas de recettes, pas de solde)
    context = {
        'form': form,
        'couts': couts,
        'total_depenses': round(total_depenses, 1),
    }

    return render(request, 'simulateur/global.html', context)