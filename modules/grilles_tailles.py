r"""
modules/grilles_tailles.py
------------------------------------------------------------
Les sept grilles de tailles de Pop Licence.
  - la page /guide-des-tailles.html (grilles completes)
  - le tableau des fiches produit, reduit aux tailles vendues

Sur la fiche, le tableau est REPLIABLE : ferme, il ne prend
qu'une ligne et ne coupe pas la description. La barre est en
jaune clair pour qu'on comprenne qu'elle s'ouvre.

La grille ADULTE (S a XXL) sert par defaut, unisexe compris.
La grille FEMME ne sort que si le champ Coupe contient
"Femme".

Pointures : formule francaise pointure = (3 x L + 4) / 2.
------------------------------------------------------------
"""

GRILLES = {

    "bebe": {
        "titre": "Tailles bebe",
        "colonnes": ["Age", "Taille (cm)", "Poids indicatif"],
        "lignes": [
            ("Naissance", "50", "3,3 kg"),
            ("1 mois", "54", "4 kg"),
            ("3 mois", "60", "5 a 6 kg"),
            ("6 mois", "68", "7 a 8 kg"),
            ("9 mois", "71", "8 a 9 kg"),
            ("12 mois", "74", "9 a 10 kg"),
            ("18 mois", "81", "11 kg"),
            ("24 mois", "86", "12 kg"),
        ],
    },

    "enfant": {
        "titre": "Tailles enfant",
        "colonnes": ["Age", "Stature (cm)"],
        "lignes": [
            ("2 ans", "92"),
            ("3 ans", "98"),
            ("4 ans", "104"),
            ("5 ans", "110"),
            ("6 ans", "116"),
            ("7 ans", "122"),
            ("8 ans", "128"),
            ("9 ans", "134"),
            ("10 ans", "140"),
            ("11 ans", "146"),
            ("12 ans", "152"),
            ("13 ans", "158"),
            ("14 ans", "164"),
        ],
    },

    "adulte": {
        "titre": "Tailles adulte",
        "colonnes": ["Taille", "Tour de poitrine", "Tour de taille"],
        "lignes": [
            ("S", "88 a 94 cm", "76 a 82 cm"),
            ("M", "96 a 102 cm", "84 a 90 cm"),
            ("L", "104 a 110 cm", "92 a 98 cm"),
            ("XL", "112 a 118 cm", "100 a 106 cm"),
            ("XXL", "120 a 126 cm", "108 a 114 cm"),
        ],
    },

    "femme": {
        "titre": "Tailles femme",
        "colonnes": ["Taille", "Tour de poitrine", "Tour de taille"],
        "lignes": [
            ("S", "84 a 88 cm", "66 a 70 cm"),
            ("M", "90 a 94 cm", "72 a 76 cm"),
            ("L", "96 a 102 cm", "78 a 84 cm"),
            ("XL", "104 a 110 cm", "86 a 92 cm"),
            ("XXL", "112 a 118 cm", "94 a 100 cm"),
        ],
    },

    "pointures": {
        "titre": "Pointures",
        "colonnes": ["Pointure", "Longueur du pied"],
        "lignes": [
            ("18", "10,7 cm"), ("19", "11,3 cm"), ("20", "12,0 cm"),
            ("21", "12,7 cm"), ("22", "13,3 cm"), ("23", "14,0 cm"),
            ("24", "14,7 cm"), ("25", "15,3 cm"), ("26", "16,0 cm"),
            ("27", "16,7 cm"), ("28", "17,3 cm"), ("29", "18,0 cm"),
            ("30", "18,7 cm"), ("31", "19,3 cm"), ("32", "20,0 cm"),
            ("33", "20,7 cm"), ("34", "21,3 cm"), ("35", "22,0 cm"),
            ("36", "22,7 cm"), ("37", "23,3 cm"), ("38", "24,0 cm"),
            ("39", "24,7 cm"), ("40", "25,3 cm"), ("41", "26,0 cm"),
            ("42", "26,7 cm"), ("43", "27,3 cm"), ("44", "28,0 cm"),
            ("45", "28,7 cm"), ("46", "29,3 cm"),
        ],
    },

    "tour_de_tete": {
        "titre": "Tour de tete",
        "colonnes": ["Taille", "Tour de tete"],
        "lignes": [
            ("0 a 6 mois", "42 a 44 cm"),
            ("6 a 12 mois", "45 a 47 cm"),
            ("1 a 2 ans", "48 a 49 cm"),
            ("3 a 5 ans", "50 a 52 cm"),
            ("6 a 8 ans", "53 a 54 cm"),
            ("9 a 12 ans", "55 a 56 cm"),
            ("Adulte S/M", "55 a 57 cm"),
            ("Adulte L/XL", "58 a 60 cm"),
        ],
    },

    "gants": {
        "titre": "Gants",
        "colonnes": ["Taille", "Tour de paume"],
        "lignes": [
            ("4 a 6 ans", "14 cm"),
            ("7 a 9 ans", "15 a 16 cm"),
            ("10 a 12 ans", "17 a 18 cm"),
            ("Adulte S", "19 a 20 cm"),
            ("Adulte M", "21 a 22 cm"),
            ("Adulte L", "23 a 24 cm"),
            ("Adulte XL", "25 a 26 cm"),
        ],
    },
}

