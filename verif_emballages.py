import sqlite3
c = sqlite3.connect("database/poplicence.db")
c.row_factory = sqlite3.Row
q = """
select p.nom, f.nom as famille, g.code, g.nom as emballage,
       case when p.id_wizishop is null or p.id_wizishop = ''
            then '' else 'DEJA DANS WIZISHOP' end as etat
from produits p
left join familles_produit f on f.id = p.famille_produit_id
left join grille_emballage g on g.id = p.emballage_id
where f.nom like '%Linge de maison%' or f.nom like '%Funko%'
order by f.nom, p.nom
"""
for r in c.execute(q):
    print("%-4s %-45s %-30s %s" % (
        r["code"] or "--", r["nom"][:45], r["famille"][:30], r["etat"]))
