import sqlite3
c = sqlite3.connect("database/poplicence.db")
q = "select c.nom, p.nom from categories_site c left join categories_site p on p.id = c.categorie_parente_id where c.nom like ? or c.nom like ?"
for r in c.execute(q, ("%lasseur%", "%erre-livre%")):
    print(r)
