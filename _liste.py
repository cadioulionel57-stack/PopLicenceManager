import sqlite3
c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")
h = c.execute("SELECT html_template FROM modeles_fiche_produit WHERE id=40").fetchone()[0]
i = h.lower().find("principales")
print(repr(h[max(0,i-500):i+200]))
