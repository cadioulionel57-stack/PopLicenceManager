"""
Import des emplacements de stockage depuis le collecteur (PTC).

Format attendu du fichier : une ligne par scan, dans l'ordre
    ligne 1 : code du PRODUIT       (EAN ou SKU)
    ligne 2 : code de l'EMPLACEMENT (commence par une lettre, ex. A01-01-07)
    ligne 3 : code du produit suivant
    ligne 4 : son emplacement
    ...

Un code d'emplacement est reconnu parce qu'il COMMENCE PAR UNE LETTRE.
Un EAN est purement numerique : aucune confusion possible.

Rien n'est ecrit en base tant que appliquer() n'est pas appele.
"""

import csv
import os
import re

from database.database import Database


# Un emplacement commence par une lettre, un EAN jamais.
_MOTIF_EMPLACEMENT = re.compile(r"^[A-Za-z]")


class EmplacementImportManager:
    """Lit un fichier de collecteur et attribue un emplacement a chaque produit."""

    def __init__(self):
        self.db = Database()

    # ------------------------------------------------------------------
    # Lecture du fichier
    # ------------------------------------------------------------------
    def lire_fichier(self, chemin):
        """
        Renvoie la liste brute des codes scannes, dans l'ordre du fichier.
        Accepte un fichier a une seule colonne ou a plusieurs (seule la
        premiere est lue). Le separateur est detecte automatiquement.
        """

        if not os.path.exists(chemin):
            raise FileNotFoundError("Fichier introuvable : %s" % chemin)

        with open(chemin, "r", encoding="utf-8-sig", errors="replace") as f:

            debut = f.read(4096)
            f.seek(0)

            separateur = ";"
            for candidat in (";", ",", "\t", "|"):
                if candidat in debut:
                    separateur = candidat
                    break

            codes = []
            for ligne in csv.reader(f, delimiter=separateur):

                if not ligne:
                    continue

                valeur = (ligne[0] or "").strip()

                if valeur:
                    codes.append(valeur)

        return codes

    # ------------------------------------------------------------------
    # Appariement produit / emplacement
    # ------------------------------------------------------------------
    def analyser(self, chemin):
        """
        Transforme la liste de codes en couples produit / emplacement,
        puis resout chaque code en produit de la base.

        Renvoie un dictionnaire :
            lignes    : liste de dicts prets a appliquer
            anomalies : messages sur les scans mal apparies
        """

        codes = self.lire_fichier(chemin)

        couples = []
        anomalies = []

        index = 0

        while index < len(codes):

            code = codes[index]

            # Un emplacement en premiere position = scan orphelin
            if _MOTIF_EMPLACEMENT.match(code):

                anomalies.append(
                    "Emplacement %s scanne sans produit devant "
                    "(scan n%d)" % (code, index + 1)
                )
                index += 1
                continue

            # Il faut un code d'emplacement juste apres
            if index + 1 >= len(codes):

                anomalies.append(
                    "Produit %s scanne en fin de fichier, "
                    "sans emplacement derriere" % code
                )
                break

            suivant = codes[index + 1]

            if not _MOTIF_EMPLACEMENT.match(suivant):

                anomalies.append(
                    "Produit %s suivi de %s, qui n'est pas un emplacement "
                    "(un emplacement commence par une lettre)"
                    % (code, suivant)
                )
                index += 1
                continue

            couples.append({
                "code": code,
                "emplacement": suivant.upper(),
            })

            index += 2

        return self._resoudre(couples, anomalies)

    # ------------------------------------------------------------------
    # Resolution des codes en produits
    # ------------------------------------------------------------------
    def _resoudre(self, couples, anomalies):

        lignes = []

        for couple in couples:

            code = couple["code"]
            emplacement = couple["emplacement"]

            ligne = {
                "code": code,
                "emplacement": emplacement,
                "produit_id": None,
                "nom": "",
                "ancien": "",
                "etat": "inconnu",
            }

            resultat = self.db.lire_un(
                "SELECT id, nom, emplacement FROM produits "
                "WHERE (ean = ? OR sku = ?) AND actif = 1 LIMIT 1",
                (code, code),
            )

            if resultat is not None:

                ligne["produit_id"] = resultat["id"]
                ligne["nom"] = resultat["nom"] or ""
                ligne["ancien"] = resultat["emplacement"] or ""

                if not ligne["ancien"]:
                    ligne["etat"] = "nouveau"

                elif ligne["ancien"].upper() == emplacement:
                    ligne["etat"] = "inchange"

                else:
                    ligne["etat"] = "deplace"

            lignes.append(ligne)

        return {"lignes": lignes, "anomalies": anomalies}

    # ------------------------------------------------------------------
    # Ecriture en base
    # ------------------------------------------------------------------
    def appliquer(self, lignes):
        """
        Ecrit les emplacements. Ignore les lignes sans produit reconnu
        et celles qui n'ont pas change. Renvoie le nombre de produits
        reellement mis a jour.
        """

        modifies = 0

        for ligne in lignes:

            if ligne.get("produit_id") is None:
                continue

            if ligne.get("etat") == "inchange":
                continue

            self.db.executer(
                "UPDATE produits SET emplacement = ? WHERE id = ?",
                (ligne["emplacement"], ligne["produit_id"]),
            )

            modifies += 1

        return modifies