# La grille femme n'est jamais trouvee toute seule : ses
# libelles sont ceux de la grille adulte.
GRILLES_CHERCHEES = [cle for cle in GRILLES if cle != "femme"]


def _normaliser(texte):
    """"3 ANS", "3 ans" et "3ans" sont pareils."""

    return "".join(str(texte or "").lower().split())


def grille_pour(libelles, coupe=None):
    """
    Trouve la grille qui correspond aux tailles vendues.
    Renvoie (cle_de_grille, lignes_retenues) ou (None, []).
    """

    cherches = [_normaliser(l) for l in libelles if l]

    if not cherches:
        return None, []

    meilleur = None
    meilleures_lignes = []

    for cle in GRILLES_CHERCHEES:

        retenues = [
            ligne for ligne in GRILLES[cle]["lignes"]
            if _normaliser(ligne[0]) in cherches
        ]

        if len(retenues) > len(meilleures_lignes):
            meilleur = cle
            meilleures_lignes = retenues

    # Au moins la moitie des tailles vendues doit etre
    # reconnue, sinon aucun tableau.
    if not meilleur or len(meilleures_lignes) * 2 < len(cherches):
        return None, []

    if meilleur == "adulte" and "femme" in _normaliser(coupe):

        meilleur = "femme"

        meilleures_lignes = [
            ligne for ligne in GRILLES["femme"]["lignes"]
            if _normaliser(ligne[0]) in cherches
        ]

    return meilleur, meilleures_lignes


def tableau_html(libelles, coupe=None):
    """
    Renvoie le bloc repliable pret a poser dans la fiche, ou
    une chaine vide si aucune grille ne correspond.

    Aucun caractere hors Latin-1 : WiziShop les afficherait
    en clair. Les symboles passent en entites decimales.
    """

    cle, lignes = grille_pour(libelles, coupe)

    if not cle or not lignes:
        return ""

    grille = GRILLES[cle]

    entetes = "".join(
        "<th style=\"padding:12px 14px;text-align:left;"
        "font-size:12px;font-weight:800;text-transform:uppercase;"
        "letter-spacing:.04em;color:#ffffff;\">"
        f"{colonne}</th>"
        for colonne in grille["colonnes"]
    )

    corps = ""

    for rang, ligne in enumerate(lignes):

        fond = "#ffffff" if rang % 2 == 0 else "#F8FAFC"

        cellules = ""

        for colonne, valeur in enumerate(ligne):

            graisse = "800" if colonne == 0 else "400"
            couleur = "#0F172A" if colonne == 0 else "#334155"

            cellules += (
                f"<td style=\"padding:11px 14px;font-size:15px;"
                f"font-weight:{graisse};color:{couleur};"
                f"border-bottom:1px solid #E2E8F0;\">"
                f"{valeur}</td>"
            )

        corps += f"<tr style=\"background:{fond};\">{cellules}</tr>"

    return (
        "<details style=\"background:#ffffff;"
        "border:1px solid #FDE68A;border-radius:12px;"
        "margin:20px 0;overflow:hidden;\">"

        "<summary style=\"cursor:pointer;padding:15px 18px;"
        "background:#FEF3C7;font-size:16px;font-weight:800;"
        "color:#0F172A;\">"

        "Trouver sa taille"

        "<span style=\"font-weight:600;font-size:14px;"
        "color:#92400E;\"> &#8212; cliquez pour voir les "
        "mesures</span>"

        "</summary>"

        "<div style=\"padding:18px;\">"

        "<div style=\"overflow-x:auto;border-radius:10px;"
        "border:1px solid #E2E8F0;\">"
        "<table style=\"width:100%;border-collapse:collapse;\">"
        f"<thead style=\"background:#0F172A;\"><tr>{entetes}</tr>"
        "</thead>"
        f"<tbody>{corps}</tbody>"
        "</table>"
        "</div>"

        "<p style=\"margin:14px 0 0 0;font-size:13px;"
        "line-height:1.7;color:#64748b;\">"
        "En cas de doute entre deux tailles, choisissez la "
        "plus grande. "
        "<a href=\"/guide-des-tailles.html\" "
        "style=\"color:#2563EB;font-weight:700;\">"
        "Voir le guide des tailles complet</a>"
        "</p>"

        "</div>"
        "</details>"
    )


if __name__ == "__main__":

    essais = [
        (["2 ans", "3 ans", "4 ans"], None),
        (["S", "M", "L", "XL", "XXL"], "Unisexe"),
        (["S", "M", "L", "XL", "XXL"], "Femme"),
        (["23", "24", "25", "26", "27", "28"], None),
        (["Rose", "Gris"], None),
    ]

    for libelles, coupe in essais:
        cle, lignes = grille_pour(libelles, coupe)
        print(f"\n{libelles}  coupe={coupe}  ->  {cle}")
        for ligne in lignes:
            print("   ", " | ".join(ligne))