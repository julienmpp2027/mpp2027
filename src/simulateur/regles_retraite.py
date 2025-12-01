# CONSTANTES POLITIQUES DU PROGRAMME MPP2027
CONSTANTES = {
    "SMIC_NET_REF": 1426.3,
    "POINTS_PAR_AN_SMIC": 465,
    "VALEUR_POINT": 1.0,
    "AGE_MORT": 85,
    "BONUS_ENFANT": 0.5,  # 6 mois par enfant

    # Paliers de rendement
    "PALIER_1_LIMIT": 20000,  # 100% jusqu'à 20k
    "PALIER_2_LIMIT": 50000,  # 80% de 20k à 50k
    "TAUX_2": 0.8,
    "TAUX_3": 0.6,  # 60% au-delà de 50k

    # Filet de sécurité
    "MINIMUM_GARANTI_67": 1000,  # Socle min à 67 ans (avant RDC)
    "MONTANT_RDC": 150,  # Boost pouvoir d'achat pour tous
}


def calculer_pension_complete(salaire, annees, enfants, penibilite, age_depart):
    """
    Calcule la pension complète selon les règles MPP2027.
    Retourne un dictionnaire avec tous les détails.
    """
    c = CONSTANTES

    # 1. CAPITAL BRUT
    pts_par_an = (salaire / c["SMIC_NET_REF"]) * c["POINTS_PAR_AN_SMIC"]
    total_brut = pts_par_an * annees

    # 2. APPLICATION DES PALIERS (RENDEMENT DÉCROISSANT)
    total_net = 0

    if total_brut <= c["PALIER_1_LIMIT"]:
        total_net = total_brut
    elif total_brut <= c["PALIER_2_LIMIT"]:
        # Palier 1 plein + partie Palier 2
        reste = total_brut - c["PALIER_1_LIMIT"]
        total_net = c["PALIER_1_LIMIT"] + (reste * c["TAUX_2"])
    else:
        # Palier 1 plein + Palier 2 plein + partie Palier 3
        # Palier 2 plein = 30 000 pts * 0.8 = 24 000 pts
        reste = total_brut - c["PALIER_2_LIMIT"]
        total_net = c["PALIER_1_LIMIT"] + 24000 + (reste * c["TAUX_3"])

    # 3. DIVISEUR (ESPÉRANCE DE VIE RESTANTE)
    evr_base = c["AGE_MORT"] - age_depart
    bonus_enfants = enfants * c["BONUS_ENFANT"]

    diviseur = evr_base - bonus_enfants - penibilite
    if diviseur < 1: diviseur = 1  # Sécurité mathématique

    # 4. PENSION DE BASE (MATHÉMATIQUE)
    pension_base = (total_net / diviseur) * c["VALEUR_POINT"]

    # 5. MINIMUM GARANTI (SOCLE DIGNITÉ)
    # Si on a 67 ans ou plus, on ne peut pas toucher moins de 1000€ (hors RDC)
    est_minime = False
    if age_depart >= 67:
        if pension_base < c["MINIMUM_GARANTI_67"]:
            pension_base = c["MINIMUM_GARANTI_67"]
            est_minime = True

    # 6. AJOUT DU RDC (BOOST POUVOIR D'ACHAT)
    pension_finale = pension_base + c["MONTANT_RDC"]

    return {
        "capital_brut": round(total_brut),
        "capital_net": round(total_net),
        "delta_solidarite": round(total_net - total_brut),
        "diviseur": round(diviseur, 1),
        "pension_base": round(pension_base),
        "rdc": c["MONTANT_RDC"],
        "pension_finale": round(pension_finale),
        "est_minime": est_minime
    }