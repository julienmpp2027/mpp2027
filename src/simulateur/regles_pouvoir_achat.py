# src/simulateur/regles_pouvoir_achat.py

CONSTANTES_PA = {
    # --- RDC (MONTANTS NETS MENSUELS) ---
    "RDC_ACTIF": 450,
    "RDC_ENFANT": 325,
    "RDC_RETRAITE_BONUS": 150,  # S'ajoute à la pension
    "RDC_ETUDIANT": 750,  # Remplace bourses
    "BONUS_PARENT_ISOLE": 300,

    # --- TVA (HYPOTHÈSE DE TAUX MOYEN PONDÉRÉ) ---
    # On considère un panier moyen (mélange taux réduit/normal)
    # Actuel : Moyenne env 15% (mix 5.5%, 10%, 20%)
    # MPP : Normal passe à 26%. On estime la moyenne pondérée à 21% (+6 pts)
    "TX_TVA_ACTUEL": 0.15,
    "TX_TVA_MPP": 0.21,

    # --- BARÈME IMPÔT ACTUEL (2025) ---
    # (Tranche limite, Taux)
    "BAREME_ACTUEL": [
        (11294, 0.00),
        (28797, 0.11),
        (82341, 0.30),
        (177106, 0.41),
        (float('inf'), 0.45)
    ],

    # --- BARÈME IMPÔT MPP 2027 ---
    # +3 points sur les 3 tranches supérieures
    "BAREME_MPP": [
        (11294, 0.00),
        (28797, 0.11),
        (82341, 0.33),  # 30 -> 33%
        (177106, 0.44),  # 41 -> 44%
        (float('inf'), 0.48)  # 45 -> 48%
    ]
}


def calculer_impot_revenu(revenu_annuel_imposable, parts, bareme):
    quotient = revenu_annuel_imposable / parts
    impot_brut = 0
    precedente_limite = 0
    for limite, taux in bareme:
        if quotient > precedente_limite:
            base = min(quotient, limite) - precedente_limite
            impot_brut += base * taux
            precedente_limite = limite
        else:
            break
    return impot_brut * parts


def calculer_pouvoir_achat(revenu_net_mensuel, adultes, enfants, statut_adulte, is_parent_isole, part_consommation):
    c = CONSTANTES_PA

    revenu_annuel_net = revenu_net_mensuel * 12

    # ====================================================
    # SCÉNARIO A : SYSTÈME ACTUEL
    # ====================================================

    # Parts fiscales : Adultes + Enfants (Système actuel de quotient familial)
    parts_actuel = adultes
    if enfants == 1:
        parts_actuel += 0.5
    elif enfants == 2:
        parts_actuel += 1.0
    elif enfants >= 3:
        parts_actuel += 1.0 + (enfants - 2)  # 1 part par enfant à partir du 3ème

    if is_parent_isole: parts_actuel += 0.5  # Demi-part parent isolé

    # Abattement 10%
    revenu_imposable_actuel = revenu_annuel_net * 0.9

    impot_actuel_an = calculer_impot_revenu(revenu_imposable_actuel, parts_actuel, c["BAREME_ACTUEL"])
    impot_actuel_mois = impot_actuel_an / 12

    net_disponible_actuel = revenu_net_mensuel - impot_actuel_mois

    # Calcul Coût TVA Actuelle
    conso_mensuelle_actuelle = net_disponible_actuel * (part_consommation / 100)
    # Formule TVA en dehors : PrixHT * Taux. Ici on a du TTC.
    # Part TVA dans TTC = Montant * (Taux / (1+Taux))
    cout_tva_actuel = conso_mensuelle_actuelle * (c["TX_TVA_ACTUEL"] / (1 + c["TX_TVA_ACTUEL"]))

    pa_reel_actuel = net_disponible_actuel - cout_tva_actuel

    # ====================================================
    # SCÉNARIO B : SYSTÈME MPP 2027
    # ====================================================

    # 1. Calcul du RDC
    rdc_mensuel = 0

    # RDC Adultes (selon statut)
    # On simplifie : si 2 adultes, on applique le statut au chef de famille et Actif au conjoint par défaut pour l'instant
    # Ou mieux : on considère le statut principal
    if statut_adulte == 'etudiant':
        rdc_mensuel += c["RDC_ETUDIANT"] * adultes  # Si couple d'étudiants
    elif statut_adulte == 'retraite':
        rdc_mensuel += c["RDC_RETRAITE_BONUS"] * adultes
    else:  # Actif
        rdc_mensuel += c["RDC_ACTIF"] * adultes

    # RDC Enfants
    rdc_mensuel += enfants * c["RDC_ENFANT"]

    # Bonus Parent Isolé
    if is_parent_isole:
        rdc_mensuel += c["BONUS_PARENT_ISOLE"]

    rdc_annuel = rdc_mensuel * 12

    # 2. Impôt MPP
    # Suppression de l'abattement 10% -> Base = 100% du net
    # RDC Imposable -> On l'ajoute
    base_imposable_mpp = revenu_annuel_net + rdc_annuel

    # Suppression des parts fiscales enfants (remplacées par RDC Enfant)
    parts_mpp = adultes
    if parts_mpp < 1: parts_mpp = 1

    impot_mpp_an = calculer_impot_revenu(base_imposable_mpp, parts_mpp, c["BAREME_MPP"])
    impot_mpp_mois = impot_mpp_an / 12

    net_disponible_mpp = revenu_net_mensuel + rdc_mensuel - impot_mpp_mois

    # 3. Calcul Coût TVA MPP (Hausse taux)
    conso_mensuelle_mpp = net_disponible_mpp * (part_consommation / 100)
    cout_tva_mpp = conso_mensuelle_mpp * (c["TX_TVA_MPP"] / (1 + c["TX_TVA_MPP"]))

    pa_reel_mpp = net_disponible_mpp - cout_tva_mpp

    # Différence purement due à la hausse de TVA
    surcout_tva = cout_tva_mpp - (conso_mensuelle_mpp * (c["TX_TVA_ACTUEL"] / (1 + c["TX_TVA_ACTUEL"])))

    return {
        "actuel": {
            "impot": round(impot_actuel_mois),
            "tva": round(cout_tva_actuel),
            "disponible": round(net_disponible_actuel),
            "final": round(pa_reel_actuel)
        },
        "mpp": {
            "rdc": round(rdc_mensuel),
            "impot": round(impot_mpp_mois),
            "tva": round(cout_tva_mpp),
            "surcout_tva": round(surcout_tva),
            "disponible": round(net_disponible_mpp),
            "final": round(pa_reel_mpp)
        },
        "delta": {
            "valeur": round(pa_reel_mpp - pa_reel_actuel),
            "is_positif": (pa_reel_mpp - pa_reel_actuel) >= 0
        }
    }