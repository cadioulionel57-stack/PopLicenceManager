import sqlite3
c = sqlite3.connect("database/poplicence.db")
q = "select p.actif, count(*) from produits p join fournisseurs f on f.id = p.fournisseur_id where f.nom = ? group by 1"
print(c.execute(q, ("ABY Style",)).fetchall())
