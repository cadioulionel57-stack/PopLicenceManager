import sqlite3

c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")

noms = [
    ("C1", "Carton simple cannelure 20 x 15 x 12"),
    ("C2", "Carton simple cannelure 35 x 25 x 10"),
    ("C3", "Carton double cannelure 45 x 45 x 20"),
    ("C4", "Carton double cannelure 60 x 40 x 30"),
    ("P1", "Pochette plastique opaque 17,5 x 25,5"),
    ("P2", "Pochette plastique opaque 24 x 35"),
    ("P3", "Pochette plastique opaque 55 x 77"),
    ("P4", "Pochette plastique opaque 35 x 45"),
]

for code, nom in noms:
    c.execute("UPDATE grille_emballage SET nom=? WHERE code=?", (nom, code))
    print("  ", code, "->", nom)

c.commit()

print()
for r in c.execute("SELECT code,nom,cout_ht FROM grille_emballage WHERE actif=1 ORDER BY code"):
    print(r)