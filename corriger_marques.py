import sqlite3
c = sqlite3.connect("database/poplicence.db")

def basculer(mauvais, bon):
    c.execute("update produits set marque_id = (select id from marques where nom = ?) where marque_id = (select id from marques where nom = ?)", (bon, mauvais))
    n = c.execute("select count(*) from produits where marque_id = (select id from marques where nom = ?)", (mauvais,)).fetchone()[0]
    if n == 0:
        c.execute("delete from marques where nom = ?", (mauvais,))
        print("marque supprimee :", mauvais)

basculer("Pok\u00e9mon", "Pokemon")
basculer("Stitch", "Lilo & Stitch")
c.commit()

q = "select m.nom, count(*) from produits p join marques m on m.id = p.marque_id join fournisseurs f on f.id = p.fournisseur_id where f.nom = ? group by 1 order by 1"
for r in c.execute(q, ("Stor",)):
    print(r)
