import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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

VERDE   = "#1D9E75"
NARANJA = "#D85A30"
ROJO    = "#C81D25"
GRIS    = "#B4B2A9"

@st.cache_data
def cargar_datos():
    df = pd.read_csv('dataset_evaluacion_unidad1.csv')
    df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
    return df

df_original = cargar_datos()

# ── Sidebar ────────────────────────────────────────────────────────────────
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

# ── Header + KPIs ──────────────────────────────────────────────────────────
st.title("📊 Dashboard · Análisis de Proyectos Nacionales")
st.caption(f"Mostrando {len(df):,} de {len(df_original):,} proyectos según filtros activos")
st.divider()

retrasados = df[df['Estado'] == 'Retrasado']
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total proyectos",       f"{len(df):,}")
k2.metric("Presupuesto total",     f"USD {df['Presupuesto_USD'].sum()/1e6:.0f}M")
k3.metric("Proyectos retrasados",  f"{len(retrasados):,}",
          f"{len(retrasados)/len(df)*100:.1f}% del total", delta_color="inverse")
k4.metric("Población beneficiada", f"{df['Poblacion_Beneficiada'].sum()/1e6:.1f}M personas")
st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈  Eficiencia por Categoría",
    "⚠️  Detección de Anomalía",
    "🔍  Explorador de Proyectos"
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("¿Cuál categoría entrega más con menos?")
    st.caption("Eficiencia social del portafolio · ROI y Costo por beneficiario")
    st.divider()

    stats = (df.groupby("Categoria")[["Presupuesto_USD", "Poblacion_Beneficiada"]]
               .sum().reset_index())
    stats["ROI"]   = stats["Poblacion_Beneficiada"] / stats["Presupuesto_USD"] * 1000
    stats["Costo"] = stats["Presupuesto_USD"] / stats["Poblacion_Beneficiada"]

    col_a, col_b = st.columns(2)

    with col_a:
        roi = stats.sort_values("ROI", ascending=True)
        roi["color"] = [VERDE if v == roi["ROI"].max() else GRIS for v in roi["ROI"]]
        fig_roi = go.Figure(go.Bar(
            x=roi["ROI"], y=roi["Categoria"], orientation='h',
            marker_color=roi["color"],
            text=[f"{v:.2f}" for v in roi["ROI"]], textposition='outside',
            hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
        ))
        fig_roi.update_layout(
            title=dict(text="<b>Salud: más personas por dólar invertido</b>", font_size=14),
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=60, t=50, b=40), height=350, showlegend=False
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    with col_b:
        costo = stats.sort_values("Costo", ascending=True)
        costo["color"] = [NARANJA if v == costo["Costo"].max() else GRIS for v in costo["Costo"]]
        fig_costo = go.Figure(go.Bar(
            x=costo["Costo"], y=costo["Categoria"], orientation='h',
            marker_color=costo["color"],
            text=[f"${v:.1f}" for v in costo["Costo"]], textposition='outside',
            hovertemplate="<b>%{y}</b><br>Costo: $%{x:.1f} por persona<extra></extra>"
        ))
        fig_costo.update_layout(
            title=dict(text="<b>Tecnología: mayor costo por persona beneficiada</b>", font_size=14),
            xaxis=dict(title="USD por beneficiario", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=60, t=50, b=40), height=350, showlegend=False
        )
        st.plotly_chart(fig_costo, use_container_width=True)

    st.divider()
    st.subheader("Mapa de eficiencia por categoría")
    st.caption("Hover sobre cada burbuja · Tamaño = presupuesto total")

    stats["Presupuesto_M"] = stats["Presupuesto_USD"] / 1e6
    fig_scatter = px.scatter(
        stats, x="Costo", y="ROI", size="Presupuesto_M", color="Categoria",
        text="Categoria", color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data={"Costo": ":.1f", "ROI": ":.2f", "Presupuesto_M": ":.1f"}
    )
    fig_scatter.update_traces(textposition='top center', marker=dict(opacity=0.85))
    fig_scatter.update_layout(
        xaxis=dict(title="Costo por beneficiario (USD) → menor es mejor",
                   showgrid=True, gridcolor="#EBEBEB"),
        yaxis=dict(title="ROI social (personas/$1.000) → mayor es mejor",
                   showgrid=True, gridcolor="#EBEBEB"),
        plot_bgcolor="white", paper_bgcolor="white",
        height=420, showlegend=False, margin=dict(l=10, r=10, t=20, b=40)
    )
    fig_scatter.add_annotation(
        x=stats["Costo"].min(), y=stats["ROI"].max(),
        text="Zona ideal", showarrow=False,
        font=dict(color=VERDE, size=11), xanchor="left"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("¿Dónde están los proyectos que nadie vigila?")
    st.caption("Anomalía operativa: impacto Medio supera en retrasos al impacto Alto")
    st.divider()

    imp = (
        df.groupby('Nivel_Impacto')
        .apply(lambda x: pd.Series({
            'tasa':          round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n':             len(x),
            'presupuesto_M': round(x['Presupuesto_USD'].sum() / 1e6, 1),
            'retrasados':    (x['Estado'] == 'Retrasado').sum()
        }))
        .reset_index()
    )
    orden = ['Alto', 'Medio', 'Bajo']
    imp['orden'] = imp['Nivel_Impacto'].map({v: i for i, v in enumerate(orden)})
    imp = imp.sort_values('orden').reset_index(drop=True)

    if 'Alto' not in imp['Nivel_Impacto'].values or 'Medio' not in imp['Nivel_Impacto'].values:
        st.warning("⚠️ Esta visualización requiere tener seleccionados los niveles **Alto** y **Medio**. Actívalos en el filtro del sidebar.")
        st.stop()

    tasa_alto  = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
    tasa_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
    pres_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'presupuesto_M'].values[0]
    n_medio    = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'retrasados'].values[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Retrasos — Alto impacto",     f"{tasa_alto:.1f}%", "referencia esperada")
    m2.metric("Retrasos — Medio impacto",    f"{tasa_medio:.1f}%",
              f"+{tasa_medio - tasa_alto:.1f} pts sobre Alto", delta_color="inverse")
    m3.metric("Presupuesto Medio en riesgo", f"USD {pres_medio:.0f}M",
              f"{int(n_medio)} proyectos retrasados", delta_color="inverse")
    st.divider()

    colores_imp = [ROJO if n == 'Medio' else GRIS for n in imp['Nivel_Impacto']]
    fig_imp = go.Figure(go.Bar(
        x=imp['tasa'], y=imp['Nivel_Impacto'], orientation='h',
        marker_color=colores_imp,
        text=[f"{v:.1f}%  ({n:.0f} proyectos)" for v, n in zip(imp['tasa'], imp['n'])],
        textposition='outside',
        hovertemplate="<b>Impacto %{y}</b><br>Tasa retraso: %{x:.1f}%<extra></extra>"
    ))
    fig_imp.add_vline(
        x=tasa_alto, line_dash="dash", line_color=VERDE, line_width=2,
        annotation_text=f"Referencia Alto: {tasa_alto:.1f}%",
        annotation_position="top",
        annotation_font_color=VERDE, annotation_font_size=11
    )
    fig_imp.add_annotation(
        x=tasa_medio - 0.5, y='Medio',
        text=f"<b>+{tasa_medio - tasa_alto:.1f} pts<br>sobre Alto</b>",
        showarrow=True, arrowhead=2, arrowcolor=ROJO,
        ax=-80, ay=40, font=dict(color=ROJO, size=11),
        bgcolor="#FFF5F5", bordercolor=ROJO, borderwidth=1
    )
    fig_imp.update_layout(
        title=dict(
            text="<b>Los proyectos de impacto Medio presentan más retrasos que los de Alto</b><br>"
                 "<sup>Una anomalía operativa: reciben menos vigilancia pese al riesgo financiero</sup>",
            font_size=14),
        xaxis=dict(title="% de proyectos retrasados", tickformat=".0f", ticksuffix="%",
                   range=[0, 28], showgrid=True, gridcolor="#E2E8F0"),
        yaxis=dict(title="Nivel de Impacto", showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        height=380, showlegend=False, margin=dict(l=10, r=80, t=80, b=40)
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    st.info(
        f"**¿Qué hacer hoy?** Revisar los **{int(n_medio)} proyectos de impacto Medio retrasados** "
        f"que concentran **USD {pres_medio:.0f}M** sin supervisión activa. "
        "El problema no está donde todos miran — está exactamente donde nadie mira."
    )

# ══════════════════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Explorador de proyectos")
    st.caption("Filtra, ordena y descarga la data directamente")
    st.divider()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        estado_filtro = st.selectbox("Estado del proyecto",
            ["Todos", "En Ejecución", "Retrasado", "Completado"])
    with col_f2:
        orden_col = st.selectbox("Ordenar por",
            ["Presupuesto_USD", "Poblacion_Beneficiada", "Fecha_Inicio"])

    df_tabla = df.copy()
    if estado_filtro != "Todos":
        df_tabla = df_tabla[df_tabla["Estado"] == estado_filtro]
    df_tabla = df_tabla.sort_values(orden_col, ascending=False)

    cols_mostrar = ["ID_Proyecto", "Categoria", "Region",
                    "Nivel_Impacto", "Estado", "Presupuesto_USD", "Poblacion_Beneficiada"]

    st.dataframe(
        df_tabla[cols_mostrar].reset_index(drop=True),
        use_container_width=True, height=420,
        column_config={
            "Presupuesto_USD": st.column_config.NumberColumn("Presupuesto USD", format="$ %,.0f"),
            "Poblacion_Beneficiada": st.column_config.NumberColumn("Población Beneficiada", format="%,.0f"),
        }
    )
    st.caption(f"{len(df_tabla):,} proyectos mostrados")

    csv = df_tabla[cols_mostrar].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar tabla como CSV",
        data=csv, file_name="proyectos_filtrados.csv", mime="text/csv"
    )
