import sqlite3
c = sqlite3.connect('poplicence.db')
for r in c.execute("SELECT id, html_template FROM modeles_fiche_produit WHERE id IN (5,20)"):
    open(f"template_{r[0]}.txt", "w", encoding="utf-8").write(r[1])
    print("ecrit template_%s.txt" % r[0])
