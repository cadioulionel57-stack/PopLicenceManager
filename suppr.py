import sqlite3
c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")
c.execute("DELETE FROM produits WHERE id IN (237,239,240)")
c.commit()
print("Supprimes :", c.total_changes)
for r in c.execute("SELECT id, nom, fournisseur_id, quantite_stock FROM produits WHERE nom LIKE '%KPop Demon Hunters%' ORDER BY nom"):
    print(r)
