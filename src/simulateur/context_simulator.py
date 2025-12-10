"""
CONTEXTE GLOBAL DE SIMULATION - MPP 2027
Ce fichier contient la logique de calcul budgétaire pour le simulateur global.
"""

# ==============================================================================
# 1. DONNÉES DÉMOGRAPHIQUES (CONSTANTES DE STRUCTURE)
# ==============================================================================

# ########   DEMOGRAPHIE  # ########
DEMOGRAPHIE = {
    "NB_ADULTES_ELIGIBLES": 34_600_000,  # actifs et personne de 18 à 67 ans hors étudiant
    "NB_ENFANTS": 14_000_000,
    "NB_RETRAITES": 17_000_000,
    "NB_ETUDIANTS": 2_970_000,
    "NB_PARENTS_ISOLES": 1_700_000,
    "NB_HANDICAPES": 1_200_000,  # (ancien AAH)
    "NB_SALARIES_PRIVE": 20_000_000,

}
# AJOUT : Calcul automatique de la Population Totale (Eligibles + Enfants + Etudiants + Retraités)
DEMOGRAPHIE["POPULATION_TOTALE"] = (
        DEMOGRAPHIE["NB_ADULTES_ELIGIBLES"] +
        DEMOGRAPHIE["NB_ENFANTS"] +
        DEMOGRAPHIE["NB_ETUDIANTS"] +
        DEMOGRAPHIE["NB_RETRAITES"]
)

# ########   AIDES SOCIALE ACTUELLE REMPLACE PAR RDC  # ########

AIDES_SOCIALES_SUPPRIMES = {
    "RSA (Revenu de Solidarité Active)": 16.5,
    "Prime d'Activité": 11.5,
    "Aides au Logement (APL, ALS, ALF)": 16.0,
    "AAH (Allocation Adulte Handicapé)": 13.0,
    "Ensemble Prestations Familiales (AF, ARS, PAJE, Complément familial)": 43.0,
    "ASPA (Minimum Vieillesse)": 5.0,
    "ASS (Allocation de Solidarité Spécifique - Chômage fin de droits)": 2.5,
    "Bourses étudiantes & Aides au logement étudiant": 3.0,
    "Autres dispositifs solidarité (Aides départements, etc.)": 1.5
}

AIDES_SOCIALES_SUPPRIMES["ECONOMIE_TOTALE"] = sum(AIDES_SOCIALES_SUPPRIMES.values())  # environ 112 milliards

# ########   NICHES FISCALE ACTUELLE   # ########

# Dictionnaire des Niches Fiscales Actuelles (Estimation PLF 2024)
# Montants en Milliards d'euros
# Total approximatif : ~88 Milliards d'euros

NICHES_FISCALES_ACTUELLES = {
    # --- CE QUE TU CONSERVES (SANCTUARISÉ) ---
    "CIR (Crédit Impôt Recherche)": 7.5,  # Tu le gardes ou le transformes en amortissement dynamique

    # Détail Outre-Mer (DOM-TOM) - Total ~6.5 Mds
    "DOM-TOM - TVA Réduite Spécifique": 1.9,  # Tu conserves explicitement ceci
    "DOM-TOM - Réduction Impôt Investissement (Girardin, etc.)": 1.6,
    "DOM-TOM - Abattement 30/40% Impôt sur le Revenu": 2.5,  # Avantage fiscal résidents
    "DOM-TOM - Exonérations diverses entreprises": 0.5,

    # --- CE QUE TU SUPPRIMES (POUR FINANCER LE RDC + BAISSE CHARGES) ---

    # Le "Gros Morceau" des ménages
    "Abattement 10% frais professionnels (Salariés & Retraités)": 24.0,
    # Tu supprimes ceci explicitement dans le programme
    "Crédit Impôt Emploi à Domicile (50%)": 6.0,  # Supprimé et compensé par le RDC
    "Exonération fiscale des Heures Supplémentaires": 2.2,  # Supprimé
    "Dons aux associations (Réduction IR)": 1.8,  # Supprimé (Redevient un don pur)

    # TVA Taux Réduits (HORS Dom-Tom)
    "TVA 10% Restauration & Hôtellerie": 5.6,  # Remontée au taux standard ou 26%
    "TVA 10% Travaux rénovation logement": 4.8,
    "TVA 5.5% Rénovation énergétique": 1.4,

    # Fiscalité du Capital & Entreprises (Hors CIR)
    "Taux réduit IS pour PME (15% au lieu de 25%)": 2.5,
    "Exonération épargne salariale (Participation/Intéressement)": 9.0,  # Niche sociale/fiscale
    "Dispositifs Immobiliers (Pinel, Denormandie, PTZ...)": 2.5,
    "Assurance Vie (Abattements succession/rachat)": 3.0,
    "Pacte Dutreil (Transmission entreprises)": 3.0,

    # Niches "Grises" ou sectorielles (Carburants, etc.)
    "Niches sur TICPE (Carburant Agri, BTP, Taxis...)": 6.8,
    "Autres crédits d'impôts entreprises (Mécénat, jeux vidéo, etc.)": 2.5,
    "Exonération prestations familiales (Non imposition des allocs)": 0.0
    # Note: Techniquement une niche mais pas chiffrée car "logique"
}

