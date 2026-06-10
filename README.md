# 🧠 Santé Mentale au Travail — Dashboard Analytique

**Dashboard interactif sur le burnout et le bien-être professionnel à l'échelle mondiale (2019–2024)**

👉 **[Voir le dashboard en live](https://mental-health-work-dashboard.streamlit.app)**

---

## Pourquoi ce projet ?

La santé mentale au travail est devenue une priorité absolue pour les DRH et les décideurs — Grande Cause nationale 2025 en France, coût estimé à plus de 130 milliards d'euros par an pour l'économie française. Pourtant, beaucoup d'entreprises naviguent encore à l'aveugle, sans indicateurs clairs ni outil de pilotage.

Ce dashboard, c'est ma réponse à ça : transformer des données publiques (OCDE, OMS, DREES, INRS) en insights actionnables, avec un vrai angle business — pas juste des graphiques, mais des réponses aux questions que se posent réellement les décideurs.

---

## Ce que le dashboard permet de faire

**6 pages, chacune avec un objectif précis :**

- **Vue Globale** — Comparer 9 pays sur 6 ans, identifier les tendances mondiales du burnout, de l'anxiété et de la dépression au travail
- **Analyse France** — Zoomer sur les secteurs français : lequel est en crise ? lequel résiste ? Avec un score de risque composite calculé sur burnout + anxiété + turnover
- **Impact Économique** — Quantifier ce que coûte vraiment l'inaction : productivité perdue, absentéisme, coût par habitant, comparaison internationale
- **Profil Démographique** — Analyser les inégalités par âge et par genre, notamment l'écart femmes/hommes qui reste systématique sur toutes les tranches d'âge
- **Explorateur SQL** — Exécuter des requêtes SQL en direct sur la base de données (CTEs, window functions, pivots...) — parce que les données méritent d'être interrogées, pas juste affichées
- **ROI & Recommandations** — Le cœur du projet pour un DRH : simuler le retour sur investissement d'un programme de prévention, voir le classement bien-être mondial, et obtenir des recommandations concrètes par secteur

---

## Stack technique

| Outil | Usage |
|-------|-------|
| Python / Pandas | Traitement et manipulation des données |
| Streamlit | Interface web interactive |
| Plotly | Visualisations (line charts, bar charts, waterfall, radar, scatter) |
| SQLite (in-memory) | Base de données pour l'explorateur SQL |
| GitHub + Streamlit Cloud | Déploiement continu |

---

## Les données

Les données sont **synthétiques mais réalistes**, construites à partir des statistiques publiées par :
- **OCDE** — Work-Life Balance Index, absentéisme, comparaisons internationales
- **OMS** — Taux de burnout, anxiété et dépression par pays
- **DREES / INRS** — Données sectorielles France, arrêts de travail
- **Mercer / Deloitte** — Benchmarks coûts économiques et ROI prévention

4 tables, 9 pays, 8 secteurs, 6 ans de données, + de 500 lignes.

---

## Requêtes SQL incluses

Le fichier `queries.sql` contient 15 requêtes analytiques couvrant :

- Window functions (LAG, RANK, DENSE_RANK, NTILE, rolling average)
- CTEs imbriquées
- Pivots conditionnels (CASE WHEN)
- Jointures multi-tables
- Score composite normalisé (min-max)
- Simulation ROI avec sous-requêtes

---

## Structure du projet

├── app.py                           # Application Streamlit principale
├── queries.sql                      # Requêtes SQL analytiques
├── requirements.txt                 # Dépendances Python
├── mental_health_countries.csv      # Données internationales
├── mental_health_costs.csv          # Coûts économiques par pays
├── mental_health_sectors_france.csv # Données sectorielles France
└── mental_health_age_gender.csv     # Données démographiques

---

## Lancer le projet en local

git clone https://github.com/Thiziriinfo/Mental-Health-Dashboard
cd Mental-Health-Dashboard
pip install -r requirements.txt
streamlit run app.py

---

## Ce que j'ai appris

Ce projet m'a forcée à réfléchir différemment — pas juste "comment faire un joli graphique" mais "quelle question est-ce que ce graphique répond ?". Le simulateur ROI notamment : j'aurais pu juste afficher des chiffres statiques, mais le vrai besoin d'un DRH c'est de pouvoir jouer avec ses propres paramètres et voir l'impact en temps réel.

---

