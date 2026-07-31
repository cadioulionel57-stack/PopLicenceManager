import sys
import traceback

from PySide6.QtWidgets import QApplication, QDateEdit
from PySide6.QtCore import QLocale

try:
    print("1")
    from database.init_database import initialiser

    print("2")
    from ui.main_window import MainWindow
    from ui.theme import appliquer as appliquer_theme

    print("3")
    initialiser()

    print("4")
    app = QApplication(sys.argv)

    # Force le point comme séparateur décimal partout dans
    # le logiciel (champs poids, prix, marge...) — sans ça,
    # les champs numériques suivent la langue de Windows et
    # attendent une virgule ; taper un point dedans produit
    # alors une valeur fausse sans aucun message d'erreur.
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    # Les dates, elles, doivent rester au format français.
    #
    # On ne peut pas simplement passer la langue en français :
    # ça réglerait les dates mais casserait tous les champs
    # numériques ci-dessus, qui attendraient alors la virgule.
    #
    # On agit donc uniquement sur les champs de date : chaque
    # champ créé dans le logiciel naît en JJ/MM/AAAA, y compris
    # dans les fenêtres ouvertes plus tard et dans celles qui
    # seront ajoutées à l'avenir.
    _init_date_origine = QDateEdit.__init__

    def _init_date_francais(self, *args, **kwargs):
        _init_date_origine(self, *args, **kwargs)
        self.setDisplayFormat("dd/MM/yyyy")

    QDateEdit.__init__ = _init_date_francais

    # Thème visuel unique du logiciel — tout le style est
    # défini dans ui/theme.py et appliqué ici, une seule
    # fois, pour l'ensemble des écrans et des fenêtres.
    appliquer_theme(app)

    print("5")
    window = MainWindow()

    print("6")
    window.show()

    print("7")
    sys.exit(app.exec())

except Exception:
    traceback.print_exc()