# Calculs pour vérification
total_niches = sum(NICHES_FISCALES_ACTUELLES.values())
dom_tom_total = sum(v for k, v in NICHES_FISCALES_ACTUELLES.items() if "DOM-TOM" in k)
cir_total = NICHES_FISCALES_ACTUELLES["CIR (Crédit Impôt Recherche)"]

# ==============================================================================
# 2. VALEURS PAR DÉFAUT DU PROGRAMME (PARAMÈTRES MODIFIABLES)
# ==============================================================================
DEFAUT_MPP = {
    # CHAPITRE 1 : RDC
    "RDC_ACTIF": 450,
    "RDC_ENFANT": 325,
    "RDC_RETRAITE": 150,
    "RDC_ETUDIANT": 750,
    "RDC_PARENT_ISOLE": 300,  # Bonus
    "RDC_HANDICAP_COMPLEMENT": 750,  # Complément pour atteindre 1200 (450+750)
    "FILET_SECURITE": 12.0,  # En Milliards (fixe)
}

# ==============================================================================
# DONNÉES SALARIALES (POUR CHAPITRE 2)
# ==============================================================================
# Répartition simplifiée de la masse salariale du privé (20 Millions salariés)

DISTRIBUTION_SALAIRES = [
    {'mult': 1.0, 'percent': 0.17},  # SMIC
    {'mult': 1.2, 'percent': 0.15},
    {'mult': 1.4, 'percent': 0.15},
    {'mult': 1.6, 'percent': 0.12},
    {'mult': 2.0, 'percent': 0.15},
    {'mult': 2.5, 'percent': 0.10},
    {'mult': 3.5, 'percent': 0.08},  # Cadres
    {'mult': 5.0, 'percent': 0.05},  # Dirigeants
    {'mult': 8.0, 'percent': 0.03},
]

CONSTANTES_CHARGES = {
    "SMIC_BRUT_2025": 1800,
    # Paramètres par défaut MPP (tels que définis dans le programme)
    "T1_TAUX": 6,  # 6%
    "T1_LIMIT": 1.2,  # Jusqu'à 1.2 SMIC
    "T2_TAUX": 30,  # 30%
    "T2_LIMIT": 2.5,  # Jusqu'à 2.5 SMIC
    "T3_TAUX": 42  # 42% au-delà
}

COEFF_CALIBRAGE_MASSE = 0.82

# ==============================================================================
# DONNÉES TVA (POUR CHAPITRE 3)
# ==============================================================================
# Bases de consommation annuelles estimées (en Milliards €) pour calibrer ~190 Md€ de recettes
CONSTANTES_TVA = {
    "BASE_NORMALE": 720.0,  # Soumis à 20% (Habits, High-Tech, Services...)
    "BASE_INTER": 180.0,  # Soumis à 10% (Restauration, Bâtiment, Transports)
    "BASE_REDUITE": 280.0,  # Soumis à 5.5% (Alimentation, Énergie partiel)

    # Coût estimé des niches (Base x Différentiel de taux)
    "BASE_NICHE_RESTAU": 55.0,  # Estimation consommation restauration
    "BASE_NICHE_BAT": 40.0,  # Estimation travaux rénovation
}


# ==============================================================================
# 3. FONCTIONS DE CALCUL
# ==============================================================================

