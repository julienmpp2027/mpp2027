"""
CONTEXTE GLOBAL DE SIMULATION - MPP 2027
Ce fichier contient toutes les constantes macro-économiques, démographiques
et les moteurs de calcul (Impôts, Cotisations, Prime) validés pour le programme.
"""

# ==============================================================================
# 1. CONSTANTES DÉMOGRAPHIQUES & PARAMÈTRES SOCIAUX
# ==============================================================================
DEMOGRAPHIE = {
    "POPULATION_TOTALE": 68_400_000,
    "NB_ADULTES_TOTAL": 53_000_000,
    "NB_ENFANTS": 15_000_000,
    "NB_RETRAITES": 17_500_000,
    "NB_ETUDIANTS": 2_900_000,
    "NB_FOYERS_FISCAUX": 40_000_000,   # Estimation étudiants post-bac
    "NB_SALARIES_PRIVE": 20_000_000,  # Assiette des cotisations patronales
}

CONSTANTES_MPP = {
    # Montants RDC (Net Mensuel)
    "RDC_ACTIF": 450,
    "RDC_ENFANT": 325,
    "RDC_RETRAITE_BONUS": 150,
    "RDC_ETUDIANT": 750,
    "RDC_PARENT_ISOLE": 300,
    "RDC_HANDICAP_TOTAL": 1200,

    # Filet de Sécurité Transitoire (Important)
    "BUDGET_GARANTIE_ZERO_PERDANT": 12.0,  # Milliards € (Provision pour compenser les pertes APL au démarrage)

    # Fiscalité
    "TVA_NORMAL": 0.26,  # Hausse de 6 pts
    "SMIC_BRUT_REF": 1800,  # Valeur pivot 2025
}

# ==============================================================================
# 2. SCÉNARIO TEMPOREL : LE "PACTE DE DÉSINFLATION"
# ==============================================================================
# Prévision de l'évolution du SMIC et de l'inflation sur 3 ans
HYPOTHESES_TEMPORELLES = {
    "ANNEE_1": {
        "INFLATION": 0.05,  # Choc TVA (+5%)
        "EVOLUTION_SMIC": 0.00,  # GEL TOTAL (Désindexation)
        "COMMENTAIRE": "Perte de pouvoir d'achat brut compensée x5 par le RDC"
    },
    "ANNEE_2": {
        "INFLATION": 0.02,  # Retour au calme
        "EVOLUTION_SMIC": 0.00,  # GEL (2ème année)
        "COMMENTAIRE": "Gain massif de compétitivité pour l'entreprise"
    },
    "ANNEE_3": {
        "INFLATION": 0.015,
        "EVOLUTION_SMIC": 0.015,  # Reprise de l'indexation normale
        "COMMENTAIRE": "Retour à la normale"
    }
}

# ==============================================================================
# 3. FINANCEMENT : AIDES ET NICHES SUPPRIMÉES (Recettes / Économies)
# ==============================================================================
# Total cible : ~187 Milliards € (112 Social + 75 Fiscal)

AIDES_SOCIALES_SUPPRIMEES = {
    "RSA_PRIME_ACTIVITE": 27.0,  # Remplacés par RDC Actif
    "APL_LOGEMENT": 16.5,  # Intégrées au cash RDC
    "FAMILLE_ENFANCE": 25.0,  # Allocs, PAJE, ARS -> RDC Enfant
    "HANDICAP": 14.8,  # AAH -> RDC Handicap
    "JEUNESSE_BOURSES": 4.3,  # Bourses -> RDC Étudiant
    "VIEILLESSE_ASPA": 4.0,  # Min Vieillesse -> Min Garanti
    "SANTE_AME": 1.2,  # Suppression AME
    "GESTION_ADMIN_FUSION": 17.7  # Gain efficience Guichet Unique
}

NICHES_FISCALES_SUPPRIMEES = {
    "EMPLOI_DOMICILE": 6.0,  # Crédit impôt 50%
    "QUOTIENT_FAMILIAL": 13.5,  # Demi-part fiscale
    "IMMOBILIER_PATRIMOINE": 8.0,  # Pinel, PTZ...
    "ABATTEMENT_10_POURCENT": 24.5,  # Suppression frais pro forfaitaires

    # ON SUPPRIME TOUT (Intéressement, Participation, Heures Sup)
    # C'est remplacé par la Prime MPP unique.
    "EPARGNE_SALARIALE_HEURES_SUP": 8.5,

    "AUTRES_MICRO_NICHES": 15.0
}

# ==============================================================================
# 4. DISPOSITIFS CONSERVÉS (Dépenses / Manque à gagner)
# ==============================================================================
NICHES_CONSERVEES = {
    # Le CIR est supprimé mais remplacé par l'Amortissement Dynamique
    # Coût estimé du nouveau dispositif :
    "AMORTISSEMENT_DYNAMIQUE": 2.5,
    # Outre-mer sanctuarisé
    "OUTRE_MER_LODEOM": 4.1,
}


