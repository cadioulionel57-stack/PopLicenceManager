r"""
modules/wizishop_api.py
------------------------------------------------------------
Connexion a l'API WiziShop v3.

LECTURE SEULE : ce module se connecte, liste les boutiques du
compte et liste les categories existantes. Il ne cree rien,
ne modifie rien, ne supprime rien.

Les identifiants sont lus et ecrits dans config_api.json, place
a la racine du projet (C:\PopLicenceManager\config_api.json).
Ce fichier contient le mot de passe en clair : il doit figurer
dans .gitignore et ne jamais partir sur GitHub.
------------------------------------------------------------
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "https://api.wizishop.com"
CONFIG_PATH = Path(__file__).parent.parent / "config_api.json"

# Duree de validite annoncee par WiziShop pour le jeton JWT
DUREE_JETON_JOURS = 30


class WiziShopAPIError(Exception):
    """Erreur d'appel a l'API, avec un message lisible en francais."""
    pass


class WiziShopAPI:

    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.config = self._lire_config()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _lire_config(self):
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as fichier:
                return json.load(fichier)
        except (json.JSONDecodeError, OSError):
            return {}

    def _ecrire_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as fichier:
                json.dump(self.config, fichier, indent=2, ensure_ascii=False)
        except OSError as erreur:
            raise WiziShopAPIError(
                "Impossible d'ecrire le fichier de configuration "
                f"{self.config_path} : {erreur}"
            )

    def enregistrer_identifiants(self, email, mot_de_passe):
        """Enregistre les identifiants et efface le jeton precedent."""
        self.config["email"] = (email or "").strip()
        self.config["mot_de_passe"] = mot_de_passe or ""
        self.config.pop("jeton", None)
        self.config.pop("jeton_expire_le", None)
        self._ecrire_config()

    @property
    def identifiants_presents(self):
        return bool(self.config.get("email") and self.config.get("mot_de_passe"))

    # ------------------------------------------------------------------
    # Authentification
    # ------------------------------------------------------------------

    def _jeton_encore_valable(self):
        jeton = self.config.get("jeton")
        expire_le = self.config.get("jeton_expire_le")
        if not jeton or not expire_le:
            return False
        try:
            # On renouvelle un jour avant l'expiration, par securite
            return datetime.fromisoformat(expire_le) > datetime.now() + timedelta(days=1)
        except ValueError:
            return False

    def se_connecter(self, forcer=False):
        """
        Renvoie un jeton valide.
        Reutilise celui deja enregistre s'il n'est pas expire.
        """
        if not forcer and self._jeton_encore_valable():
            return self.config["jeton"]

        if not self.identifiants_presents:
            raise WiziShopAPIError(
                "Aucun identifiant enregistre. Renseignez votre adresse e-mail "
                "et votre mot de passe WiziShop dans les reglages."
            )

        email = self.config["email"]
        mot_de_passe = self.config["mot_de_passe"]

        # La documentation ne precise pas le nom du champ identifiant.
        # On essaie les deux ecritures habituelles.
        derniere_erreur = None
        for champ in ("username", "email"):
            try:
                reponse = self._appel(
                    "POST",
                    "/v3/auth/login",
                    corps={champ: email, "password": mot_de_passe},
                    avec_jeton=False,
                )
            except WiziShopAPIError as erreur:
                derniere_erreur = erreur
                continue

            jeton = reponse.get("token")
            if not jeton:
                derniere_erreur = WiziShopAPIError(
                    "La connexion a reussi mais l'API n'a renvoye aucun jeton."
                )
                continue

            self.config["jeton"] = jeton
            self.config["jeton_expire_le"] = (
                datetime.now() + timedelta(days=DUREE_JETON_JOURS)
            ).isoformat()
            self.config["champ_identifiant"] = champ
            if reponse.get("account_id"):
                self.config["account_id"] = reponse["account_id"]
            self._ecrire_config()
            return jeton

        raise derniere_erreur or WiziShopAPIError("Connexion impossible.")

    # ------------------------------------------------------------------
    # Appel generique
    # ------------------------------------------------------------------

    def _appel(self, methode, chemin, corps=None, avec_jeton=True, tentative=1):
        url = BASE_URL + chemin
        entetes = {"Content-Type": "application/json"}

        if avec_jeton:
            entetes["Authorization"] = "Bearer " + self.se_connecter()

        donnees = None
        if corps is not None:
            donnees = json.dumps(corps).encode("utf-8")

        requete = urllib.request.Request(
            url, data=donnees, headers=entetes, method=methode
        )

        try:
            with urllib.request.urlopen(requete, timeout=30) as reponse:
                contenu = reponse.read().decode("utf-8")
                return json.loads(contenu) if contenu else {}

        except urllib.error.HTTPError as erreur:
            detail = ""
            try:
                detail = erreur.read().decode("utf-8")[:400]
            except Exception:
                pass

            if erreur.code == 429 and tentative <= 3:
                # Limite de debit : on attend puis on reessaie
                time.sleep(5 * tentative)
                return self._appel(methode, chemin, corps, avec_jeton, tentative + 1)

            messages = {
                400: "Requete incorrecte : l'API n'a pas compris la demande.",
                401: "Identifiants refuses ou jeton expire.",
                403: "Acces interdit : ce compte n'a pas les droits necessaires.",
                404: "Ressource introuvable.",
                405: "Cette methode n'existe pas sur l'API.",
                409: "Cette ressource existe deja.",
                422: "Donnees refusees par l'API (erreur de validation).",
                429: "Trop d'appels d'affilee, la limite de debit est atteinte.",
                500: "Erreur interne du serveur WiziShop.",
            }
            message = messages.get(erreur.code, f"Erreur HTTP {erreur.code}.")
            raise WiziShopAPIError(f"{message}\n\nDetail renvoye : {detail}")

        except urllib.error.URLError as erreur:
            raise WiziShopAPIError(
                f"Impossible de joindre l'API WiziShop : {erreur.reason}"
            )

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------

    def lister_boutiques(self):
        """Renvoie la liste des boutiques associees au compte."""
        self.se_connecter()
        account_id = self.config.get("account_id")
        if not account_id:
            raise WiziShopAPIError(
                "Identifiant de compte introuvable dans la reponse de connexion."
            )
        reponse = self._appel("GET", f"/v3/accounts/{account_id}/shops")
        if isinstance(reponse, list):
            return reponse
        return reponse.get("results") or reponse.get("resultats") or []

    def id_boutique(self):
        """Renvoie l'identifiant de la boutique, en le memorisant."""
        if self.config.get("shop_id"):
            return self.config["shop_id"]
        boutiques = self.lister_boutiques()
        if not boutiques:
            raise WiziShopAPIError("Aucune boutique trouvee sur ce compte.")
        self.config["shop_id"] = boutiques[0].get("id")
        self._ecrire_config()
        return self.config["shop_id"]

    def lister_categories(self):
        """Renvoie toutes les categories de la boutique, page par page."""
        shop_id = self.id_boutique()
        categories = []
        page = 1
        while True:
            reponse = self._appel(
                "GET", f"/v3/shops/{shop_id}/categories?page={page}&limit=100"
            )
            if isinstance(reponse, list):
                categories.extend(reponse)
                break
            lot = reponse.get("results") or reponse.get("resultats") or []
            categories.extend(lot)
            total_pages = reponse.get("pages") or 1
            if page >= total_pages or not lot:
                break
            page += 1
        return categories

    # ------------------------------------------------------------------
    # Test de connexion
    # ------------------------------------------------------------------

    def tester_connexion(self):
        """
        Fait le tour complet en lecture seule.
        Renvoie un texte lisible a afficher dans l'interface.
        """
        lignes = []
        self.se_connecter(forcer=True)
        lignes.append("Connexion reussie.")
        lignes.append(
            "Champ d'identifiant accepte : " + self.config.get("champ_identifiant", "?")
        )

        boutiques = self.lister_boutiques()
        lignes.append(f"Boutiques trouvees : {len(boutiques)}")
        for boutique in boutiques:
            lignes.append(
                f"   - id {boutique.get('id')} : {boutique.get('name') or boutique.get('nom') or 'sans nom'}"
            )

        categories = self.lister_categories()
        lignes.append(f"Categories existantes : {len(categories)}")
        if categories:
            lignes.append("Champs renvoyes par l'API pour la premiere categorie :")
            lignes.append("   " + ", ".join(sorted(categories[0].keys())))

        return "\n".join(lignes)