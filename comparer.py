import sqlite3
c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")
c.row_factory = sqlite3.Row
sql = """
SELECT id, nom, fournisseur_id, prix_fournisseur_ht, prix_achat_gestion,
       quantite_stock, exporte_wizishop, id_wizishop, modele_fiche_id,
       image_principale, description_longue
FROM produits WHERE id IN (172,237,173,239,175,240) ORDER BY nom, id
"""
for r in c.execute(sql):
    print(r["id"], "|", r["nom"][:45], "| fourn", r["fournisseur_id"],
          "| achat", r["prix_fournisseur_ht"], "| gestion", r["prix_achat_gestion"],
          "| stock", r["quantite_stock"], "| exp", r["exporte_wizishop"],
          "| idws", r["id_wizishop"], "| modele", r["modele_fiche_id"],
          "| img", "oui" if r["image_principale"] else "NON",
          "| desc", len(r["description_longue"] or ""))
