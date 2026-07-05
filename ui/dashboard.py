from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        titre = QLabel("🏠 Tableau de bord")
        titre.setAlignment(Qt.AlignCenter)

        titre.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
            color:#1E5AA8;
            padding:20px;
        """)

        layout.addWidget(titre)

        texte = QLabel(
            "Bienvenue dans Pop Licence Manager\n\n"
            "Version 1.0"
        )

        texte.setAlignment(Qt.AlignCenter)

        texte.setStyleSheet("""
            font-size:16px;
            color:#555;
        """)

        layout.addWidget(texte)
        layout.addStretch()