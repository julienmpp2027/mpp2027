from django.shortcuts import render
from django.http import JsonResponse
from .regles_retraite import calculer_pension_complete, CONSTANTES
from django import forms
from .forms import SimulateurRDCForm, SimulateurChargesForm
from .context_simulator import calculer_cout_rdc, calculer_charges_sociales, DEMOGRAPHIE


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


from .forms import SimulateurRDCForm, SimulateurChargesForm, SimulateurTVAForm
from .context_simulator import calculer_cout_rdc, calculer_charges_sociales, DEMOGRAPHIE, calculer_recettes_tva


def simulateur_global(request):
    # --- GESTION DU CHAPITRE 1 (RDC) ---
    # On regarde si le bouton "submit_rdc" a été cliqué
    if 'submit_rdc' in request.POST:
        form_rdc = SimulateurRDCForm(request.POST, prefix="rdc")
    else:
        # Sinon, on charge le formulaire avec les valeurs par défaut (initial)
        form_rdc = SimulateurRDCForm(prefix="rdc")

    data_rdc = {}
    if form_rdc.is_valid():
        data_rdc = form_rdc.cleaned_data

    # Calcul (utilise les données du form OU les défauts si form vide)
    res_rdc = calculer_cout_rdc(data_rdc)

    # --- GESTION DU CHAPITRE 2 (CHARGES) ---
    # On regarde si le bouton "submit_charges" a été cliqué
    if 'submit_charges' in request.POST:
        form_charges = SimulateurChargesForm(request.POST, prefix="charges")
    else:
        # Sinon, on charge le formulaire par défaut (ce qui règle le problème d'affichage)
        form_charges = SimulateurChargesForm(prefix="charges")

    data_charges = {}
    if form_charges.is_valid():
        data_charges = form_charges.cleaned_data

    res_charges = calculer_charges_sociales(data_charges)

    context = {
        'form_rdc': form_rdc,
        'res_rdc': res_rdc,
        'form_charges': form_charges,
        'res_charges': res_charges,
        'demo': DEMOGRAPHIE,
    }


    # 2. CHARGES (Chapitre 2)
    form_charges = SimulateurChargesForm(request.POST or None, prefix="charges")
    data_charges = {}
    if form_charges.is_valid(): data_charges = form_charges.cleaned_data
    res_charges = calculer_charges_sociales(data_charges)

    # Note : Pour les graphiques JS, on passera les valeurs par défaut au template
    # pour qu'il puisse dessiner la courbe initiale.

    context = {
        'form_rdc': form_rdc,
        'res_rdc': res_rdc,
        'form_charges': form_charges,
        'res_charges': res_charges,
        'demo': DEMOGRAPHIE,
    }


    # 3. TVA STRATÉGIQUE (NOUVEAU)
    if 'submit_tva' in request.POST:
        form_tva = SimulateurTVAForm(request.POST, prefix="tva")
    else:
        form_tva = SimulateurTVAForm(prefix="tva")

    data_tva = {}
    if form_tva.is_valid():
        data_tva = form_tva.cleaned_data

    res_tva = calculer_recettes_tva(data_tva)

    context = {
        'form_rdc': form_rdc,
        'res_rdc': res_rdc,
        'form_charges': form_charges,
        'res_charges': res_charges,
        'form_tva': form_tva,  # Nouveau
        'res_tva': res_tva,  # Nouveau
        'demo': DEMOGRAPHIE,
    }

    return render(request, 'simulateur/global.html', context)