import sqlite3, re, shutil, datetime

base = r"C:\PopLicenceManager\database\poplicence.db"
copie = r"C:\SauvegardeBase\poplicence_avant_carac2_%s.db" % datetime.datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy2(base, copie)
print("Sauvegarde :", copie)

c = sqlite3.connect(base)
c.row_factory = sqlite3.Row

motif = re.compile(
    r"\s*<!--[^>]*CARACT[^>]*-->\s*<div[^>]*>.*?Caract[e\u00e9]ristiques principales.*?</ul>\s*</div>",
    re.IGNORECASE | re.DOTALL,
)

touches = 0
for r in c.execute("SELECT id, nom, html_template FROM modeles_fiche_produit").fetchall():
    h = r["html_template"] or ""
    n = motif.sub("", h)
    if n != h:
        c.execute("UPDATE modeles_fiche_produit SET html_template=? WHERE id=?", (n, r["id"]))
        touches += 1
        print("  retire :", r["id"], r["nom"])

c.commit()

restants = c.execute(
    "SELECT count(*) FROM modeles_fiche_produit "
    "WHERE html_template LIKE '%aracteristiques principales%' "
    "OR html_template LIKE '%aract\u00e9ristiques principales%'"
).fetchone()[0]

print("Templates modifies :", touches)
print("Restants a traiter :", restants)