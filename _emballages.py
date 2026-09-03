import sqlite3, shutil, datetime

base = r"C:\PopLicenceManager\database\poplicence.db"
copie = r"C:\SauvegardeBase\poplicence_avant_emballages_%s.db" % datetime.datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy2(base, copie)
print("Sauvegarde :", copie)

c = sqlite3.connect(base)

# (code, L, l, h, cout_ht)  -- lignes existantes a corriger
maj = [
    ("C1", 20.0, 15.0, 12.0, 0.48),
    ("C2", 35.0, 25.0, 10.0, 0.63),
    ("C3", 45.0, 45.0, 20.0, 2.20),
    ("C4", 60.0, 40.0, 30.0, 2.39),
    ("P1", 17.5, 25.5, 1.0, 0.14),
    ("P2", 24.0, 35.0, 1.0, 0.22),
    ("P3", 55.0, 77.0, 1.0, 0.65),
    ("P4", 35.0, 45.0, 1.0, 0.23),
]

for code, L, l, h, cout in maj:
    c.execute(
        "UPDATE grille_emballage SET longueur_ext_cm=?, largeur_ext_cm=?, "
        "hauteur_ext_cm=?, cout_ht=? WHERE code=?",
        (L, l, h, cout, code),
    )
    print("  corrige :", code)

# (code, nom, L, l, h, poids_g, poids_max_g, cout_ht, calage_ht) -- nouveaux
ajouts = [
    ("C5", "Carton simple cannelure 35 x 22 x 20", 35.0, 22.0, 20.0, 240.0, 5000.0, 0.76, 0.12),
    ("C6", "Carton simple cannelure 60 x 20 x 15", 60.0, 20.0, 15.0, 300.0, 5000.0, 1.14, 0.15),
    ("K1", "Sac kraft brun 24 x 12 x 31", 24.0, 12.0, 31.0, 45.0, 3000.0, 0.28, 0.05),
    ("K2", "Sac kraft brun 32 x 12 x 41", 32.0, 12.0, 41.0, 60.0, 4000.0, 0.33, 0.05),
]

for a in ajouts:
    deja = c.execute("SELECT id FROM grille_emballage WHERE code=?", (a[0],)).fetchone()
    if deja:
        print("  existe deja :", a[0])
        continue
    c.execute(
        "INSERT INTO grille_emballage (code,nom,longueur_ext_cm,largeur_ext_cm,"
        "hauteur_ext_cm,poids_g,poids_max_g,cout_ht,calage_ht,actif) "
        "VALUES (?,?,?,?,?,?,?,?,?,1)", a
    )
    print("  ajoute :", a[0], a[1])

# F1 non achete
c.execute("UPDATE grille_emballage SET actif=0 WHERE code='F1'")
print("  desactive : F1 (carton fourreau, non achete)")

c.commit()

print()
for r in c.execute("SELECT code,nom,longueur_ext_cm,largeur_ext_cm,hauteur_ext_cm,cout_ht,actif FROM grille_emballage ORDER BY code"):
    print(r)