import sqlite3
c = sqlite3.connect("database/poplicence.db")
c.row_factory = sqlite3.Row
q = "select f.nom fourn, p.actif, p.statut_stock, count(*) n from produits p left join fournisseurs f on f.id = p.fournisseur_id group by 1, 2, 3"
for r in c.execute(q):
    print(dict(r))