def calculer_cout_rdc(params):
    """
    Calcule le coût du Chapitre 1 (RDC) en fonction des montants entrés par l'utilisateur.
    Retourne un dictionnaire avec le détail et le total en Milliards.
    """
    # On récupère les montants (ou ceux par défaut si absents)
    m_actif = params.get('rdc_actif', DEFAUT_MPP["RDC_ACTIF"])
    m_enfant = params.get('rdc_enfant', DEFAUT_MPP["RDC_ENFANT"])
    m_retraite = params.get('rdc_retraite', DEFAUT_MPP["RDC_RETRAITE"])
    m_etudiant = params.get('rdc_etudiant', DEFAUT_MPP["RDC_ETUDIANT"])
    m_isole = params.get('rdc_parent_isole', DEFAUT_MPP["RDC_PARENT_ISOLE"])
    m_handicap = params.get('rdc_handicap', DEFAUT_MPP["RDC_HANDICAP_COMPLEMENT"])
    m_filet = params.get('filet_securite', DEFAUT_MPP["FILET_SECURITE"])

    # Calcul des sous-totaux (Population * Montant * 12 mois) / 1 Milliard
    couts = {
        'actifs': (DEMOGRAPHIE["NB_ADULTES_ELIGIBLES"] * m_actif * 12) / 1e9,
        'enfants': (DEMOGRAPHIE["NB_ENFANTS"] * m_enfant * 12) / 1e9,
        'retraites': (DEMOGRAPHIE["NB_RETRAITES"] * m_retraite * 12) / 1e9,
        'etudiants': (DEMOGRAPHIE["NB_ETUDIANTS"] * m_etudiant * 12) / 1e9,
        'isoles': (DEMOGRAPHIE["NB_PARENTS_ISOLES"] * m_isole * 12) / 1e9,
        'handicap': (DEMOGRAPHIE["NB_HANDICAPES"] * m_handicap * 12) / 1e9,
        'filet_securite': float(m_filet)  # On utilise la valeur dynamique
    }

    # Total
    total = sum(couts.values())

    return {
        'details': couts,
        'total': round(total, 2)
    }


def _calculer_cout_salarie(salaire_brut, params, smic):
    """
    Fonction utilitaire qui calcule les coûts pour UN salarié donné.
    Retourne : {cout_actuel, cout_mpp, charges_mpp}
    """
    # Paramètres MPP
    t1_taux = (params.get('t1_taux') if params.get('t1_taux') is not None else 6) / 100
    t1_lim = (params.get('t1_limit') if params.get('t1_limit') is not None else 1.2) * smic

    t2_taux = (params.get('t2_taux') if params.get('t2_taux') is not None else 30) / 100
    t2_lim = (params.get('t2_limit') if params.get('t2_limit') is not None else 2.5) * smic

    t3_taux = (params.get('t3_taux') if params.get('t3_taux') is not None else 42) / 100

    # --- 1. SYSTÈME ACTUEL (Approximation Fillon lissée) ---
    if salaire_brut <= smic:
        taux_actuel = 0.04
    elif salaire_brut <= 1.6 * smic:
        taux_actuel = 0.04 + (0.28 * (salaire_brut - smic) / (0.6 * smic))
    elif salaire_brut <= 2.5 * smic:
        taux_actuel = 0.32 + (0.10 * (salaire_brut - 1.6 * smic) / (0.9 * smic))
    else:
        taux_actuel = 0.42

    charges_actuelles = salaire_brut * taux_actuel
    cout_actuel = salaire_brut + charges_actuelles

    # --- 2. SYSTÈME MPP (Marginal) ---
    charges_mpp = 0
    # T1
    base_t1 = min(salaire_brut, t1_lim)
    charges_mpp += base_t1 * t1_taux
    # T2
    if salaire_brut > t1_lim:
        base_t2 = min(salaire_brut, t2_lim) - t1_lim
        charges_mpp += base_t2 * t2_taux
    # T3
    if salaire_brut > t2_lim:
        base_t3 = salaire_brut - t2_lim
        charges_mpp += base_t3 * t3_taux

    cout_mpp = salaire_brut + charges_mpp

    return {
        'brut': salaire_brut,
        'cout_actuel': cout_actuel,
        'cout_mpp': cout_mpp,
        'charges_mpp': charges_mpp,
        'taux_effectif_mpp': (charges_mpp / salaire_brut) * 100 if salaire_brut > 0 else 0
    }


