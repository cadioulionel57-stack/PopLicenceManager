import sqlite3

conn = sqlite3.connect("database/poplicence.db")
conn.row_factory = sqlite3.Row

# ----------------------------------------------------------
# 1. Recalibrage des 7 familles existantes.
#    Les identifiants sont conservés : aucun produit ne peut
#    se retrouver orphelin.
# ----------------------------------------------------------

familles = [
    (1, "Vêtements à tailles - t-shirts, pulls, sweats, pyjamas, bodys, leggings", 0.28, 0.25, 2),
    (2, "Sacs et bagagerie - sacs à dos, sacs à main, cartables, trousses", 1.34, 0.06, 5),
    (3, "Objets - mugs, vaisselle, papeterie, figurines, déco, jeux", 0.52, 0.04, 3),
    (4, "Linge de maison - serviettes, parures, plaids, coussins", 0.28, 0.05, 2),
    (5, "Funko Pop et petites figurines sous boîte", 0.88, 0.04, 4),
    (6, "Volumineux et fragile - statues, coffrets collectors, grosses lampes", 2.08, 0.06, 6),
    (7, "DROP-Mobilier Enfant", 0.00, 0.06, 7),
]

for identifiant, nom, emballage, retour, emballage_id in familles:

    conn.execute(
        """
        UPDATE familles_produit
        SET nom = ?, cout_emballage_ht = ?,
            taux_retour = ?, emballage_id = ?
        WHERE id = ?
        """,
        (nom, emballage, retour, emballage_id, identifiant)
    )

# ----------------------------------------------------------
# 2. Les deux familles qui manquaient.
#    Créées seulement si elles n'existent pas déjà, pour que
#    ce script puisse être relancé sans rien dupliquer.
# ----------------------------------------------------------

nouvelles = [
    ("Accessoires taille unique - bonnets, écharpes, gants, chaussettes", 0.16, 0.06, 1),
    ("Chaussures - adulte, enfant, bottes, chaussons", 1.00, 0.30, 4),
]

for nom, emballage, retour, emballage_id in nouvelles:

    existe = conn.execute(
        "SELECT id FROM familles_produit WHERE nom = ?", (nom,)
    ).fetchone()

    if existe is None:

        conn.execute(
            """
            INSERT INTO familles_produit
            (nom, cout_emballage_ht, taux_retour, actif, emballage_id)
            VALUES (?, ?, ?, 1, ?)
            """,
            (nom, emballage, retour, emballage_id)
        )

# ----------------------------------------------------------
# 3. Rebasculement des produits sur la bonne famille,
#    d'après leur catégorie de site.
# ----------------------------------------------------------

correspondances = {
    "Bonnets": "Accessoires taille unique",
    "Écharpes": "Accessoires taille unique",
    "Chaussettes": "Accessoires taille unique",
    "Chaussons": "Chaussures",
    "Baskets": "Chaussures",
    "Pulls": "Vêtements à tailles",
    "Sweats & Hoodies": "Vêtements à tailles",
    "Pyjamas": "Vêtements à tailles",
    "T-shirts": "Vêtements à tailles",
    "Trousses de toilette": "Objets",
    "Accessoires de mode": "Objets",
    "Sacs à dos": "Sacs et bagagerie",
    "Sacs à main": "Sacs et bagagerie",
}

total = 0

for categorie, debut_famille in correspondances.items():

    famille = conn.execute(
        "SELECT id FROM familles_produit WHERE nom LIKE ?",
        (debut_famille + "%",)
    ).fetchone()

    if famille is None:
        print("famille introuvable :", debut_famille)
        continue

    resultat = conn.execute(
        """
        UPDATE produits
        SET famille_produit_id = ?
        WHERE categorie_site_id = (
            SELECT id FROM categories_site WHERE nom = ?
        )
        """,
        (famille["id"], categorie)
    )

    if resultat.rowcount:
        print(f"   {categorie} -> {debut_famille} : {resultat.rowcount}")

    total += resultat.rowcount

conn.commit()

# ----------------------------------------------------------
# 4. Vérification
# ----------------------------------------------------------

print()
print("--- familles ---")

for ligne in conn.execute(
    "SELECT id, taux_retour, cout_emballage_ht, nom "
    "FROM familles_produit ORDER BY id"
):
    print(
        f"  {ligne['id']:2d}  retour {ligne['taux_retour']*100:4.1f}%"
        f"  emballage {ligne['cout_emballage_ht']:5.2f}  {ligne['nom']}"
    )

print()
print("--- produits par famille ---")

for ligne in conn.execute(
    "SELECT COUNT(*) AS n, COALESCE(f.nom, 'AUCUNE FAMILLE') AS nom "
    "FROM produits p "
    "LEFT JOIN familles_produit f ON f.id = p.famille_produit_id "
    "WHERE p.actif = 1 GROUP BY 2 ORDER BY 1 DESC"
):
    print(f"  {ligne['n']:3d}  {ligne['nom']}")

print()
print("produits rebasculés :", total)