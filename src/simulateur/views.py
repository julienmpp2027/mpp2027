from django.shortcuts import render
from django.http import JsonResponse
from .regles_retraite import calculer_pension_complete, CONSTANTES

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