def calculer_charges_sociales(params):
    """
    Calcule le budget global ET les profils types.
    """
    smic = CONSTANTES_CHARGES["SMIC_BRUT_2025"]
    nb_salaries = DEMOGRAPHIE["NB_SALARIES_PRIVE"]

    recettes_theoriques = 0
    recettes_reelles_actuelles = 0
    recettes_mpp = 0

    # 1. CALCUL GLOBAL (Budget)
    for segment in DISTRIBUTION_SALAIRES:
        salaire = segment['mult'] * smic
        nb_gens = segment['percent'] * nb_salaries * COEFF_CALIBRAGE_MASSE

        # On utilise notre fonction utilitaire
        res = _calculer_cout_salarie(salaire, params, smic)

        # Agrégation (Attention, _calculer_cout_salarie renvoie des montants mensuels)
        recettes_theoriques += (salaire * 0.42) * nb_gens * 12
        recettes_reelles_actuelles += (res['cout_actuel'] - salaire) * nb_gens * 12
        recettes_mpp += res['charges_mpp'] * nb_gens * 12

    # 2. CALCUL DU "DÉGRÈVEMENT MAX" (Avantage annuel pour un haut salaire)
    # C'est la différence entre payer 42% sur tout le salaire (Théorique) et payer le tarif MPP
    # pour un salaire qui dépasse la T2 (donc qui a bénéficié de tous les allègements possibles)

    # On prend un salaire fictif très haut pour saturer les tranches
    salaire_max = 10 * smic
    res_max = _calculer_cout_salarie(salaire_max, params, smic)

    charges_theo_max = salaire_max * 0.42
    charges_mpp_max = res_max['charges_mpp']
    # Gain mensuel par rapport au taux plein de 42%
    gain_mensuel_max = charges_theo_max - charges_mpp_max

    # 3. CALCUL DES PROFILS TYPES
    profils_def = [
        {'label': 'SMIC', 'mult': 1.0},
        {'label': 'Qualifié (1.5 SMIC)', 'mult': 1.5},
        {'label': 'Technicien (2.0 SMIC)', 'mult': 2.0},
        {'label': 'Cadre (3.5 SMIC)', 'mult': 3.5},
        {'label': 'Dirigeant (5.0 SMIC)', 'mult': 5.0},
    ]

    profils_data = []
    for p in profils_def:
        s = p['mult'] * smic
        r = _calculer_cout_salarie(s, params, smic)
        profils_data.append({
            'label': p['label'],
            'salaire_brut': round(s),
            'cout_actuel': round(r['cout_actuel']),
            'cout_mpp': round(r['cout_mpp']),
            'gain': round(r['cout_actuel'] - r['cout_mpp']),
            'taux_eff': round(r['taux_effectif_mpp'], 1)
        })

    # Totaux en Milliards
    total_theo = round(recettes_theoriques / 1e9, 1)
    total_reel = round(recettes_reelles_actuelles / 1e9, 1)
    allegements = round(total_theo - total_reel, 1)
    total_mpp = round(recettes_mpp / 1e9, 1)
    impact = round(total_mpp - total_reel, 1)

    return {
        'recettes_theoriques': total_theo,
        'allegements_actuels': allegements,
        'recettes_actuelles': total_reel,
        'recettes_mpp': total_mpp,
        'total': impact,
        # Nouveaux champs
        'gain_max_annuel': round(gain_mensuel_max * 12),
        'profils': profils_data
    }


