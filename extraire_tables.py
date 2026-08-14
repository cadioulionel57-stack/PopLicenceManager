import sqlite3
tables = ["marques","categories_site","themes_template","fournisseurs","emballages","canaux_vente","licences","univers"]
c = sqlite3.connect("database/poplicence.db")
with open("tables.txt", "w", encoding="utf-8") as f:
    for t in tables:
        try:
            cur = c.execute("SELECT * FROM " + t)
            cols = [d[0] for d in cur.description]
            f.write("=== " + t + " === " + str(cols) + "\n")
            for r in cur.fetchall():
                f.write(str(r) + "\n")
            f.write("\n")
        except Exception as e:
            f.write("=== " + t + " === TABLE ABSENTE : " + str(e) + "\n\n")
print("Fichier cree : C:\\PopLicenceManager\\tables.txt")
