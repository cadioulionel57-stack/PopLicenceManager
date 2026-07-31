import shutil

from datetime import datetime
from pathlib import Path

from database.database import Database


class PhotoCommandeManager:
    """
    Gère les photos rattachées à une commande : clichés du
    produit et du colis pris avant expédition, et photos de
    l'état d'un article au retour.

    Les images ne sont jamais stockées dans la base : elles
    sont copiées dans photos/commandes/<numero>/ à la racine
    du projet, et seule leur adresse est enregistrée.
    """

    def __init__(self):

        self.db = Database()

        self.racine = (
            Path(__file__).resolve().parent.parent
            / "photos"
            / "commandes"
        )

    def dossier_commande(self, numero_commande):
        """
        Renvoie le dossier de la commande, en le créant s'il
        n'existe pas encore.
        """

        numero = (numero_commande or "sans-numero").strip()

        for caractere in '\\/:*?"<>|':
            numero = numero.replace(caractere, "-")

        dossier = self.racine / numero

        dossier.mkdir(parents=True, exist_ok=True)

        return dossier

    def ajouter(
        self,
        commande_id,
        numero_commande,
        chemin_source,
        type_photo="expedition",
        commentaire=None,
    ):
        """
        Copie une photo dans le dossier de la commande et
        l'enregistre. Renvoie le chemin du fichier copié.
        """

        source = Path(chemin_source)

        if not source.exists():
            return None

        horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        nom_fichier = (
            f"{type_photo}_{horodatage}{source.suffix.lower()}"
        )

        destination = (
            self.dossier_commande(numero_commande) / nom_fichier
        )

        # Deux photos prises dans la même seconde ne doivent
        # pas s'écraser l'une l'autre.
        compteur = 1

        while destination.exists():

            destination = destination.with_name(
                f"{type_photo}_{horodatage}_{compteur}"
                f"{source.suffix.lower()}"
            )

            compteur += 1

        shutil.copy2(source, destination)

        self.db.executer(
            """
            INSERT INTO commandes_photos
            (commande_id, type, chemin, date_ajout,
             commentaire, actif)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                commande_id,
                type_photo,
                str(destination),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                commentaire,
            ),
        )

        return str(destination)

    def lister(self, commande_id, type_photo=None):
        """
        Renvoie les photos actives d'une commande, de la plus
        ancienne à la plus récente.
        """

        if commande_id is None:
            return []

        if type_photo is None:

            return self.db.lire(
                """
                SELECT * FROM commandes_photos
                WHERE commande_id = ? AND actif = 1
                ORDER BY date_ajout
                """,
                (commande_id,),
            )

        return self.db.lire(
            """
            SELECT * FROM commandes_photos
            WHERE commande_id = ? AND type = ? AND actif = 1
            ORDER BY date_ajout
            """,
            (commande_id, type_photo),
        )

    def supprimer(self, photo_id, effacer_fichier=True):
        """
        Retire la photo de la fiche. Le fichier lui-même
        n'est effacé du disque que si effacer_fichier est
        vrai.
        """

        ligne = self.db.lire_un(
            """
            SELECT chemin FROM commandes_photos WHERE id = ?
            """,
            (photo_id,),
        )

        self.db.executer(
            """
            UPDATE commandes_photos SET actif = 0 WHERE id = ?
            """,
            (photo_id,),
        )

        if effacer_fichier and ligne is not None:

            fichier = Path(ligne["chemin"])

            if fichier.exists():

                try:
                    fichier.unlink()
                except OSError:
                    pass

    def compter(self, commande_id):
        """
        Nombre de photos actives, pour afficher un compteur
        sans charger toute la liste.
        """

        if commande_id is None:
            return 0

        ligne = self.db.lire_un(
            """
            SELECT COUNT(*) AS total FROM commandes_photos
            WHERE commande_id = ? AND actif = 1
            """,
            (commande_id,),
        )

        return ligne["total"] if ligne else 0