import sqlite3
c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")
q = ("SELECT id, nom, html_template FROM modeles_fiche_produit "
     "WHERE html_template LIKE '%aracteristiques principales%' "
     "OR html_template LIKE '%aract\u00e9ristiques principales%'")
for r in c.execute(q):
    print("=====", r[0], r[1])
    i = r[2].lower().find("principales")
    print(repr(r[2][max(0, i - 400):i + 150]))
    print()