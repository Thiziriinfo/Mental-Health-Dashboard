import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Santé Mentale au Travail",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

PALETTE = ["#0078D4","#D13438","#107C10","#E36C09","#5C2D91",
           "#008272","#E3008C","#F2C811","#004578","#A4262C"]

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background:#f3f2f1; }
  [data-testid="stSidebar"] { background:#201f1e; }
  [data-testid="stSidebar"] * { color:#c8c6c4 !important; }
  .metric-card { background:#fff; border-radius:6px; padding:16px 20px;
    border-left:5px solid #0078D4; box-shadow:0 1px 4px rgba(0,0,0,.08); margin-bottom:4px; }
  .metric-card.red    { border-left-color:#D13438; }
  .metric-card.green  { border-left-color:#107C10; }
  .metric-card.amber  { border-left-color:#E36C09; }
  .metric-label { font-size:11px; color:#605e5c; text-transform:uppercase;
    letter-spacing:.06em; font-weight:600; margin-bottom:4px; }
  .metric-value { font-size:28px; font-weight:300; color:#323130; line-height:1; }
  .metric-delta { font-size:12px; margin-top:4px; }
  .delta-up { color:#D13438; } .delta-down { color:#107C10; }
  .page-title { font-size:22px; font-weight:600; color:#323130; margin-bottom:4px; }
  .page-sub { font-size:13px; color:#605e5c; margin-bottom:20px; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    return {
        "countries":   pd.read_csv(os.path.join(base, "mental_health_countries.csv")),
        "costs":       pd.read_csv(os.path.join(base, "mental_health_costs.csv")),
        "sectors":     pd.read_csv(os.path.join(base, "mental_health_sectors_france.csv")),
        "age_gender":  pd.read_csv(os.path.join(base, "mental_health_age_gender.csv")),
    }

data = load()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Santé Mentale au Travail")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🌍 Vue Globale",
        "🇫🇷 Analyse France",
        "💶 Impact Économique",
        "👥 Profil Démographique",
        "🔍 Explorateur SQL",
    ])
    st.markdown("---")
    st.markdown("**Filtres**")
    all_years = sorted(data["countries"]["Year"].unique().tolist())
    years = st.multiselect("Années", all_years, default=all_years)
    if not years: years = all_years

    all_countries = sorted(data["countries"]["Country"].unique().tolist())
    countries_sel = st.multiselect("Pays", all_countries, default=all_countries)
    if not countries_sel: countries_sel = all_countries

    st.markdown("---")
    st.caption("Sources : OCDE · OMS · DREES · INRS")
    st.caption("© Thiziri Abchiche · 2026")

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def kpi(col, label, value, delta=None, color=""):
    dhtml = ""
    if delta:
        cls = "delta-up" if "▲" in delta else "delta-down"
        dhtml = f'<div class="metric-delta {cls}">{delta}</div>'
    col.markdown(f"""<div class="metric-card {color}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>{dhtml}
    </div>""", unsafe_allow_html=True)

def style(fig, h=320):
    fig.update_layout(height=h, margin=dict(l=8,r=8,t=36,b=8),
        paper_bgcolor="#fff", plot_bgcolor="#fff",
        font=dict(family="Segoe UI",size=11,color="#323130"),
        legend=dict(orientation="h",yanchor="bottom",y=-0.35,font_size=10),
        xaxis=dict(showgrid=True,gridcolor="#f3f2f1"),
        yaxis=dict(showgrid=True,gridcolor="#f3f2f1"))
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🌍 Vue Globale":
    st.markdown('<div class="page-title">Vue Globale — Burnout & Bien-être</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Analyse comparative internationale · Sources OCDE/OMS 2019–2024</div>', unsafe_allow_html=True)

    df  = data["countries"]
    df  = df[df["Year"].isin(years) & df["Country"].isin(countries_sel)]
    df24 = df[df["Year"] == max(years)]

    c1,c2,c3,c4 = st.columns(4)
    best = df24.loc[df24["Burnout_Rate_pct"].idxmin()]
    kpi(c1, "Taux burnout moyen 2024",  f"{df24['Burnout_Rate_pct'].mean():.1f}%", "▲ +6.4 pts vs 2019", "red")
    kpi(c2, "Jours absence / employé",  f"{df24['Absenteeism_Days_per_employee'].mean():.1f} j", "▲ +2.1 j vs 2019", "amber")
    kpi(c3, "Coût présentéisme moyen",  f"${df24['Presenteeism_Cost_USD'].mean():,.0f}", "▲ +$1 020 vs 2019")
    kpi(c4, "Meilleur WLB — pays modèle", best["Country"], f"Burnout : {best['Burnout_Rate_pct']}%", "green")

    col1, col2 = st.columns(2)
    with col1:
        pivot = df.pivot_table(index="Year", columns="Country", values="Burnout_Rate_pct")
        fig = go.Figure()
        for i, c in enumerate(pivot.columns):
            fig.add_trace(go.Scatter(x=pivot.index, y=pivot[c], name=c, mode="lines+markers",
                line=dict(width=2, color=PALETTE[i % len(PALETTE)]), marker_size=5))
        fig.update_layout(title="Évolution du taux de burnout par pays")
        st.plotly_chart(style(fig), use_container_width=True)

    with col2:
        s = df24.sort_values("Burnout_Rate_pct")
        fig = px.bar(s, x="Burnout_Rate_pct", y="Country", orientation="h",
                     title="Burnout 2024 — Classement international",
                     color="Burnout_Rate_pct",
                     color_continuous_scale=["#107C10","#F2C811","#D13438"])
        fig.update_coloraxes(showscale=False)
        fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        st.plotly_chart(style(fig), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = px.scatter(df24, x="Work_Life_Balance_Index", y="Burnout_Rate_pct",
                         size="Presenteeism_Cost_USD", color="Region", text="Country",
                         title="Work-Life Balance vs Burnout (2024)",
                         color_discrete_sequence=PALETTE,
                         labels={"Work_Life_Balance_Index":"WLB Index","Burnout_Rate_pct":"Burnout (%)"})
        fig.update_traces(textposition="top center", textfont_size=9)
        st.plotly_chart(style(fig), use_container_width=True)

    with col4:
        dfr = df[df["Country"] == "France"]
        fig = go.Figure()
        for m, color, name in [("Burnout_Rate_pct","#D13438","Burnout"),
                                ("Anxiety_Rate_pct","#E36C09","Anxiété"),
                                ("Depression_Rate_pct","#0078D4","Dépression")]:
            fig.add_trace(go.Bar(x=dfr["Year"], y=dfr[m], name=name, marker_color=color))
        fig.update_layout(barmode="group", title="France — Burnout · Anxiété · Dépression")
        st.plotly_chart(style(fig), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ANALYSE FRANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🇫🇷 Analyse France":
    st.markdown('<div class="page-title">Analyse par Secteur — France</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Burnout, coûts et absentéisme par secteur · 2019–2024</div>', unsafe_allow_html=True)

    df  = data["sectors"]
    df  = df[df["Annee"].isin(years)]
    df24 = df[df["Annee"] == max(years)]

    worst = df24.loc[df24["Taux_Burnout_pct"].idxmax()]
    best  = df24.loc[df24["Taux_Burnout_pct"].idxmin()]
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, "Secteur le + touché 2024",    worst["Secteur"],  f"{worst['Taux_Burnout_pct']}% burnout", "red")
    kpi(c2, "Coût max / employé",          f"{int(df24['Cout_par_employe_EUR'].max()):,} €", "Juridique", "amber")
    kpi(c3, "Turnover moyen France",       f"{df24['Taux_Turnover_pct'].mean():.1f}%", "▲ corrélé au burnout")
    kpi(c4, "Secteur le moins touché",     best["Secteur"],   f"{best['Taux_Burnout_pct']}% burnout", "green")

    col1, col2 = st.columns(2)
    with col1:
        s = df24.sort_values("Taux_Burnout_pct")
        colors = ["#D13438" if v >= 40 else "#E36C09" if v >= 35 else "#107C10"
                  for v in s["Taux_Burnout_pct"]]
        fig = go.Figure(go.Bar(y=s["Secteur"], x=s["Taux_Burnout_pct"], orientation="h",
            marker_color=colors, text=[f"{v:.1f}%" for v in s["Taux_Burnout_pct"]],
            textposition="outside"))
        fig.update_layout(title="Burnout par secteur — France 2024", xaxis_title="%", showlegend=False)
        st.plotly_chart(style(fig), use_container_width=True)

    with col2:
        fig = px.bar(df24.sort_values("Cout_par_employe_EUR", ascending=False),
                     x="Secteur", y="Cout_par_employe_EUR",
                     title="Coût annuel par employé (€)",
                     color="Cout_par_employe_EUR",
                     color_continuous_scale=["#deecf9","#0078D4","#004578"])
        fig.update_coloraxes(showscale=False)
        fig.update_traces(texttemplate="%{y:,}€", textposition="outside")
        st.plotly_chart(style(fig), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        top4 = ["Santé & Social","IT","Finance","Éducation"]
        fig = px.line(df[df["Secteur"].isin(top4)], x="Annee", y="Taux_Burnout_pct",
                      color="Secteur", markers=True,
                      title="Évolution burnout — Top secteurs (2019–2024)",
                      color_discrete_sequence=PALETTE,
                      labels={"Annee":"Année","Taux_Burnout_pct":"Burnout (%)"})
        fig.update_traces(line_width=2, marker_size=5)
        st.plotly_chart(style(fig), use_container_width=True)

    with col4:
        df24r = df24.copy()
        df24r["risk_score"] = (df24r["Taux_Burnout_pct"]*0.4 +
                               df24r["Taux_Anxiete_pct"]*0.3 +
                               df24r["Taux_Turnover_pct"]*0.3)
        df24r["Niveau"] = pd.cut(df24r["risk_score"], bins=[0,32,38,100],
                                 labels=["🟢 Faible","🟡 Modéré","🔴 Critique"])
        st.markdown("**Tableau synthétique — France 2024**")
        st.dataframe(
            df24r[["Secteur","Taux_Burnout_pct","Cout_par_employe_EUR",
                   "Jours_Absence_moy","Taux_Turnover_pct","Niveau"]]
            .rename(columns={"Taux_Burnout_pct":"Burnout %","Cout_par_employe_EUR":"Coût/emp. €",
                             "Jours_Absence_moy":"Absence j","Taux_Turnover_pct":"Turnover %"})
            .sort_values("Burnout %", ascending=False).reset_index(drop=True),
            use_container_width=True, height=270)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — IMPACT ÉCONOMIQUE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💶 Impact Économique":
    st.markdown('<div class="page-title">Impact Économique Global</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Coûts directs et indirects liés à la santé mentale au travail · Mds €</div>', unsafe_allow_html=True)

    df   = data["costs"]
    df   = df[df["Annee"].isin(years)]
    df24 = df[df["Annee"] == max(years)]
    dfr  = df[df["Pays"] == "France"]
    fr24 = df24[df24["Pays"] == "France"].iloc[0]
    usa24 = df24[df24["Pays"] == "USA"]["Cout_Total_Mds_EUR"].values[0]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, "Coût total France 2024",    f"{fr24['Cout_Total_Mds_EUR']:.1f} Mds €",   "▲ +27.5% vs 2019", "red")
    kpi(c2, "Perte productivité France", f"{fr24['Perte_Productivite_Mds_EUR']:.1f} Mds €", "57% du coût total", "amber")
    kpi(c3, "Coût / habitant France",    f"{int(fr24['Cout_par_habitant_EUR']):,} €", "▲ +418 € vs 2019")
    kpi(c4, "Coût total USA 2024",       f"{usa24:.1f} Mds €",                         "Record mondial", "red")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df24.sort_values("Cout_Total_Mds_EUR", ascending=False),
                     x="Pays", y="Cout_Total_Mds_EUR",
                     title="Coût total par pays — 2024 (Mds €)",
                     color="Cout_Total_Mds_EUR",
                     color_continuous_scale=["#deecf9","#0078D4","#D13438"])
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig), use_container_width=True)

    with col2:
        fig = go.Figure(go.Pie(
            labels=["Productivité perdue","Coût santé","Absentéisme"],
            values=[fr24["Perte_Productivite_Mds_EUR"],
                    fr24["Cout_Sante_Mds_EUR"],
                    fr24["Cout_Absenteisme_Mds_EUR"]],
            hole=0.55, marker_colors=["#D13438","#0078D4","#E36C09"],
            textinfo="label+percent"))
        fig.update_layout(title="Décomposition coûts — France 2024")
        st.plotly_chart(style(fig), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dfr["Annee"], y=dfr["Cout_Total_Mds_EUR"],
            name="Coût total", fill="tozeroy", line=dict(color="#0078D4",width=2),
            fillcolor="rgba(0,120,212,0.1)"))
        fig.add_trace(go.Scatter(x=dfr["Annee"], y=dfr["Perte_Productivite_Mds_EUR"],
            name="Productivité perdue", line=dict(color="#D13438",width=2,dash="dash")))
        fig.update_layout(title="Évolution des coûts — France (Mds €)")
        st.plotly_chart(style(fig), use_container_width=True)

    with col4:
        fig = px.bar(df24.sort_values("Cout_par_habitant_EUR"),
                     x="Cout_par_habitant_EUR", y="Pays", orientation="h",
                     title="Coût par habitant 2024 (€)",
                     color="Cout_par_habitant_EUR",
                     color_continuous_scale=["#dff6dd","#107C10","#004578"])
        fig.update_coloraxes(showscale=False)
        fig.update_traces(texttemplate="%{x:,}€", textposition="outside")
        st.plotly_chart(style(fig), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PROFIL DÉMOGRAPHIQUE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Profil Démographique":
    st.markdown('<div class="page-title">Profil Démographique</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Burnout, anxiété et demande d\'aide par âge et genre · 2024</div>', unsafe_allow_html=True)

    df   = data["age_gender"]
    df24 = df[df["Annee"] == 2024]
    dfr  = df24[df24["Pays"] == "France"]
    fem  = dfr[dfr["Genre"] == "Femme"]
    hom  = dfr[dfr["Genre"] == "Homme"]

    wf  = fem.loc[fem["Taux_Burnout_pct"].idxmax()]
    wh  = hom.loc[hom["Taux_Burnout_pct"].idxmax()]
    gap = round(fem["Taux_Burnout_pct"].mean() - hom["Taux_Burnout_pct"].mean(), 1)
    ma  = fem.loc[fem["Taux_Demande_Aide_pct"].idxmax()]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, "Groupe + touché — Femmes", wf["Groupe_Age"],  f"{wf['Taux_Burnout_pct']}% burnout", "red")
    kpi(c2, "Groupe + touché — Hommes", wh["Groupe_Age"],  f"{wh['Taux_Burnout_pct']}% burnout", "amber")
    kpi(c3, "Écart Femmes / Hommes",    f"+{gap} pts",      "Femmes systématiquement + touchées")
    kpi(c4, "Demande d'aide max (F)",   ma["Groupe_Age"],  f"{ma['Taux_Demande_Aide_pct']}%", "green")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fem["Groupe_Age"], y=fem["Taux_Burnout_pct"],
                             name="Femmes", marker_color="#D13438"))
        fig.add_trace(go.Bar(x=hom["Groupe_Age"], y=hom["Taux_Burnout_pct"],
                             name="Hommes", marker_color="#0078D4"))
        fig.update_layout(barmode="group",
                          title="Burnout — Femmes vs Hommes par âge (France 2024)",
                          yaxis_title="%")
        st.plotly_chart(style(fig), use_container_width=True)

    with col2:
        fig = go.Figure()
        for ser, color, dash in [
            (fem, "#D13438", "solid"),  (hom, "#0078D4", "dot"),
        ]:
            for m, name in [("Taux_Anxiete_pct","Anxiété"), ("Taux_Depression_pct","Dépression")]:
                lbl = f"{name} {'F' if dash=='solid' else 'H'}"
                fig.add_trace(go.Scatter(x=ser["Groupe_Age"], y=ser[m], name=lbl,
                    mode="lines+markers",
                    line=dict(color=color if m=="Taux_Anxiete_pct" else "#5C2D91" if dash=="solid" else "#008272",
                              width=2, dash=dash), marker_size=5))
        fig.update_layout(title="Anxiété & Dépression par âge — France 2024", yaxis_title="%")
        st.plotly_chart(style(fig), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fem["Groupe_Age"], y=fem["Taux_Demande_Aide_pct"],
                             name="Femmes", marker_color="#D13438"))
        fig.add_trace(go.Bar(x=hom["Groupe_Age"], y=hom["Taux_Demande_Aide_pct"],
                             name="Hommes", marker_color="#0078D4"))
        fig.update_layout(barmode="group",
                          title="Demande d'aide professionnelle (%) — France 2024",
                          yaxis_title="%")
        st.plotly_chart(style(fig), use_container_width=True)

    with col4:
        ages = fem["Groupe_Age"].tolist()
        fig = go.Figure()
        for pays_n, color in [("France","#0078D4"),("UK","#5C2D91"),("Japan","#D13438")]:
            sub = df24[(df24["Pays"] == pays_n) & (df24["Genre"] == "Femme")]
            if not sub.empty:
                vals = sub.set_index("Groupe_Age").reindex(ages)["Taux_Burnout_pct"].tolist()
                fig.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=ages+[ages[0]],
                    name=pays_n, fill="toself", line_color=color, opacity=0.7))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,60])),
                          title="Burnout Femmes — Comparaison internationale")
        st.plotly_chart(style(fig, 340), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — EXPLORATEUR SQL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Explorateur SQL":
    st.markdown('<div class="page-title">Explorateur SQL</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Requêtes analytiques en direct · CTEs · Window Functions · Jointures</div>', unsafe_allow_html=True)

    @st.cache_resource
    def get_conn():
        conn = sqlite3.connect(":memory:")
        data["countries"].to_sql("countries", conn, if_exists="replace", index=False)
        data["costs"].to_sql("costs", conn, if_exists="replace", index=False)
        data["sectors"].to_sql("sectors_france", conn, if_exists="replace", index=False)
        data["age_gender"].to_sql("age_gender", conn, if_exists="replace", index=False)
        return conn

    mem_conn = get_conn()

    queries = {
        "1 — Burnout moyen par pays (AVG + GROUP BY)": """SELECT Country, Region,
       ROUND(AVG(Burnout_Rate_pct), 2) AS avg_burnout_pct,
       ROUND(AVG(Anxiety_Rate_pct), 2) AS avg_anxiety_pct,
       ROUND(AVG(Absenteeism_Days_per_employee), 1) AS avg_absence_days
FROM countries
GROUP BY Country, Region
ORDER BY avg_burnout_pct DESC""",

        "2 — Évolution YoY France (LAG Window Function)": """SELECT Year, Burnout_Rate_pct,
       LAG(Burnout_Rate_pct) OVER (ORDER BY Year) AS prev_year,
       ROUND(Burnout_Rate_pct - LAG(Burnout_Rate_pct) OVER (ORDER BY Year), 2) AS yoy_change_pts
FROM countries
WHERE Country = 'France'
ORDER BY Year""",

        "3 — Top 3 pays les + touchés / année (RANK)": """WITH ranked AS (
    SELECT Year, Country, Burnout_Rate_pct,
           RANK() OVER (PARTITION BY Year ORDER BY Burnout_Rate_pct DESC) AS rnk
    FROM countries
)
SELECT Year, Country, Burnout_Rate_pct, rnk
FROM ranked WHERE rnk <= 3
ORDER BY Year, rnk""",

        "4 — Score risque secteurs France 2024 (DENSE_RANK)": """SELECT Secteur, Taux_Burnout_pct, Taux_Anxiete_pct, Taux_Turnover_pct,
       ROUND(Taux_Burnout_pct*0.4 + Taux_Anxiete_pct*0.3 + Taux_Turnover_pct*0.3, 2) AS risk_score,
       DENSE_RANK() OVER (ORDER BY Taux_Burnout_pct*0.4 + Taux_Anxiete_pct*0.3 + Taux_Turnover_pct*0.3 DESC) AS risk_rank
FROM sectors_france WHERE Annee = 2024
ORDER BY risk_score DESC""",

        "5 — Pays au-dessus de la moyenne mondiale (CTE)": """WITH global_avg AS (
    SELECT Year, AVG(Burnout_Rate_pct) AS world_avg FROM countries GROUP BY Year
)
SELECT c.Country, c.Year, c.Burnout_Rate_pct,
       ROUND(g.world_avg, 2) AS world_avg,
       ROUND(c.Burnout_Rate_pct - g.world_avg, 2) AS delta
FROM countries c JOIN global_avg g ON c.Year = g.Year
WHERE c.Year = 2024
ORDER BY delta DESC""",

        "6 — Décomposition coûts % par pays (2024)": """SELECT Pays, Cout_Total_Mds_EUR,
       ROUND(Perte_Productivite_Mds_EUR*100.0/Cout_Total_Mds_EUR,1) AS pct_productivite,
       ROUND(Cout_Sante_Mds_EUR*100.0/Cout_Total_Mds_EUR,1)         AS pct_sante,
       ROUND(Cout_Absenteisme_Mds_EUR*100.0/Cout_Total_Mds_EUR,1)   AS pct_absenteisme
FROM costs WHERE Annee = 2024
ORDER BY Cout_Total_Mds_EUR DESC""",

        "7 — Pivot burnout par pays 2019→2024": """SELECT Country,
       MAX(CASE WHEN Year=2019 THEN Burnout_Rate_pct END) AS "2019",
       MAX(CASE WHEN Year=2021 THEN Burnout_Rate_pct END) AS "2021",
       MAX(CASE WHEN Year=2024 THEN Burnout_Rate_pct END) AS "2024",
       ROUND(MAX(CASE WHEN Year=2024 THEN Burnout_Rate_pct END) -
             MAX(CASE WHEN Year=2019 THEN Burnout_Rate_pct END), 1) AS variation_5y
FROM countries GROUP BY Country ORDER BY variation_5y DESC""",

        "8 — Écart Femmes / Hommes par âge (PIVOT)": """SELECT Pays, Groupe_Age,
       MAX(CASE WHEN Genre='Femme' THEN Taux_Burnout_pct END) AS burnout_femme,
       MAX(CASE WHEN Genre='Homme' THEN Taux_Burnout_pct END) AS burnout_homme,
       ROUND(MAX(CASE WHEN Genre='Femme' THEN Taux_Burnout_pct END) -
             MAX(CASE WHEN Genre='Homme' THEN Taux_Burnout_pct END), 1) AS ecart_pts
FROM age_gender WHERE Annee = 2024
GROUP BY Pays, Groupe_Age ORDER BY Pays, Groupe_Age""",
    }

    selected = st.selectbox("Choisir une requête", list(queries.keys()))
    q_input  = st.text_area("Éditeur SQL", value=queries[selected].strip(), height=160)

    if st.button("▶ Exécuter", type="primary"):
        try:
            result = pd.read_sql(q_input, mem_conn)
            st.success(f"✅ {len(result)} lignes retournées")
            st.dataframe(result, use_container_width=True)
            nums = result.select_dtypes("number").columns.tolist()
            if len(result.columns) >= 2 and nums:
                fig = px.bar(result.head(15), x=result.columns[0], y=nums[0],
                             color_discrete_sequence=["#0078D4"])
                st.plotly_chart(style(fig, 260), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")
