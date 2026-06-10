-- =============================================================
--  MENTAL HEALTH AT WORK — SQL Analysis
--  Author  : Thiziri Abchiche | Data Analyst
--  Dataset : OCDE · OMS · DREES · INRS (2019-2024)
--  DB      : SQLite  (mental_health.db)
-- =============================================================


-- ─────────────────────────────────────────────────────────────
-- 1. APERÇU GLOBAL — Taux moyen de burnout par pays (2019-2024)
-- ─────────────────────────────────────────────────────────────
SELECT
    Country,
    Region,
    ROUND(AVG(Burnout_Rate_pct), 2)         AS avg_burnout_pct,
    ROUND(AVG(Anxiety_Rate_pct), 2)         AS avg_anxiety_pct,
    ROUND(AVG(Depression_Rate_pct), 2)      AS avg_depression_pct,
    ROUND(AVG(Absenteeism_Days_per_employee), 1) AS avg_absence_days
FROM countries
GROUP BY Country, Region
ORDER BY avg_burnout_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- 2. TENDANCE — Évolution YoY du taux de burnout (France)
-- ─────────────────────────────────────────────────────────────
SELECT
    Year,
    Burnout_Rate_pct,
    LAG(Burnout_Rate_pct) OVER (ORDER BY Year)  AS prev_year,
    ROUND(Burnout_Rate_pct
          - LAG(Burnout_Rate_pct) OVER (ORDER BY Year), 2) AS yoy_change_pts,
    CASE
        WHEN Burnout_Rate_pct > LAG(Burnout_Rate_pct) OVER (ORDER BY Year) THEN '▲ hausse'
        WHEN Burnout_Rate_pct < LAG(Burnout_Rate_pct) OVER (ORDER BY Year) THEN '▼ baisse'
        ELSE '= stable'
    END AS tendance
FROM countries
WHERE Country = 'France'
ORDER BY Year;


-- ─────────────────────────────────────────────────────────────
-- 3. CLASSEMENT — Top 3 pays les plus touchés chaque année
-- ─────────────────────────────────────────────────────────────
WITH ranked AS (
    SELECT
        Year,
        Country,
        Burnout_Rate_pct,
        RANK() OVER (PARTITION BY Year ORDER BY Burnout_Rate_pct DESC) AS rnk
    FROM countries
)
SELECT Year, Country, Burnout_Rate_pct, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY Year, rnk;


-- ─────────────────────────────────────────────────────────────
-- 4. CORRÉLATION — Work-Life Balance vs Burnout (2024)
-- ─────────────────────────────────────────────────────────────
SELECT
    Country,
    Work_Life_Balance_Index,
    Burnout_Rate_pct,
    CASE
        WHEN Work_Life_Balance_Index >= 7 THEN 'Excellent WLB'
        WHEN Work_Life_Balance_Index >= 5.5 THEN 'Bon WLB'
        ELSE 'WLB fragile'
    END AS wlb_category,
    ROUND(Presenteeism_Cost_USD / 1000.0, 1) AS presenteeism_k_usd
FROM countries
WHERE Year = 2024
ORDER BY Work_Life_Balance_Index DESC;


-- ─────────────────────────────────────────────────────────────
-- 5. SECTEURS FRANCE — Secteurs les plus à risque en 2024
-- ─────────────────────────────────────────────────────────────
SELECT
    Secteur,
    Taux_Burnout_pct,
    Taux_Anxiete_pct,
    Jours_Absence_moy,
    Cout_par_employe_EUR,
    Taux_Turnover_pct,
    ROUND(Taux_Burnout_pct * 0.4
        + Taux_Anxiete_pct * 0.3
        + Taux_Turnover_pct * 0.3, 2) AS risk_score,
    DENSE_RANK() OVER (ORDER BY
        Taux_Burnout_pct * 0.4
        + Taux_Anxiete_pct * 0.3
        + Taux_Turnover_pct * 0.3 DESC) AS risk_rank
FROM sectors_france
WHERE Annee = 2024
ORDER BY risk_score DESC;


-- ─────────────────────────────────────────────────────────────
-- 6. COÛT ÉCONOMIQUE — Décomposition par pays (2024)
-- ─────────────────────────────────────────────────────────────
SELECT
    Pays,
    Cout_Total_Mds_EUR,
    Perte_Productivite_Mds_EUR,
    Cout_Sante_Mds_EUR,
    Cout_Absenteisme_Mds_EUR,
    ROUND(Perte_Productivite_Mds_EUR * 100.0 / Cout_Total_Mds_EUR, 1) AS pct_productivite,
    ROUND(Cout_Sante_Mds_EUR * 100.0 / Cout_Total_Mds_EUR, 1)         AS pct_sante,
    ROUND(Cout_Absenteisme_Mds_EUR * 100.0 / Cout_Total_Mds_EUR, 1)   AS pct_absenteisme,
    Cout_par_habitant_EUR