# ==============================================================================
# 5. MOTEUR 1 : SIMULATEUR COÛT SALARIÉ (MPP 2027)
# ==============================================================================
def simuler_cout_salarie(salaire_brut_mensuel):
    """
    Calcule le coût employeur avec le barème 'Bosse' MPP (6% / 62% / 42%).
    """
    SMIC = 1800

    # --- A. CALCUL ACTUEL (Estimation Fillon/Bandreau) ---
    if salaire_brut_mensuel <= SMIC:
        taux_actuel = 0.04
    elif salaire_brut_mensuel <= 1.6 * SMIC:
        ratio = (salaire_brut_mensuel - SMIC) / (0.6 * SMIC)
        taux_actuel = 0.04 + (0.26 * ratio)
    elif salaire_brut_mensuel <= 2.5 * SMIC:
        ratio = (salaire_brut_mensuel - 1.6 * SMIC) / (0.9 * SMIC)
        taux_actuel = 0.30 + (0.12 * ratio)
    else:
        taux_actuel = 0.42

    charges_actuelles = salaire_brut_mensuel * taux_actuel

    # --- B. CALCUL MPP (Barème Marginal) ---
    # Tranche 1 : 0 à 1.4 SMIC (2520€) -> 6%
    # Tranche 2 : 1.4 à 3.0 SMIC (5400€) -> 62% (Effort de rattrapage)
    # Tranche 3 : > 3.0 SMIC -> 42% (Taux normal)

    limit_t1 = 1.4 * SMIC
    limit_t2 = 3.0 * SMIC

    charges_mpp = 0

    # T1
    base_t1 = min(salaire_brut_mensuel, limit_t1)
    charges_mpp += base_t1 * 0.06

    # T2
    if salaire_brut_mensuel > limit_t1:
        base_t2 = min(salaire_brut_mensuel, limit_t2) - limit_t1
        charges_mpp += base_t2 * 0.62  # Le taux calibré

    # T3
    if salaire_brut_mensuel > limit_t2:
        base_t3 = salaire_brut_mensuel - limit_t2
        charges_mpp += base_t3 * 0.42

    # Taux moyen réel MPP (pour la taxation de la Prime)
    taux_moyen_mpp = charges_mpp / salaire_brut_mensuel if salaire_brut_mensuel > 0 else 0

    return {
        "cout_total_actuel": round(salaire_brut_mensuel + charges_actuelles),
        "cout_total_mpp": round(salaire_brut_mensuel + charges_mpp),
        "gain_mensuel": round(charges_actuelles - charges_mpp),
        "taux_moyen_mpp_pourcent": round(taux_moyen_mpp * 100, 1)
    }


# ==============================================================================
# 6. MOTEUR 2 : SIMULATEUR PRIME DE PARTAGE MPP
# ==============================================================================
def simuler_prime_mpp(montant_prime, salaire_brut_mensuel, cumul_primes_annee=0):
    """
    Simule le coût et le net de la nouvelle prime unique.
    Vérifie les verrous (Plafond 3000€, Règle des 10%).
    """
    # 1. Récupération du taux moyen de l'entreprise (basé sur le salaire du bénéficiaire)
    infos_salaire = simuler_cout_salarie(salaire_brut_mensuel)
    taux_patronal_moyen = infos_salaire["taux_moyen_mpp_pourcent"] / 100

    # 2. Vérification des plafonds
    plafond_annuel = 3000
    reste_disponible = max(0, plafond_annuel - cumul_primes_annee)

    # Partie de la prime qui respecte le plafond (Désocialisée salarié / Taux moyen patron)
    part_sous_plafond = min(montant_prime, reste_disponible)

    # Partie hors plafond (Traitée comme du salaire : Taux marginal 62% ou 42% + Charges salariales)
    part_hors_plafond = montant_prime - part_sous_plafond

    # --- COÛT PATRON ---
    cout_part_exoneree = part_sous_plafond * (1 + taux_patronal_moyen)

    # Pour la part hors plafond, on simplifie en prenant le taux marginal le plus haut (Tranche 2 à 62%)
    # C'est dissuasif, c'est le but.
    cout_part_hors_plafond = part_hors_plafond * (1 + 0.62)

    cout_total_patron = cout_part_exoneree + cout_part_hors_plafond

    # --- NET SALARIÉ ---
    # Sous plafond : Brut = Net
    net_sous_plafond = part_sous_plafond
    # Hors plafond : Charges salariales standard (~22%)
    net_hors_plafond = part_hors_plafond * (1 - 0.22)

    total_net_salarie = net_sous_plafond + net_hors_plafond

    return {
        "montant_demande": montant_prime,
        "part_exoneree": part_sous_plafond,
        "part_requalifiee_salaire": part_hors_plafond,
        "cout_total_patron": round(cout_total_patron),
        "net_total_salarie": round(total_net_salarie),
        "message": "Attention : dépassement du plafond annuel !" if part_hors_plafond > 0 else "Prime valide."
    }


# ==============================================================================
# 7. MOTEUR 3 : SIMULATEUR IMPÔT (Avec suppression abattement 10%)
# ==============================================================================
def simuler_impot_mpp(revenu_net_imposable_annuel, nb_parts, montant_rdc_annuel):
    # Système Actuel (2025)
    # Abattement 10%
    abat = min(revenu_net_imposable_annuel * 0.10, 14177)
    base_act = revenu_net_imposable_annuel - abat
    q_act = base_act / nb_parts

    def bareme(q, tranches, taux):
        impot = 0
        for i in range(len(taux)):
            t_min = tranches[i]
            t_max = tranches[i + 1] if i + 1 < len(tranches) else float('inf')
            if q > t_min:
                impot += (min(q, t_max) - t_min) * taux[i]
        return impot

    # Barème 2025
    tranches = [0, 11294, 28797, 82341, 177106]
    taux_act = [0.00, 0.11, 0.30, 0.41, 0.45]
    impot_act = bareme(q_act, tranches, taux_act) * nb_parts

    # Système MPP
    # Base élargie : Pas d'abattement + RDC
    base_mpp = revenu_net_imposable_annuel + montant_rdc_annuel
    q_mpp = base_mpp / nb_parts

    # Barème MPP (+3 pts hauts revenus)
    taux_mpp = [0.00, 0.11, 0.33, 0.44, 0.48]
    impot_mpp = bareme(q_mpp, tranches, taux_mpp) * nb_parts

    return {
        "actuel": round(impot_act),
        "mpp": round(impot_mpp),
        "delta": round(impot_mpp - impot_act)
    }