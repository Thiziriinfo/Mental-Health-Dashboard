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
        "💡 ROI & Recommandations",
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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ROI & RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 ROI & Recommandations":
    st.markdown('<div class="page-title">ROI & Recommandations</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Simulateur d\'impact financier · Score bien-être · Actions prioritaires pour les DRH</div>', unsafe_allow_html=True)

    sectors_df = data["sectors"]
    costs_df   = data["costs"]
    countries_df = data["countries"]

    df_sec24  = sectors_df[sectors_df["Annee"] == 2024]
    df_cost24 = costs_df[costs_df["Annee"] == 2024]
    df_ctr24  = countries_df[countries_df["Year"] == 2024]

    # ── SIMULATEUR ROI ──────────────────────────────────────────────────────────
    st.markdown("### 🧮 Simulateur ROI — Investissement en prévention")
    st.markdown("*Basé sur les études Deloitte & OMS : chaque 1€ investi en prévention génère 4–5€ de retour*")

    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.markdown("**Paramètres entreprise**")
        nb_employes   = st.slider("Nombre d'employés", 50, 10000, 500, step=50)
        salaire_moy   = st.slider("Salaire moyen annuel (€)", 25000, 80000, 40000, step=1000)
        burnout_actuel = st.slider("Taux de burnout actuel (%)", 10, 60, 35)
        reduction_cible = st.slider("Réduction burnout visée (points)", 1, 20, 10)
        invest_par_emp = st.slider("Investissement prévention / employé (€/an)", 50, 2000, 500, step=50)

    with col_s2:
        # Calculs
        employes_burnout     = int(nb_employes * burnout_actuel / 100)
        employes_saves        = int(nb_employes * reduction_cible / 100)
        cout_absenteisme_emp  = 18 * (salaire_moy / 220)           # 18j absence × coût journalier
        cout_presenteisme_emp = salaire_moy * 0.07                  # 7% perte productivité
        cout_turnover_emp     = salaire_moy * 0.30                  # 30% du salaire pour remplacer

        gain_absenteisme  = round(employes_saves * cout_absenteisme_emp)
        gain_presenteisme = round(employes_saves * cout_presenteisme_emp)
        gain_turnover     = round(employes_saves * 0.15 * cout_turnover_emp)  # 15% turnover évité
        total_gain        = gain_absenteisme + gain_presenteisme + gain_turnover
        total_invest       = nb_employes * invest_par_emp
        roi_ratio          = round(total_gain / total_invest, 1) if total_invest > 0 else 0

        st.markdown("**Résultats simulés**")
        r1, r2, r3, r4 = st.columns(4)
        kpi(r1, "Employés à risque",        f"{employes_burnout:,}",      f"sur {nb_employes:,} employés", "red")
        kpi(r2, "Gain absentéisme",         f"{gain_absenteisme:,} €",    "Jours évités × coût journalier", "amber")
        kpi(r3, "Gain productivité",        f"{gain_presenteisme:,} €",   "Présentéisme réduit", "blue")
        kpi(r4, "ROI estimé",               f"× {roi_ratio}",             f"Pour {total_invest:,}€ investis → {total_gain:,}€ récupérés", "green")

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphique waterfall
        fig = go.Figure(go.Waterfall(
            name="ROI", orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Investissement","Gain absentéisme","Gain productivité","Gain turnover","ROI net"],
            y=[-total_invest, gain_absenteisme, gain_presenteisme, gain_turnover,
               total_gain - total_invest],
            connector=dict(line=dict(color="#e1dfdd")),
            decreasing=dict(marker_color="#D13438"),
            increasing=dict(marker_color="#107C10"),
            totals=dict(marker_color="#0078D4"),
            text=[f"-{total_invest:,}€", f"+{gain_absenteisme:,}€",
                  f"+{gain_presenteisme:,}€", f"+{gain_turnover:,}€",
                  f"{total_gain-total_invest:+,}€"],
            textposition="outside"
        ))
        fig.update_layout(title=f"Waterfall ROI — {nb_employes} employés | Réduction {reduction_cible} pts burnout",
                          yaxis_title="€")
        st.plotly_chart(style(fig, 300), use_container_width=True)

    st.markdown("---")

    # ── SCORE BIEN-ÊTRE COMPOSITE ───────────────────────────────────────────────
    st.markdown("### 🏆 Score Bien-être Mondial 2024")
    st.markdown("*Indice composite : WLB (40%) + Burnout inversé (30%) + Absentéisme inversé (30%)*")

    wlb_min, wlb_max = df_ctr24["Work_Life_Balance_Index"].min(), df_ctr24["Work_Life_Balance_Index"].max()
    brn_min, brn_max = df_ctr24["Burnout_Rate_pct"].min(), df_ctr24["Burnout_Rate_pct"].max()
    abs_min, abs_max = df_ctr24["Absenteeism_Days_per_employee"].min(), df_ctr24["Absenteeism_Days_per_employee"].max()

    df_score = df_ctr24.copy()
    df_score["wlb_norm"]  = (df_score["Work_Life_Balance_Index"] - wlb_min) / (wlb_max - wlb_min)
    df_score["brn_norm"]  = 1 - (df_score["Burnout_Rate_pct"] - brn_min) / (brn_max - brn_min)
    df_score["abs_norm"]  = 1 - (df_score["Absenteeism_Days_per_employee"] - abs_min) / (abs_max - abs_min)
    df_score["wellbeing_score"] = (df_score["wlb_norm"]*0.4 + df_score["brn_norm"]*0.3 + df_score["abs_norm"]*0.3).round(3)
    df_score = df_score.sort_values("wellbeing_score", ascending=False).reset_index(drop=True)
    df_score["Rang"] = df_score.index + 1
    df_score["Médaille"] = df_score["Rang"].map({1:"🥇", 2:"🥈", 3:"🥉"}).fillna("")

    col_w1, col_w2 = st.columns([1, 2])
    with col_w1:
        st.dataframe(
            df_score[["Médaille","Country","wellbeing_score","Burnout_Rate_pct","Work_Life_Balance_Index"]]
            .rename(columns={"wellbeing_score":"Score","Burnout_Rate_pct":"Burnout %","Work_Life_Balance_Index":"WLB","Country":"Pays"}),
            use_container_width=True, height=300
        )
    with col_w2:
        colors = ["#F2C811" if i==0 else "#C8C6C4" if i==1 else "#CD7F32" if i==2 else "#0078D4"
                  for i in range(len(df_score))]
        fig = go.Figure(go.Bar(
            x=df_score["Country"], y=df_score["wellbeing_score"],
            marker_color=colors,
            text=[f"{v:.3f}" for v in df_score["wellbeing_score"]],
            textposition="outside"
        ))
        fig.update_layout(title="Classement bien-être au travail — 2024", yaxis_title="Score (0-1)", showlegend=False)
        st.plotly_chart(style(fig, 300), use_container_width=True)

    st.markdown("---")

    # ── RECOMMANDATIONS ─────────────────────────────────────────────────────────
    st.markdown("### 🎯 Recommandations Actionnables par Secteur — France 2024")

    reco = {
        "Santé & Social":  {"niveau":"🔴 Critique", "color":"#FDE7E9", "border":"#D13438",
            "actions":["Mise en place de cellules de soutien psychologique d'urgence",
                       "Réduction des heures supplémentaires + renforts temporaires",
                       "Programme de rotation des équipes soignantes",
                       "Formations managers : détection précoce du burnout"]},
        "Éducation":       {"niveau":"🔴 Élevé", "color":"#FDE7E9", "border":"#D13438",
            "actions":["Réduction de la charge administrative des enseignants",
                       "Mise en place de temps de décompression collectif",
                       "Accès facilité aux psychologues scolaires pour les personnels",
                       "Valorisation et reconnaissance des équipes"]},
        "Juridique":       {"niveau":"🟡 Modéré", "color":"#FFF4CE", "border":"#E36C09",
            "actions":["Encadrement des astreintes et horaires atypiques",
                       "Formation à la gestion du stress et des conflits clients",
                       "Programme bien-être financé par le cabinet",
                       "Entretiens individuels trimestriels sur la charge de travail"]},
        "Finance":         {"niveau":"🟡 Modéré", "color":"#FFF4CE", "border":"#E36C09",
            "actions":["Télétravail partiel pour réduire la pression de présence",
                       "Sensibilisation aux risques du présentéisme",
                       "Coaching collectif en période de clôtures/reporting",
                       "Indicateurs bien-être intégrés aux objectifs managériaux"]},
        "BTP":             {"niveau":"🟢 Faible", "color":"#DFF6DD", "border":"#107C10",
            "actions":["Maintenir et renforcer les protocoles de sécurité",
                       "Suivi médical régulier (stress physique → mental)",
                       "Encourager la solidarité d'équipe déjà présente",
                       "Benchmark des bonnes pratiques vers d'autres secteurs"]},
    }

    cols = st.columns(3)
    for i, (secteur, info) in enumerate(reco.items()):
        with cols[i % 3]:
            actions_html = "".join([f"<li style='margin-bottom:4px;font-size:12px;color:#323130;'>{a}</li>" for a in info["actions"]])
            st.markdown(f"""
            <div style='background:{info["color"]};border-left:4px solid {info["border"]};
                        border-radius:6px;padding:14px 16px;margin-bottom:12px;'>
              <div style='font-weight:700;font-size:13px;color:#323130;margin-bottom:4px;'>{secteur}</div>
              <div style='font-size:11px;margin-bottom:8px;'>{info["niveau"]}</div>
              <ul style='padding-left:16px;margin:0;'>{actions_html}</ul>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 Projection Tendance Burnout — France 2025–2027")
    st.caption("Projection basée sur la tendance linéaire 2019–2024")

    df_fr = countries_df[countries_df["Country"] == "France"].sort_values("Year")
    import numpy as np
    z = np.polyfit(df_fr["Year"], df_fr["Burnout_Rate_pct"], 1)
    p = np.poly1d(z)
    years_proj = [2025, 2026, 2027]
    proj_vals  = [round(p(y), 1) for y in years_proj]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_fr["Year"], y=df_fr["Burnout_Rate_pct"],
        name="Historique", mode="lines+markers",
        line=dict(color="#0078D4", width=2), marker_size=6))
    fig.add_trace(go.Scatter(x=years_proj, y=proj_vals,
        name="Projection", mode="lines+markers",
        line=dict(color="#D13438", width=2, dash="dash"), marker_size=6))
    fig.add_shape(type="line", x0=2024, x1=2027,
                  y0=df_fr["Burnout_Rate_pct"].max(), y1=df_fr["Burnout_Rate_pct"].max(),
                  line=dict(color="#E36C09", dash="dot", width=1))
    fig.add_annotation(x=2025, y=df_fr["Burnout_Rate_pct"].max()+0.5,
                       text="⚠️ Seuil d'alerte", showarrow=False,
                       font=dict(color="#E36C09", size=10))
    fig.update_layout(title="Tendance & Projection burnout France (2019–2027)",
                      yaxis_title="Burnout (%)", xaxis_title="Année")
    st.plotly_chart(style(fig, 300), use_container_width=True)
