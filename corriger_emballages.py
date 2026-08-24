import sqlite3
c = sqlite3.connect("database/poplicence.db")
c.row_factory = sqlite3.Row

def emb(code):
    r = c.execute("select id from grille_emballage where code = ?", (code,)).fetchone()
    return r["id"] if r else None

print("=== 1. NOUVEAUX EMBALLAGES ===")
for code, nom, L, l, h, poids, cout, calage in [
    ("P4", "Pochette d'expedition L", 45, 35, 1, 55, 0.42, 0.00),
    ("F1", "Carton fourreau long", 50, 10, 10, 180, 0.75, 0.10),
]:
    if emb(code):
        print("  deja present :", code)
    else:
        c.execute(
            "insert into grille_emballage "
            "(code, nom, longueur_ext_cm, largeur_ext_cm, hauteur_ext_cm, "
            "poids_g, cout_ht, calage_ht) values (?,?,?,?,?,?,?,?)",
            (code, nom, L, l, h, poids, cout, calage))
        print("  cree :", code, nom)

print()
print("=== 2. FAMILLES ===")
CORRECTIONS = [("%Linge de maison%", "C3"), ("%Funko%", "C1")]
familles_touchees = []
for motif, code in CORRECTIONS:
    i = emb(code)
    for f in c.execute("select id, nom from familles_produit where nom like ?", (motif,)):
        familles_touchees.append((f["id"], i))
        print("  %-55s -> %s" % (f["nom"][:55], code))
    c.execute("update familles_produit set emballage_id = ? where nom like ?", (i, motif))

print()
print("=== 3. FICHES PRODUIT (hors WiziShop) ===")
for famille_id, emballage_id in familles_touchees:
    n = c.execute(
        "update produits set emballage_id = ? "
        "where famille_produit_id = ? and (id_wizishop is null or id_wizishop = '')",
        (emballage_id, famille_id)).rowcount
    bloques = c.execute(
        "select count(*) from produits where famille_produit_id = ? "
        "and id_wizishop is not null and id_wizishop <> ''",
        (famille_id,)).fetchone()[0]
    print("  famille %s : %d produit(s) corrige(s), %d laisse(s) (deja dans WiziShop)"
          % (famille_id, n, bloques))

print()
print("=== 4. DOUBLON FAMILLE ACCESSOIRES ===")
lignes = c.execute(
    "select id, nom from familles_produit "
    "where nom like '%ccessoires taille unique%' order by id").fetchall()
for r in lignes:
    print("  trouve :", r["id"], r["nom"])
if len(lignes) > 1:
    garde = lignes[0]["id"]
    for r in lignes[1:]:
        c.execute("update produits set famille_produit_id = ? where famille_produit_id = ?",
                  (garde, r["id"]))
        c.execute("delete from familles_produit where id = ?", (r["id"],))
        print("  supprime :", r["id"])
else:
    print("  pas de doublon")

c.commit()

print()
print("=== GRILLE FINALE ===")
for r in c.execute("select code, nom, longueur_ext_cm, largeur_ext_cm, "
                   "hauteur_ext_cm, cout_ht from grille_emballage order by code"):
    print("  %-4s %-34s %3.0f x %3.0f x %3.0f   %.2f EUR" % (
        r["code"], r["nom"][:34], r["longueur_ext_cm"],
        r["largeur_ext_cm"], r["hauteur_ext_cm"], r["cout_ht"]))
