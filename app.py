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
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Eficiencia por Categoría",
    "⚠️  Detección de Anomalía",
    "🔍  Explorador de Proyectos",
    "🎨  Fase 2: Antes vs. Después"
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

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — FASE 2: ANTES VS DESPUÉS
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Fase 2: Composición del Mensaje")
    st.caption("Transformación de gráficas exploratorias en argumentos visuales aclaratorios")
    st.divider()

    # ── COMPARATIVA 1 ──────────────────────────────────────────────────────
    st.markdown("### Comparativa 1 — Eficiencia por Categoría")
    st.markdown(
        "**Pregunta respondida:** ¿Qué categoría genera más impacto social por dólar invertido?"
    )

    antes1, despues1 = st.columns(2)

    with antes1:
        st.markdown("#### ANTES — Gráfica exploratoria")
        stats2 = df.groupby("Categoria")[["Presupuesto_USD","Poblacion_Beneficiada"]].sum().reset_index()
        stats2["ROI"] = stats2["Poblacion_Beneficiada"] / stats2["Presupuesto_USD"] * 1000
        roi_exp = stats2.sort_values("ROI", ascending=True)

        fig_a1 = go.Figure(go.Bar(
            x=roi_exp["ROI"], y=roi_exp["Categoria"], orientation='h',
            marker_color='steelblue',
            text=[f"{v:.2f}" for v in roi_exp["ROI"]], textposition='outside',
        ))
        fig_a1.update_layout(
            title="ROI Social por Categoría",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB"),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_a1, use_container_width=True)

        st.info("**Problema:** Todas las barras en el mismo azul. El ojo no sabe dónde ir. No hay jerarquía visual ni mensaje claro.")

    with despues1:
        st.markdown("#### DESPUÉS — Gráfica aclaratoria")
        roi_ac = stats2.sort_values("ROI", ascending=True)
        roi_ac["color"] = ["#1D9E75" if v == roi_ac["ROI"].max() else "#B4B2A9" for v in roi_ac["ROI"]]

        fig_d1 = go.Figure(go.Bar(
            x=roi_ac["ROI"], y=roi_ac["Categoria"], orientation='h',
            marker_color=roi_ac["color"],
            text=[f"{v:.2f}" for v in roi_ac["ROI"]], textposition='outside',
            hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
        ))
        fig_d1.update_layout(
            title="<b>Salud: más personas por dólar invertido</b>",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_d1, use_container_width=True)
        st.success("**Solución:** Color selectivo — solo Salud en verde. El eje X se mantiene para referencia. Título que comunica el hallazgo, no solo describe la variable.")

    # Justificación
    with st.expander("Ver justificación de decisiones visuales — Comparativa 1"):
        st.markdown("""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme en todas las barras | Verde solo en Salud, gris en el resto | Color como énfasis, no decoración. Principio de pre-atención visual |
| **Ordenación** | Sin orden aparente | De menor a mayor ROI | El ojo sigue la dirección de las barras hacia la categoría dominante |
| **Título** | Descriptivo ("ROI Social por Categoría") | Informativo ("Salud: más personas por dólar") | El título comunica el hallazgo, no la variable |
| **Interactividad** | Estático (matplotlib) | Hover con tooltip (Plotly) | Permite explorar valores exactos sin saturar la gráfica |
        """)

    st.divider()

    # ── COMPARATIVA 2 ──────────────────────────────────────────────────────
    st.markdown("### Comparativa 2 — Detección de Anomalía")
    st.markdown(
        "**Pregunta respondida:** ¿En qué segmento del portafolio se concentran los retrasos de forma inesperada?"
    )

    antes2, despues2 = st.columns(2)

    imp2 = (
        df.groupby('Nivel_Impacto')
        .apply(lambda x: pd.Series({
            'tasa':      round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n':         len(x),
            'retrasados': int((x['Estado'] == 'Retrasado').sum())
        }))
        .reset_index()
    )
    orden2 = ['Alto', 'Medio', 'Bajo']
    imp2['orden'] = imp2['Nivel_Impacto'].map({v: i for i, v in enumerate(orden2)})
    imp2 = imp2.sort_values('orden').reset_index(drop=True)

    with antes2:
        st.markdown("#### ANTES — Sin contraste")
        fig_a2 = go.Figure(go.Bar(
            x=imp2['tasa'], y=imp2['Nivel_Impacto'], orientation='h',
            marker_color='steelblue', width=0.5,
            text=[f"{v:.1f}%" for v in imp2['tasa']], textposition='outside',
        ))
        fig_a2.update_layout(
            title="Tasa de retraso por nivel de impacto",
            xaxis=dict(title="% retrasados", range=[0, 25], showgrid=True, gridcolor="#EBEBEB"),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            height=300, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_a2, use_container_width=True)
        st.info("**Problema:** Todas las barras iguales. La anomalía existe pero es invisible. El espectador no sabe si debe preocuparse.")

    with despues2:
        st.markdown("#### DESPUÉS — Figura / Fondo")
        colores2 = ["#C81D25" if n == 'Medio' else "#B4B2A9" for n in imp2['Nivel_Impacto']]
        tasa_alto2 = imp2.loc[imp2['Nivel_Impacto'] == 'Alto', 'tasa'].values[0]
        tasa_medio2 = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]

        fig_d2 = go.Figure(go.Bar(
            x=imp2['tasa'], y=imp2['Nivel_Impacto'], orientation='h',
            marker_color=colores2, width=0.5,
            text=[f"{v:.1f}%  ({n} proyectos)" for v, n in zip(imp2['tasa'], imp2['n'])],
            textposition='outside',
            hovertemplate="<b>Impacto %{y}</b><br>%{x:.1f}% retrasados<extra></extra>"
        ))
        fig_d2.add_vline(
            x=tasa_alto2, line_dash="dash", line_color="#276749", line_width=2,
            annotation_text=f"Referencia Alto: {tasa_alto2:.1f}%",
            annotation_font_color="#276749", annotation_font_size=10
        )
        fig_d2.add_annotation(
            x=tasa_medio2 - 0.5, y='Medio',
            text=f"<b>+{tasa_medio2 - tasa_alto2:.1f} pts sobre Alto</b>",
            showarrow=True, arrowhead=2, arrowcolor="#C81D25",
            ax=-90, ay=35, font=dict(color="#C81D25", size=10),
            bgcolor="#FFF5F5", bordercolor="#C81D25", borderwidth=1
        )
        fig_d2.update_layout(
            title="<b>Impacto Medio: la anomalía que nadie vigila</b>",
            xaxis=dict(title="% retrasados", range=[0, 28], showgrid=True, gridcolor="#E2E8F0"),
            yaxis=dict(showgrid=False),
            plot_bgcolor="white", paper_bgcolor="white",
            height=300, showlegend=False, margin=dict(l=10, r=80, t=40, b=30)
        )
        st.plotly_chart(fig_d2, use_container_width=True)
        st.success("**Solución:** Rojo solo en Medio. Línea de referencia verde marca lo esperado. Anotación con la brecha exacta. El insight está escrito en la gráfica.")

    with st.expander("Ver justificación de decisiones visuales — Comparativa 2"):
        st.markdown("""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme | Rojo en Medio, gris en el resto | Contraste Figura/Fondo — la anomalía es la figura, el contexto es el fondo |
| **Línea de referencia** | No existe | Línea verde punteada en tasa del Alto | Permite medir la brecha visualmente sin calcular |
| **Anotación** | No existe | "+6 pts sobre Alto" con flecha | El insight está escrito en la gráfica — no hay que interpretarlo |
| **Ordenación** | Alfabética | Alto → Medio → Bajo (narrativa) | El ojo llega a Medio después de ver que Alto es el mejor, construyendo la sorpresa |
| **Título** | Neutro | "La anomalía que nadie vigila" | Comunica urgencia y acción, no solo descripción |
        """)

    st.divider()
    st.markdown("### Principios aplicados")
    c1, c2, c3 = st.columns(3)
    c1.metric("Data-to-Ink Ratio", "Maximizado", "Ejes y bordes eliminados")
    c2.metric("Color selectivo", "1 categoría destacada", "Por gráfica")
    c3.metric("Anotaciones", "Insight en la gráfica", "No en el texto externo")@st.cache_data
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
