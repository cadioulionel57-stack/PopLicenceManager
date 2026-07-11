from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QScrollArea,
)
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
    QHorizontalBarSeries,
    QLineSeries,
    QDateTimeAxis,
)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

from modules.commande_manager import CommandeManager
from modules.tresorerie_manager import TresorerieManager


class StatistiquesPage(QWidget):
    """
    Graphiques de pilotage — pour l'instant, la répartition
    du CA par canal de vente, mois par mois.
    """

    COULEURS = [
        "#144b8b", "#1e7d32", "#e67e22", "#c0392b", "#8e44ad",
        "#0064d2", "#eaba00", "#0057a8", "#7b241c", "#16a085",
    ]

    def __init__(self):

        super().__init__()

        self.manager = CommandeManager()
        self.managerTresorerie = TresorerieManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
        QLabel#sousTitre{ font-size:15px; font-weight:600; color:#0f2f5c; }
        QFrame#card{
            background:white; border:1px solid #e1e8f0;
            border-radius:12px;
        }
        QComboBox{
            background:#f7f9fc; border:1px solid #d7e0ec;
            border-radius:7px; padding:6px 8px; font-size:10.5pt;
        }
        """)

        exterieur = QVBoxLayout(self)
        exterieur.setContentsMargins(0, 0, 0, 0)

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet(
            "QScrollArea{border:none; background:transparent;}"
        )

        contenuDefilant = QWidget()
        layout = QVBoxLayout(contenuDefilant)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        zoneDefilement.setWidget(contenuDefilant)
        exterieur.addWidget(zoneDefilement)

        entete = QHBoxLayout()
        titre = QLabel("📊 Statistiques")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        ####################################################
        # Répartition du CA par canal
        ####################################################

        carte = QFrame()
        carte.setObjectName("card")
        layoutCarte = QVBoxLayout(carte)

        entêteGraphique = QHBoxLayout()

        titreGraphique = QLabel("🥧 Répartition du CA par canal de vente")
        titreGraphique.setObjectName("sousTitre")
        entêteGraphique.addWidget(titreGraphique)

        entêteGraphique.addStretch()

        entêteGraphique.addWidget(QLabel("Mois :"))

        self.selecteurMois = QComboBox()
        self.selecteurMois.currentIndexChanged.connect(
            self.rafraichirCamembert
        )
        entêteGraphique.addWidget(self.selecteurMois)

        layoutCarte.addLayout(entêteGraphique)

        self.labelVide = QLabel(
            "Aucune commande pour ce mois — rien à répartir."
        )
        self.labelVide.setStyleSheet("color:#7f8c8d; padding:20px;")
        layoutCarte.addWidget(self.labelVide)

        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chartView.setMinimumHeight(420)
        layoutCarte.addWidget(self.chartView)

        layout.addWidget(carte)

        ####################################################
        # Évolution du CA dans le temps
        ####################################################

        carteEvolution = QFrame()
        carteEvolution.setObjectName("card")
        layoutEvolution = QVBoxLayout(carteEvolution)

        entêteEvolution = QHBoxLayout()

        titreEvolution = QLabel("📈 Évolution du CA — mois par mois")
        titreEvolution.setObjectName("sousTitre")
        entêteEvolution.addWidget(titreEvolution)

        entêteEvolution.addStretch()

        entêteEvolution.addWidget(QLabel("Année :"))

        self.selecteurAnnee = QComboBox()
        self.selecteurAnnee.currentIndexChanged.connect(
            self.rafraichirEvolution
        )
        entêteEvolution.addWidget(self.selecteurAnnee)

        layoutEvolution.addLayout(entêteEvolution)

        self.chartViewEvolution = QChartView()
        self.chartViewEvolution.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewEvolution.setMinimumHeight(380)
        layoutEvolution.addWidget(self.chartViewEvolution)

        layout.addWidget(carteEvolution)

        ####################################################
        # Meilleures ventes par licence
        ####################################################

        carteLicences = QFrame()
        carteLicences.setObjectName("card")
        layoutLicences = QVBoxLayout(carteLicences)

        entêteLicences = QHBoxLayout()

        titreLicences = QLabel("🏆 Meilleures ventes par licence (CA)")
        titreLicences.setObjectName("sousTitre")
        entêteLicences.addWidget(titreLicences)

        entêteLicences.addStretch()

        entêteLicences.addWidget(QLabel("Mois :"))

        self.selecteurMoisLicences = QComboBox()
        self.selecteurMoisLicences.currentIndexChanged.connect(
            self.rafraichirLicences
        )
        entêteLicences.addWidget(self.selecteurMoisLicences)

        layoutLicences.addLayout(entêteLicences)

        self.labelVideLicences = QLabel(
            "Aucune vente avec licence pour ce mois."
        )
        self.labelVideLicences.setStyleSheet("color:#7f8c8d; padding:20px;")
        layoutLicences.addWidget(self.labelVideLicences)

        self.chartViewLicences = QChartView()
        self.chartViewLicences.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewLicences.setMinimumHeight(380)
        layoutLicences.addWidget(self.chartViewLicences)

        layout.addWidget(carteLicences)

        ####################################################
        # Bénéfice net par canal
        ####################################################

        carteBenefice = QFrame()
        carteBenefice.setObjectName("card")
        layoutBenefice = QVBoxLayout(carteBenefice)

        entêteBenefice = QHBoxLayout()

        titreBenefice = QLabel("💰 Bénéfice net par canal")
        titreBenefice.setObjectName("sousTitre")
        entêteBenefice.addWidget(titreBenefice)

        entêteBenefice.addStretch()

        entêteBenefice.addWidget(QLabel("Mois :"))

        self.selecteurMoisBenefice = QComboBox()
        self.selecteurMoisBenefice.currentIndexChanged.connect(
            self.rafraichirBenefice
        )
        entêteBenefice.addWidget(self.selecteurMoisBenefice)

        layoutBenefice.addLayout(entêteBenefice)

        self.labelVideBenefice = QLabel(
            "Aucune commande pour ce mois."
        )
        self.labelVideBenefice.setStyleSheet("color:#7f8c8d; padding:20px;")
        layoutBenefice.addWidget(self.labelVideBenefice)

        self.chartViewBenefice = QChartView()
        self.chartViewBenefice.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewBenefice.setMinimumHeight(380)
        layoutBenefice.addWidget(self.chartViewBenefice)

        layout.addWidget(carteBenefice)

        ####################################################
        # Évolution de la trésorerie (solde bancaire)
        ####################################################

        carteTresorerie = QFrame()
        carteTresorerie.setObjectName("card")
        layoutTresorerie = QVBoxLayout(carteTresorerie)

        titreTresorerie = QLabel("🏦 Évolution du solde bancaire")
        titreTresorerie.setObjectName("sousTitre")
        layoutTresorerie.addWidget(titreTresorerie)

        self.labelVideTresorerie = QLabel(
            "Aucun solde saisi pour l'instant — renseigne ton "
            "solde du jour dans Trésorerie pour voir apparaître "
            "cette courbe."
        )
        self.labelVideTresorerie.setStyleSheet(
            "color:#7f8c8d; padding:20px;"
        )
        self.labelVideTresorerie.setWordWrap(True)
        layoutTresorerie.addWidget(self.labelVideTresorerie)

        self.chartViewTresorerie = QChartView()
        self.chartViewTresorerie.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewTresorerie.setMinimumHeight(380)
        layoutTresorerie.addWidget(self.chartViewTresorerie)

        layout.addWidget(carteTresorerie)

        ####################################################
        # Répartition des coûts liés aux ventes
        ####################################################

        carteCharges = QFrame()
        carteCharges.setObjectName("card")
        layoutCharges = QVBoxLayout(carteCharges)

        entêteCharges = QHBoxLayout()

        titreCharges = QLabel("🥧 Répartition des coûts liés aux ventes")
        titreCharges.setObjectName("sousTitre")
        entêteCharges.addWidget(titreCharges)

        entêteCharges.addStretch()

        entêteCharges.addWidget(QLabel("Mois :"))

        self.selecteurMoisCharges = QComboBox()
        self.selecteurMoisCharges.currentIndexChanged.connect(
            self.rafraichirCharges
        )
        entêteCharges.addWidget(self.selecteurMoisCharges)

        layoutCharges.addLayout(entêteCharges)

        self.labelVideCharges = QLabel(
            "Aucune commande pour ce mois."
        )
        self.labelVideCharges.setStyleSheet("color:#7f8c8d; padding:20px;")
        layoutCharges.addWidget(self.labelVideCharges)

        self.chartViewCharges = QChartView()
        self.chartViewCharges.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewCharges.setMinimumHeight(420)
        layoutCharges.addWidget(self.chartViewCharges)

        layout.addWidget(carteCharges)

        layout.addStretch()

        self.charger()

    def charger(self):

        mois_disponibles = self.manager.mois_avec_commandes()

        self.selecteurMois.blockSignals(True)
        self.selecteurMois.clear()

        if not mois_disponibles:

            mois_disponibles = [date.today().strftime("%Y-%m")]

        for mois in mois_disponibles:
            self.selecteurMois.addItem(mois, mois)

        self.selecteurMois.blockSignals(False)

        self.rafraichirCamembert()

        annees_disponibles = self.manager.annees_disponibles()

        self.selecteurAnnee.blockSignals(True)
        self.selecteurAnnee.clear()

        if not annees_disponibles:
            annees_disponibles = [str(date.today().year)]

        for annee in annees_disponibles:
            self.selecteurAnnee.addItem(annee, annee)

        self.selecteurAnnee.blockSignals(False)

        self.rafraichirEvolution()

        self.selecteurMoisLicences.blockSignals(True)
        self.selecteurMoisLicences.clear()

        for mois in mois_disponibles:
            self.selecteurMoisLicences.addItem(mois, mois)

        self.selecteurMoisLicences.blockSignals(False)

        self.rafraichirLicences()

        self.selecteurMoisBenefice.blockSignals(True)
        self.selecteurMoisBenefice.clear()

        for mois in mois_disponibles:
            self.selecteurMoisBenefice.addItem(mois, mois)

        self.selecteurMoisBenefice.blockSignals(False)

        self.rafraichirBenefice()

        self.rafraichirTresorerie()

        self.selecteurMoisCharges.blockSignals(True)
        self.selecteurMoisCharges.clear()

        for mois in mois_disponibles:
            self.selecteurMoisCharges.addItem(mois, mois)

        self.selecteurMoisCharges.blockSignals(False)

        self.rafraichirCharges()

    def rafraichirCharges(self):

        mois = self.selecteurMoisCharges.currentData()

        if mois is None:
            return

        donnees = self.manager.repartition_charges_mois(mois)

        if not donnees:

            self.labelVideCharges.setVisible(True)
            self.chartViewCharges.setVisible(False)
            return

        self.labelVideCharges.setVisible(False)
        self.chartViewCharges.setVisible(True)

        series = QPieSeries()

        for i, item in enumerate(donnees):

            tranche = series.append(
                f"{item['poste']} ({item['montant_ht']:.0f} € HT)",
                item["montant_ht"]
            )
            tranche.setLabelVisible(True)
            tranche.setColor(QColor(self.COULEURS[i % len(self.COULEURS)]))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Répartition des coûts liés aux ventes — {mois}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.chartViewCharges.setChart(chart)

    def rafraichirTresorerie(self):

        historique = self.managerTresorerie.historique_soldes(limite=90)

        if not historique:

            self.labelVideTresorerie.setVisible(True)
            self.chartViewTresorerie.setVisible(False)
            return

        self.labelVideTresorerie.setVisible(False)
        self.chartViewTresorerie.setVisible(True)

        # Du plus ancien au plus récent, pour que la courbe
        # se lise naturellement de gauche à droite.
        historique = list(reversed(historique))

        from PySide6.QtCore import QDateTime, QDate, QTime

        series = QLineSeries()
        series.setColor(QColor("#144b8b"))

        for point in historique:

            annee, mois, jour = (int(x) for x in point["date"].split("-"))
            instant = QDateTime(QDate(annee, mois, jour), QTime(0, 0, 0))

            series.append(
                instant.toMSecsSinceEpoch(), point["solde_ttc"]
            )

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Évolution du solde bancaire")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(False)

        axeX = QDateTimeAxis()
        axeX.setFormat("dd/MM/yy")
        axeX.setTitleText("Date")
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        valeurs = [p["solde_ttc"] for p in historique]
        valeur_max = max(valeurs) if valeurs else 100
        valeur_min = min(valeurs) if valeurs else 0

        axeY = QValueAxis()
        axeY.setRange(
            valeur_min * 0.9 if valeur_min > 0 else valeur_min * 1.1,
            valeur_max * 1.1
        )
        axeY.setLabelFormat("%.0f €")
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        self.chartViewTresorerie.setChart(chart)

    def rafraichirBenefice(self):

        mois = self.selecteurMoisBenefice.currentData()

        if mois is None:
            return

        donnees = self.manager.benefice_par_canal(mois)

        if not donnees:

            self.labelVideBenefice.setVisible(True)
            self.chartViewBenefice.setVisible(False)
            return

        self.labelVideBenefice.setVisible(False)
        self.chartViewBenefice.setVisible(True)

        canaux = [d["canal"] for d in donnees]

        # Deux séries séparées (positif / négatif) pour que
        # les canaux déficitaires ressortent en rouge et les
        # rentables en vert, sans que la charge graphique ne
        # permette de colorer chaque barre individuellement
        # dans une même série.
        valeurs_positives = [
            max(d["benefice_ht"], 0) for d in donnees
        ]
        valeurs_negatives = [
            min(d["benefice_ht"], 0) for d in donnees
        ]

        setPositif = QBarSet("Bénéfice")
        setPositif.append(valeurs_positives)
        setPositif.setColor(QColor("#1e7d32"))

        setNegatif = QBarSet("Perte")
        setNegatif.append(valeurs_negatives)
        setNegatif.setColor(QColor("#c0392b"))

        series = QBarSeries()
        series.append(setPositif)
        series.append(setNegatif)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Bénéfice net par canal — {mois}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(False)

        axeX = QBarCategoryAxis()
        axeX.append(canaux)
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        toutes_valeurs = valeurs_positives + valeurs_negatives
        valeur_max = max(toutes_valeurs) if toutes_valeurs else 100
        valeur_min = min(toutes_valeurs) if toutes_valeurs else 0

        axeY = QValueAxis()
        axeY.setRange(
            valeur_min * 1.15 if valeur_min < 0 else 0,
            valeur_max * 1.15 if valeur_max > 0 else 100
        )
        axeY.setLabelFormat("%.0f €")
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        self.chartViewBenefice.setChart(chart)

    def rafraichirLicences(self):

        mois = self.selecteurMoisLicences.currentData()

        if mois is None:
            return

        donnees = self.manager.ca_par_licence(mois)

        if not donnees:

            self.labelVideLicences.setVisible(True)
            self.chartViewLicences.setVisible(False)
            return

        self.labelVideLicences.setVisible(False)
        self.chartViewLicences.setVisible(True)

        # Du plus petit au plus grand, pour qu'un classement
        # en barres horizontales affiche le meilleur en haut.
        donnees = list(reversed(donnees))

        licences = [d["licence"] for d in donnees]
        valeurs = [d["ca_ht"] for d in donnees]

        barSet = QBarSet("CA HT")
        barSet.append(valeurs)
        barSet.setColor(QColor("#1e7d32"))

        series = QHorizontalBarSeries()
        series.append(barSet)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Meilleures licences — {mois}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(False)

        axeY = QBarCategoryAxis()
        axeY.append(licences)
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        valeur_max = max(valeurs) if valeurs else 100

        axeX = QValueAxis()
        axeX.setRange(0, valeur_max * 1.15 if valeur_max > 0 else 100)
        axeX.setLabelFormat("%.0f €")
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        self.chartViewLicences.setChart(chart)

    def rafraichirEvolution(self):

        annee = self.selecteurAnnee.currentData()

        if annee is None:
            return

        donnees = self.manager.ca_par_mois_annee(annee)

        mois = [d["mois"] for d in donnees]
        valeurs = [d["ca_ht"] for d in donnees]

        barSet = QBarSet("CA HT")
        barSet.append(valeurs)
        barSet.setColor(QColor("#1e88c7"))

        series = QBarSeries()
        series.append(barSet)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"CA mensuel — {annee}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(False)

        axeX = QBarCategoryAxis()
        axeX.append(mois)
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        valeur_max = max(valeurs) if valeurs else 100

        axeY = QValueAxis()
        axeY.setRange(0, valeur_max * 1.15 if valeur_max > 0 else 100)
        axeY.setLabelFormat("%.0f €")
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        self.chartViewEvolution.setChart(chart)

    def rafraichirCamembert(self):

        mois = self.selecteurMois.currentData()

        if mois is None:
            return

        donnees = self.manager.ca_par_canal(mois)

        if not donnees:

            self.labelVide.setVisible(True)
            self.chartView.setVisible(False)
            return

        self.labelVide.setVisible(False)
        self.chartView.setVisible(True)

        series = QPieSeries()

        for i, item in enumerate(donnees):

            tranche = series.append(
                f"{item['canal']} ({item['ca_ht']:.0f} € HT)",
                item["ca_ht"]
            )
            tranche.setLabelVisible(True)
            tranche.setColor(QColor(self.COULEURS[i % len(self.COULEURS)]))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Répartition du CA — {mois}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.chartView.setChart(chart)