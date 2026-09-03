import sqlite3
c = sqlite3.connect('poplicence.db')
cols = [x[1] for x in c.execute("PRAGMA table_info(modeles_fiche_produit)")]
print("COLONNES:", cols)
print("---")
for r in c.execute("SELECT id, nom FROM modeles_fiche_produit WHERE html_template LIKE '%Bretelles ajustables%'"):
    print(r[0], "|", r[1])
