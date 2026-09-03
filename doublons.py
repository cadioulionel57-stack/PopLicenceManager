import sqlite3
c = sqlite3.connect(r"C:\PopLicenceManager\database\poplicence.db")
sql = """
SELECT LTRIM(ean,'0') AS cle, COUNT(*) AS n,
       GROUP_CONCAT(id), GROUP_CONCAT(fournisseur_id), MIN(nom)
FROM produits
WHERE ean IS NOT NULL AND ean <> ''
GROUP BY cle HAVING n > 1
ORDER BY MIN(nom)
"""
lignes = list(c.execute(sql))
for r in lignes:
    print(r)
print("TOTAL doublons :", len(lignes))
