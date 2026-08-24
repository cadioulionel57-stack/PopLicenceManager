import sqlite3
c = sqlite3.connect("database/poplicence.db")
c.row_factory = sqlite3.Row
q = """
select f.nom as famille, g.code, count(*) as n
from produits p
left join familles_produit f on f.id = p.famille_produit_id
left join grille_emballage g on g.id = p.emballage_id
group by f.nom, g.code order by n desc
"""
for r in c.execute(q):
    print("%4d  %-6s %s" % (r["n"], r["code"] or "--", r["famille"] or "(sans famille)"))