def calculer_recettes_tva(params):
    """
    Calcule les recettes de TVA Actuelles vs MPP en fonction des taux choisis.
    """
    # 1. Taux Utilisateur (ou défaut MPP : 26% et 10%)
    t_norm_mpp = (params.get('taux_normal') if params.get('taux_normal') is not None else 26) / 100
    t_red_mpp = (params.get('taux_reduit') if params.get('taux_reduit') is not None else 10) / 100

    # On met la valeur par défaut à True pour qu'elle corresponde aux cases cochées du formulaire.
    suppress_restau = params.get('suppress_restau', True)
    suppress_batiment = params.get('suppress_batiment', True)

    # --- A. SITUATION ACTUELLE (20% / 10% / 5.5%) ---
    # Recette = Base * Taux
    recette_actuelle = (
            CONSTANTES_TVA["BASE_NORMALE"] * 0.20 +
            CONSTANTES_TVA["BASE_INTER"] * 0.10 +
            CONSTANTES_TVA["BASE_REDUITE"] * 0.055
    )

    # --- B. SITUATION PROJETÉE (MPP) ---
    # Gestion des bascules de base (Niches)
    base_normale_mpp = CONSTANTES_TVA["BASE_NORMALE"]
    base_reduite_mpp = CONSTANTES_TVA["BASE_REDUITE"] + CONSTANTES_TVA[
        "BASE_INTER"]  # Par défaut l'inter passe au réduit (10%)

    # Si on supprime la niche Restau, elle sort du réduit pour aller au normal
    if suppress_restau:
        base_reduite_mpp -= CONSTANTES_TVA["BASE_NICHE_RESTAU"]
        base_normale_mpp += CONSTANTES_TVA["BASE_NICHE_RESTAU"]

    # Idem Bâtiment
    if suppress_batiment:
        base_reduite_mpp -= CONSTANTES_TVA["BASE_NICHE_BAT"]
        base_normale_mpp += CONSTANTES_TVA["BASE_NICHE_BAT"]

    recette_mpp = (
            base_normale_mpp * t_norm_mpp +
            base_reduite_mpp * t_red_mpp
    )

    # --- C. INDICATEURS CLÉS ---
    gain_total = recette_mpp - recette_actuelle

    # Rendement du point de TVA (Moyenne lissée)
    # Total Base ~ 1180 Md€. 1% = 11.8 Md€ théorique.
    # En pratique, on divise la recette par le taux moyen.
    rendement_point = recette_mpp / ((t_norm_mpp * 0.65 + t_red_mpp * 0.35) * 100)

    # --- D. PROFILS TYPES (Impact Pouvoir d'Achat) ---
    # On estime la part du revenu consommée soumise à TVA
    profils_tva = []
    defs_profils = [
        {'nom': 'SMIC', 'net': 1400, 'propension': 1.0, 'part_necessite': 0.6},  # Conso 100%, 60% produits vitaux
        {'nom': 'Moyen', 'net': 2500, 'propension': 0.9, 'part_necessite': 0.5},
        {'nom': 'Aisé', 'net': 4000, 'propension': 0.8, 'part_necessite': 0.4},
        {'nom': 'Cadre Sup', 'net': 6000, 'propension': 0.7, 'part_necessite': 0.3},
        {'nom': 'Riche', 'net': 10000, 'propension': 0.5, 'part_necessite': 0.25},
    ]

    for p in defs_profils:
        budget_conso = p['net'] * p['propension']

        # Panier Actuel
        # Mix simplifié : Part nécessité à 5.5%, le reste à 20% (ignorant le 10% pour simplifier le profil)
        tva_payee_actuel = budget_conso * (p['part_necessite'] * 0.055 + (1 - p['part_necessite']) * 0.20)

        # Panier MPP
        # Nécessité passe au Taux Réduit choisi (ex: 10%), le reste au Normal (ex: 26%)
        tva_payee_mpp = budget_conso * (p['part_necessite'] * t_red_mpp + (1 - p['part_necessite']) * t_norm_mpp)

        surcout = tva_payee_mpp - tva_payee_actuel

        profils_tva.append({
            'nom': p['nom'],
            'net': p['net'],
            'surcout': round(surcout),
            'part_revenu': round((surcout / p['net']) * 100, 1)
        })

    return {
        'recette_actuelle': round(recette_actuelle, 1),
        'recette_mpp': round(recette_mpp, 1),
        'total': round(gain_total, 1),
        'point_tva': round(rendement_point, 1),
        'profils': profils_tva,
        # Pour affichage des coûts niches
        'cout_niche_restau': round(CONSTANTES_TVA["BASE_NICHE_RESTAU"] * (t_norm_mpp - t_red_mpp), 1),
        'cout_niche_bat': round(CONSTANTES_TVA["BASE_NICHE_BAT"] * (t_norm_mpp - t_red_mpp), 1)
    }