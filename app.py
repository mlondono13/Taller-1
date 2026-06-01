import streamlit as st
from utils.datos import cargar_datos, calcular_stats, calcular_kpis
from components import tab1_eficiencia, tab2_anomalia, tab3_explorador, tab4_antes_despues

st.set_page_config(
    page_title="Taller Visualización · Unidad 1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #F7F7F5; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F0EE;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1D9E75 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Datos 
df_original = cargar_datos()

# Sidebar
with st.sidebar:
    st.title("Filtros")
    st.divider()
    categorias = st.multiselect("Categoría",
        options=sorted(df_original["Categoria"].unique()),
        default=sorted(df_original["Categoria"].unique()))
    regiones = st.multiselect("Región",
        options=sorted(df_original["Region"].unique()),
        default=sorted(df_original["Region"].unique()))
    impactos = st.multiselect("Nivel de Impacto",
        options=["Alto", "Medio", "Bajo"], default=["Alto", "Medio", "Bajo"])
    st.divider()
    st.caption("Taller Visualización de Datos · Unidad 1")

df = df_original[
    df_original["Categoria"].isin(categorias) &
    df_original["Region"].isin(regiones) &
    df_original["Nivel_Impacto"].isin(impactos)
]

# Cálculos globales
stats, meta = calcular_stats(df)
kpis = calcular_kpis(df)

# Header 
st.markdown("""
<div style="
    border-top: 2px solid #1D9E75;
    border-bottom: 2px solid #1D9E75;
    padding: 1rem 0.25rem;
    margin-bottom: 1rem;
">
    <p style="color:#6B7280; font-size:0.78rem; margin:0 0 0.3rem 0;
              text-transform:uppercase; letter-spacing:1.5px; font-weight:600;">
        Pregunta central
    </p>
    <p style="color:#1A202C; font-size:1.25rem; font-weight:800; margin:0; line-height:1.5;">
        ¿Estamos invirtiendo el presupuesto donde se genera el mayor impacto social —
        y hay proyectos críticos que nadie está vigilando?
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(f"Mostrando {kpis['total']:,} de {len(df_original):,} proyectos según filtros activos")
st.divider()

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total proyectos",       f"{kpis['total']:,}")
k2.metric("Presupuesto total",     f"USD {kpis['pres_total']/1e6:.0f}M")
k3.metric("Proyectos retrasados",  f"{kpis['retrasados']:,}",
          f"{kpis['pct_retrasados']:.1f}% del total", delta_color="inverse")
k4.metric("Población beneficiada", f"{kpis['poblacion']/1e6:.1f}M personas")
k5.metric("Presupuesto en riesgo", f"USD {kpis['pres_retrasado']/1e6:.0f}M",
          f"{kpis['pct_riesgo']:.1f}% parado sin avance", delta_color="inverse")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Eficiencia por Categoría",
    "⚠️  Detección de Anomalía",
    "🔍  Explorador de Proyectos",
    "🎨  Fase 2: Antes vs. Después"
])

with tab1:
    tab1_eficiencia.render(stats, meta)

with tab2:
    tab2_anomalia.render(df, meta)

with tab3:
    tab3_explorador.render(df, meta)

with tab4:
    tab4_antes_despues.render(df, stats, meta)