FROM costs
WHERE Annee = 2024
ORDER BY Cout_Total_Mds_EUR DESC;


-- ─────────────────────────────────────────────────────────────
-- 7. WINDOW FUNCTION — Cumul des coûts France sur 6 ans
-- ─────────────────────────────────────────────────────────────
SELECT
    Annee,
    Cout_Total_Mds_EUR,
    SUM(Cout_Total_Mds_EUR) OVER (
        PARTITION BY Pays ORDER BY Annee
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumul_cout_mds,
    ROUND(AVG(Cout_Total_Mds_EUR) OVER (
        PARTITION BY Pays ORDER BY Annee
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_avg_3y
FROM costs
WHERE Pays = 'France'
ORDER BY Annee;


-- ─────────────────────────────────────────────────────────────
-- 8. DÉMOGRAPHIE — Écart Femmes / Hommes par tranche d'âge
-- ─────────────────────────────────────────────────────────────
SELECT
    Pays,
    Groupe_Age,
    MAX(CASE WHEN Genre = 'Femme' THEN Taux_Burnout_pct END) AS burnout_femme,
    MAX(CASE WHEN Genre = 'Homme' THEN Taux_Burnout_pct END) AS burnout_homme,
    ROUND(
        MAX(CASE WHEN Genre = 'Femme' THEN Taux_Burnout_pct END) -
        MAX(CASE WHEN Genre = 'Homme' THEN Taux_Burnout_pct END)
    , 1) AS ecart_pts
FROM age_gender
WHERE Annee = 2024
GROUP BY Pays, Groupe_Age
ORDER BY Pays, Groupe_Age;


-- ─────────────────────────────────────────────────────────────
-- 9. CTE COMPLEXE — Pays au-dessus de la moyenne mondiale
-- ─────────────────────────────────────────────────────────────
WITH global_avg AS (
    SELECT
        Year,
        AVG(Burnout_Rate_pct) AS world_avg_burnout
    FROM countries
    GROUP BY Year
),
country_vs_avg AS (
    SELECT
        c.Country,
        c.Year,
        c.Burnout_Rate_pct,
        g.world_avg_burnout,
        ROUND(c.Burnout_Rate_pct - g.world_avg_burnout, 2) AS delta_vs_world
    FROM countries c
    JOIN global_avg g ON c.Year = g.Year
)
SELECT *,
    CASE WHEN delta_vs_world > 0 THEN 'Au-dessus moyenne' ELSE 'En-dessous moyenne' END AS position
FROM country_vs_avg
WHERE Year = 2024
ORDER BY delta_vs_world DESC;


-- ─────────────────────────────────────────────────────────────
-- 10. JOINTURE — Secteurs France : coût total estimé (2024)
-- ─────────────────────────────────────────────────────────────
WITH france_2024 AS (
    SELECT Cout_par_habitant_EUR
    FROM costs
    WHERE Pays = 'France' AND Annee = 2024
)
SELECT
    s.Secteur,
    s.Nb_Employes_milliers,
    s.Cout_par_employe_EUR,
    ROUND(s.Nb_Employes_milliers * 1000 * s.Cout_par_employe_EUR / 1e9, 2) AS cout_secteur_mds_EUR,
    s.Taux_Burnout_pct,
    s.Taux_Turnover_pct
FROM sectors_france s
WHERE s.Annee = 2024
ORDER BY cout_secteur_mds_EUR DESC;


-- ─────────────────────────────────────────────────────────────
-- 11. PERCENTILE — Classement des secteurs par absentéisme
-- ─────────────────────────────────────────────────────────────
SELECT
    Secteur,
    Annee,
    Jours_Absence_moy,
    NTILE(4) OVER (PARTITION BY Annee ORDER BY Jours_Absence_moy) AS quartile_absence,
    ROUND(AVG(Jours_Absence_moy) OVER (PARTITION BY Annee), 1)    AS avg_national
FROM sectors_france
ORDER BY Annee, Jours_Absence_moy DESC;


-- ─────────────────────────────────────────────────────────────
-- 12. PIVOT — Burnout par pays et par année (format large)
-- ─────────────────────────────────────────────────────────────
SELECT
    Country,
    MAX(CASE WHEN Year = 2019 THEN Burnout_Rate_pct END) AS "2019",
    MAX(CASE WHEN Year = 2020 THEN Burnout_Rate_pct END) AS "2020",
    MAX(CASE WHEN Year = 2021 THEN Burnout_Rate_pct END) AS "2021",
    MAX(CASE WHEN Year = 2022 THEN Burnout_Rate_pct END) AS "2022",
    MAX(CASE WHEN Year = 2023 THEN Burnout_Rate_pct END) AS "2023",
    MAX(CASE WHEN Year = 2024 THEN Burnout_Rate_pct END) AS "2024",
    ROUND(
        MAX(CASE WHEN Year = 2024 THEN Burnout_Rate_pct END) -
        MAX(CASE WHEN Year = 2019 THEN Burnout_Rate_pct END)
    , 1) AS variation_2019_2024
FROM countries
GROUP BY Country
ORDER BY variation_2019_2024 DESC;


-- ─────────────────────────────────────────────────────────────
-- 13. SOUS-REQUÊTE — Secteurs France plus touchés que la moyenne
-- ─────────────────────────────────────────────────────────────
SELECT
    Secteur,
    Taux_Burnout_pct,
    Cout_par_employe_EUR,
    ROUND(Taux_Burnout_pct - (
        SELECT AVG(Taux_Burnout_pct) FROM sectors_france WHERE Annee = 2024
    ), 2) AS ecart_vs_moyenne
FROM sectors_france
WHERE Annee = 2024
  AND Taux_Burnout_pct > (
      SELECT AVG(Taux_Burnout_pct) FROM sectors_france WHERE Annee = 2024
  )
ORDER BY ecart_vs_moyenne DESC;


-- ─────────────────────────────────────────────────────────────
-- 14. ROI — Estimation du retour sur investissement prévention
--     Hypothèse : -10% burnout = -8% coûts absentéisme
-- ─────────────────────────────────────────────────────────────
SELECT
    Pays,
    Annee,
    Cout_Absenteisme_Mds_EUR                                        AS cout_actuel,
    ROUND(Cout_Absenteisme_Mds_EUR * 0.92, 2)                       AS cout_apres_prevention,
    ROUND(Cout_Absenteisme_Mds_EUR * 0.08, 2)                       AS economie_estimee_mds,
    ROUND(Cout_Absenteisme_Mds_EUR * 0.08 * 1000 / Nb_Arrêts_Travail_milliers, 0) AS economie_par_arret_EUR
FROM costs
WHERE Annee = 2024
ORDER BY economie_estimee_mds DESC;


-- ─────────────────────────────────────────────────────────────
-- 15. ANALYSE FINALE — Score global de bien-être par pays (2024)
--     Composite : WLB (40%) + Burnout inversé (30%) + Absentéisme inversé (30%)
-- ─────────────────────────────────────────────────────────────
WITH normalized AS (
    SELECT
        Country,
        Year,
        Work_Life_Balance_Index,
        Burnout_Rate_pct,
        Absenteeism_Days_per_employee,
        -- Normalisation 0-1 (min-max)
        (Work_Life_Balance_Index - MIN(Work_Life_Balance_Index) OVER ()) /
            NULLIF(MAX(Work_Life_Balance_Index) OVER () - MIN(Work_Life_Balance_Index) OVER (), 0) AS wlb_norm,
        1.0 - (Burnout_Rate_pct - MIN(Burnout_Rate_pct) OVER ()) /
            NULLIF(MAX(Burnout_Rate_pct) OVER () - MIN(Burnout_Rate_pct) OVER (), 0) AS burnout_inv_norm,
        1.0 - (Absenteeism_Days_per_employee - MIN(Absenteeism_Days_per_employee) OVER ()) /
            NULLIF(MAX(Absenteeism_Days_per_employee) OVER () - MIN(Absenteeism_Days_per_employee) OVER (), 0) AS abs_inv_norm
    FROM countries
    WHERE Year = 2024
)
SELECT
    Country,
    ROUND(wlb_norm * 0.4 + burnout_inv_norm * 0.3 + abs_inv_norm * 0.3, 3) AS wellbeing_score,
    RANK() OVER (ORDER BY wlb_norm * 0.4 + burnout_inv_norm * 0.3 + abs_inv_norm * 0.3 DESC) AS world_rank,
    Work_Life_Balance_Index,
    Burnout_Rate_pct,
    Absenteeism_Days_per_employee
FROM normalized
ORDER BY wellbeing_score DESC;
