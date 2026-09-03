import sqlite3, re, shutil, datetime

base = r"C:\PopLicenceManager\database\poplicence.db"
copie = r"C:\SauvegardeBase\poplicence_avant_retrait_carac_%s.db" % datetime.datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy2(base, copie)
print("Sauvegarde :", copie)

c = sqlite3.connect(base)
c.row_factory = sqlite3.Row

motif = re.compile(
    r"\s*<!--\s*CARACT[^>]*-->.*?Caract[eé]ristiques principales.*?</ul>\s*</div>",
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
print("Templates modifies :", touches)
