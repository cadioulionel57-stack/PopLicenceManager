import sqlite3, shutil, datetime

base = r"C:\PopLicenceManager\database\poplicence.db"
copie = r"C:\SauvegardeBase\poplicence_avant_marques_%s.db" % datetime.datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy2(base, copie)
print("Sauvegarde :", copie)

c = sqlite3.connect(base)

# Spider-man (10) fusionne dans Spider-Man (11)
c.execute("UPDATE produits SET marque_id=11 WHERE marque_id=10")
c.execute("DELETE FROM marques WHERE id=10")
print("Spider-man fusionne dans Spider-Man")

# Star Wars (20) renomme en Star-Wars, l'ancien vide (52) supprime
c.execute("DELETE FROM marques WHERE id=52")
c.execute("UPDATE marques SET nom='Star-Wars' WHERE id=20")
print("Star Wars renomme en Star-Wars")

# poplicence (53) renomme en Pop Licence, Poplicence vide (14) supprime
c.execute("DELETE FROM marques WHERE id=14")
c.execute("UPDATE marques SET nom='Pop Licence' WHERE id=53")
print("poplicence renomme en Pop Licence")

# Mercredi vide (59) supprime, Wednesday (60) conserve
c.execute("DELETE FROM marques WHERE id=59")
print("Mercredi supprime, Wednesday conserve")

c.commit()

print()
print("Marques restantes :", c.execute("SELECT count(1) FROM marques").fetchone()[0])
orphelins = c.execute(
    "SELECT count(1) FROM produits WHERE marque_id IS NOT NULL "
    "AND marque_id NOT IN (SELECT id FROM marques)"
).fetchone()[0]
print("Produits sans marque valide :", orphelins)