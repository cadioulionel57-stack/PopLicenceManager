"""
ui/reglages_api.py
------------------------------------------------------------
Ecran de reglages de la connexion a l'API WiziShop.

Trois choses : saisir l'adresse e-mail, saisir le mot de passe,
tester la connexion. Rien n'est cree ni modifie sur la boutique,
le test est en lecture seule.

Peut se lancer seul :  python ui\\reglages_api.py
------------------------------------------------------------
"""

import sys
from pathlib import Path

# Permet de retrouver le dossier modules/ meme quand ce fichier
# est lance directement depuis le dossier ui/
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QPlainTextEdit,
    QMessageBox,
)
from PySide6.QtGui import QFont

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError


class ReglagesAPIDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion à l'API WiziShop")
        self.setMinimumWidth(620)

        self.api = WiziShopAPI()

        disposition = QVBoxLayout(self)

        titre = QLabel("Connexion à l'API WiziShop")
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        titre.setFont(police)
        disposition.addWidget(titre)

        explication = QLabel(
            "Saisissez les identifiants de votre espace d'administration WiziShop.\n"
            "Ils sont enregistrés dans config_api.json, sur cet ordinateur uniquement."
        )
        explication.setWordWrap(True)
        disposition.addWidget(explication)

        formulaire = QFormLayout()
        formulaire.setContentsMargins(0, 12, 0, 12)

        self.champ_email = QLineEdit()
        self.champ_email.setPlaceholderText("votre adresse e-mail WiziShop")
        formulaire.addRow("Adresse e-mail :", self.champ_email)

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.setPlaceholderText("votre mot de passe WiziShop")
        formulaire.addRow("Mot de passe :", self.champ_mot_de_passe)

        disposition.addLayout(formulaire)

        boutons = QHBoxLayout()
        self.bouton_enregistrer = QPushButton("Enregistrer")
        self.bouton_tester = QPushButton("Tester la connexion")
        self.bouton_fermer = QPushButton("Fermer")
        boutons.addWidget(self.bouton_enregistrer)
        boutons.addWidget(self.bouton_tester)
        boutons.addStretch()
        boutons.addWidget(self.bouton_fermer)
        disposition.addLayout(boutons)

        disposition.addWidget(QLabel("Résultat du test :"))
        self.zone_resultat = QPlainTextEdit()
        self.zone_resultat.setReadOnly(True)
        self.zone_resultat.setMinimumHeight(220)
        disposition.addWidget(self.zone_resultat)

        self.bouton_enregistrer.clicked.connect(self.enregistrer)
        self.bouton_tester.clicked.connect(self.tester)
        self.bouton_fermer.clicked.connect(self.close)

        self.charger_valeurs()

    def charger_valeurs(self):
        """Réaffiche les identifiants déjà enregistrés, s'il y en a."""
        self.champ_email.setText(self.api.config.get("email", ""))
        self.champ_mot_de_passe.setText(self.api.config.get("mot_de_passe", ""))

    def enregistrer(self):
        email = self.champ_email.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not email or not mot_de_passe:
            QMessageBox.warning(
                self, "Champs vides",
                "Renseignez l'adresse e-mail et le mot de passe avant d'enregistrer."
            )
            return

        try:
            self.api.enregistrer_identifiants(email, mot_de_passe)
        except WiziShopAPIError as erreur:
            QMessageBox.critical(self, "Erreur", str(erreur))
            return

        self.zone_resultat.setPlainText(
            "Identifiants enregistrés dans :\n"
            f"{self.api.config_path}\n\n"
            "Vous pouvez maintenant tester la connexion."
        )

    def tester(self):
        email = self.champ_email.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not email or not mot_de_passe:
            QMessageBox.warning(
                self, "Champs vides",
                "Renseignez l'adresse e-mail et le mot de passe avant de tester."
            )
            return

        # On enregistre avant de tester, pour utiliser les valeurs affichées
        try:
            self.api.enregistrer_identifiants(email, mot_de_passe)
        except WiziShopAPIError as erreur:
            QMessageBox.critical(self, "Erreur", str(erreur))
            return

        self.bouton_tester.setEnabled(False)
        self.zone_resultat.setPlainText("Test en cours, patientez...")
        QApplication.processEvents()

        try:
            resultat = self.api.tester_connexion()
            self.zone_resultat.setPlainText(resultat)
        except WiziShopAPIError as erreur:
            self.zone_resultat.setPlainText("ECHEC DU TEST\n\n" + str(erreur))
        except Exception as erreur:
            self.zone_resultat.setPlainText(
                "ECHEC DU TEST (erreur inattendue)\n\n"
                f"{type(erreur).__name__} : {erreur}"
            )
        finally:
            self.bouton_tester.setEnabled(True)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    fenetre = ReglagesAPIDialog()
    fenetre.show()
    sys.exit(application.exec())