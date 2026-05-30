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
 
# ── Cálculos globales ──────────────────────────────────────────────────────
retrasados     = df[df['Estado'] == 'Retrasado']
pres_total     = df['Presupuesto_USD'].sum()
pres_retrasado = retrasados['Presupuesto_USD'].sum()
pct_riesgo     = pres_retrasado / pres_total * 100 if pres_total > 0 else 0
 
stats = (df.groupby("Categoria")[["Presupuesto_USD", "Poblacion_Beneficiada"]]
           .sum().reset_index())
stats["ROI"]   = stats["Poblacion_Beneficiada"] / stats["Presupuesto_USD"] * 1000
stats["Costo"] = stats["Presupuesto_USD"] / stats["Poblacion_Beneficiada"]
 
cat_mejor_roi   = stats.loc[stats["ROI"].idxmax(),   "Categoria"]
cat_mayor_costo = stats.loc[stats["Costo"].idxmax(), "Categoria"]
val_mejor_roi   = stats["ROI"].max()
val_menor_roi   = stats["ROI"].min()
cat_menor_roi   = stats.loc[stats["ROI"].idxmin(),   "Categoria"]
 
# ── PREGUNTA CENTRAL ───────────────────────────────────────────────────────
st.markdown("""
<div style="background:#1A202C; border-radius:12px; padding:1.4rem 2rem; margin-bottom:1rem;">
    <p style="color:#B4B2A9; font-size:0.85rem; margin:0 0 0.3rem 0; text-transform:uppercase; letter-spacing:1px;">
        Pregunta central
    </p>
    <p style="color:#F7F7F5; font-size:1.35rem; font-weight:800; margin:0;">
        ¿Estamos invirtiendo el presupuesto donde se genera el mayor impacto social —
        y hay proyectos críticos que nadie está vigilando?
    </p>
</div>
""", unsafe_allow_html=True)
 
st.caption(f"Mostrando {len(df):,} de {len(df_original):,} proyectos según filtros activos")
st.divider()
 
# ── KPIs — 5 columnas, el de alerta en rojo ────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total proyectos",        f"{len(df):,}")
k2.metric("Presupuesto total",      f"USD {pres_total/1e6:.0f}M")
k3.metric("Proyectos retrasados",   f"{len(retrasados):,}",
          f"{len(retrasados)/len(df)*100:.1f}% del total", delta_color="inverse")
k4.metric("Población beneficiada",  f"{df['Poblacion_Beneficiada'].sum()/1e6:.1f}M personas")
k5.metric("Presupuesto en riesgo",  f"USD {pres_retrasado/1e6:.0f}M",
          f"{pct_riesgo:.1f}% parado sin avance", delta_color="inverse")
 
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
 
    roi = stats.sort_values("ROI", ascending=True)
    roi["color"] = [VERDE if v == roi["ROI"].max() else GRIS for v in roi["ROI"]]
    fig_roi = go.Figure(go.Bar(
        x=roi["ROI"], y=roi["Categoria"], orientation='h',
        marker_color=roi["color"],
        text=[f"{v:.2f}" for v in roi["ROI"]], textposition='outside',
        hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
    ))
    fig_roi.update_layout(
        title=dict(text=f"<b>{cat_mejor_roi}: más personas por cada mil dólares invertidos</b>", font_size=14),
        xaxis=dict(title="Personas por USD $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=40), height=320, showlegend=False
    )
    st.plotly_chart(fig_roi, use_container_width=True)
    st.divider()
 
    costo = stats.sort_values("Costo", ascending=True)
    costo["color"] = [NARANJA if v == costo["Costo"].max() else GRIS for v in costo["Costo"]]
    fig_costo = go.Figure(go.Bar(
        x=costo["Costo"], y=costo["Categoria"], orientation='h',
        marker_color=costo["color"],
        text=[f"${v:.1f}" for v in costo["Costo"]], textposition='outside',
        hovertemplate="<b>%{y}</b><br>Costo: $%{x:.1f} por persona<extra></extra>"
    ))
    fig_costo.update_layout(
        title=dict(text=f"<b>{cat_mayor_costo}: mayor costo por persona beneficiada</b>", font_size=14),
        xaxis=dict(title="USD por beneficiario", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=40), height=320, showlegend=False
    )
    st.plotly_chart(fig_costo, use_container_width=True)
    st.divider()
 
    # Conclusión del Tab 1
    brecha_roi = val_mejor_roi / val_menor_roi
    st.markdown(f"""
<div style="background:#F0FFF4; border-left:4px solid #1D9E75; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#276749; font-weight:800; font-size:1rem; margin:0 0 0.4rem 0;">
        Conclusión — ¿Qué hacer con esto?
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.7;">
        <strong>{cat_mejor_roi}</strong> genera <strong>{val_mejor_roi:.0f} personas beneficiadas por cada $1,000</strong> —
        {brecha_roi:.1f}x más eficiente que {cat_menor_roi} ({val_menor_roi:.0f} personas/$1,000).
        En la próxima ronda de asignación presupuestal, cada peso adicional destinado a
        <strong>{cat_mejor_roi}</strong> tiene el mayor retorno social del portafolio.
        <strong>{cat_mayor_costo}</strong> necesita justificar su costo con impacto diferencial demostrable.
    </p>
</div>
""", unsafe_allow_html=True)
 
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
            'tasa':               round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n':                  len(x),
            'presupuesto_total_M': round(x['Presupuesto_USD'].sum() / 1e6, 1),
            'presupuesto_ret_M':  round(x[x['Estado']=='Retrasado']['Presupuesto_USD'].sum() / 1e6, 1),
            'retrasados':         int((x['Estado'] == 'Retrasado').sum())
        }))
        .reset_index()
    )
    orden = ['Alto', 'Medio', 'Bajo']
    imp['orden'] = imp['Nivel_Impacto'].map({v: i for i, v in enumerate(orden)})
    imp = imp.sort_values('orden').reset_index(drop=True)
 
    if 'Alto' not in imp['Nivel_Impacto'].values or 'Medio' not in imp['Nivel_Impacto'].values:
        st.warning("Esta visualización requiere tener seleccionados los niveles **Alto** y **Medio**.")
        st.stop()
 
    tasa_alto      = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
    tasa_medio     = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
    n_medio        = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'retrasados'].values[0]
    pres_ret_alto  = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'presupuesto_ret_M'].values[0]
    pres_ret_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'presupuesto_ret_M'].values[0]
    pres_ret_bajo  = imp.loc[imp['Nivel_Impacto'] == 'Bajo',  'presupuesto_ret_M'].values[0] if 'Bajo' in imp['Nivel_Impacto'].values else 0
    n_ret_bajo     = imp.loc[imp['Nivel_Impacto'] == 'Bajo',  'retrasados'].values[0] if 'Bajo' in imp['Nivel_Impacto'].values else 0
    n_ret_alto     = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'retrasados'].values[0]
    brecha         = tasa_medio - tasa_alto
 
    m1, m2, m3 = st.columns(3)
    m1.metric("Retrasos — Alto impacto",    f"{tasa_alto:.1f}%",  "referencia esperada")
    m2.metric("Retrasos — Medio impacto",   f"{tasa_medio:.1f}%",
              f"{brecha:.1f} pts sobre Alto", delta_color="inverse")
    m3.metric("Presupuesto Medio parado",   f"USD {pres_ret_medio:.0f}M",
              f"{int(n_medio)} proyectos retrasados", delta_color="inverse")
    st.divider()
 
    colores_imp = [ROJO if n == 'Medio' else GRIS for n in imp['Nivel_Impacto']]
    etiquetas   = [f"{v:.1f}%<br>({int(r)} de {int(n)})"
                   for v, n, r in zip(imp['tasa'], imp['n'], imp['retrasados'])]
 
    fig_imp = go.Figure(go.Bar(
        x=imp['Nivel_Impacto'], y=imp['tasa'],
        marker_color=colores_imp,
        text=etiquetas, textposition='outside',
        hovertemplate="<b>Impacto %{x}</b><br>Tasa retraso: %{y:.1f}%<extra></extra>"
    ))
    fig_imp.add_hline(
        y=tasa_alto, line_dash="dash", line_color=VERDE, line_width=2,
        annotation_text=f"Referencia Alto: {tasa_alto:.1f}%",
        annotation_position="top right",
        annotation_font_color=VERDE, annotation_font_size=11
    )
    fig_imp.add_annotation(
        x='Medio', y=tasa_medio,
        text=f"<b>{brecha:.1f} pts sobre Alto</b>",
        showarrow=True, arrowhead=2, arrowcolor=ROJO,
        ax=70, ay=-70, font=dict(color=ROJO, size=11),
        bgcolor="#FFF5F5", bordercolor=ROJO, borderwidth=1
    )
    fig_imp.update_layout(
        title=dict(
            text="<b>Los proyectos de impacto Medio presentan más retrasos que los de Alto</b><br>"
                 "<sup>Una anomalía operativa: reciben menos vigilancia pese al riesgo financiero</sup>",
            font_size=14),
        xaxis=dict(title="Nivel de Impacto", showgrid=False),
        yaxis=dict(title="% de proyectos retrasados", tickformat=".0f", ticksuffix="%",
                   range=[0, max(imp['tasa']) * 1.35], showgrid=True, gridcolor="#E2E8F0"),
        plot_bgcolor="white", paper_bgcolor="white",
        height=420, showlegend=False, margin=dict(l=40, r=40, t=90, b=40)
    )
    st.plotly_chart(fig_imp, use_container_width=True)
 
    st.subheader("Presupuesto real en riesgo por nivel de impacto")
    st.caption("Solo proyectos con estado 'Retrasado' — no el presupuesto total de cada nivel")
    pa, pm, pb = st.columns(3)
    pa.metric("Alto — presupuesto retrasado",  f"USD {pres_ret_alto:.0f}M",
              f"{int(n_ret_alto)} proyectos", delta_color="inverse")
    pm.metric("Medio — presupuesto retrasado", f"USD {pres_ret_medio:.0f}M",
              f"{int(n_medio)} proyectos", delta_color="inverse")
    pb.metric("Bajo — presupuesto retrasado",  f"USD {pres_ret_bajo:.0f}M",
              f"{int(n_ret_bajo)} proyectos", delta_color="inverse")
 
    st.divider()
    st.markdown(f"""
<div style="background:#FFF5F5; border-left:4px solid #C81D25; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#C81D25; font-weight:800; font-size:1rem; margin:0 0 0.4rem 0;">
        Conclusión — ¿Qué hacer con esto?
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.7;">
        Los <strong>{int(n_medio)} proyectos de impacto Medio retrasados</strong> tienen
        <strong>USD {pres_ret_medio:.0f}M parados</strong> — sin avanzar, sin generar impacto.
        Activar seguimiento quincenal para este grupo específico reduciría su tasa al nivel del Alto ({tasa_alto:.1f}%),
        reactivando presupuesto equivalente a financiar proyectos nuevos de {cat_mejor_roi}.
        <strong>No se necesita más dinero — se necesita atención dirigida.</strong>
    </p>
</div>
""", unsafe_allow_html=True)
 
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
 
    # Mensaje contextual si se filtra por Retrasado + Medio
    medio_retrasados = df_tabla[df_tabla['Nivel_Impacto'] == 'Medio'] if estado_filtro == 'Retrasado' else pd.DataFrame()
    if estado_filtro == 'Retrasado' and len(medio_retrasados) > 0:
        pres_medio_tab = medio_retrasados['Presupuesto_USD'].sum() / 1e6
        st.warning(
            f"Estos son los proyectos del punto ciego: **{len(medio_retrasados)} proyectos de impacto Medio retrasados** "
            f"con **USD {pres_medio_tab:.0f}M parados**. Son el foco de intervención prioritaria."
        )
 
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
 
    st.markdown("### Comparativa 1 — Eficiencia por Categoría")
    st.markdown("**Pregunta respondida:** ¿Qué categoría genera más impacto social por dólar invertido?")
 
    antes1, despues1 = st.columns(2)
    roi_exp = stats.sort_values("ROI", ascending=True)
 
    with antes1:
        st.markdown("#### ANTES — Gráfica exploratoria")
        fig_a1 = go.Figure(go.Bar(
            x=roi_exp["ROI"], y=roi_exp["Categoria"], orientation='h',
            marker_color='steelblue',
            text=[f"{v:.2f}" for v in roi_exp["ROI"]], textposition='outside',
        ))
        fig_a1.update_layout(
            title="ROI Social por Categoría",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB"),
            yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_a1, use_container_width=True)
        st.info("**Problema:** Todas las barras en el mismo azul. El ojo no sabe dónde ir.")
 
    with despues1:
        st.markdown("#### DESPUÉS — Gráfica aclaratoria")
        roi_ac = roi_exp.copy()
        roi_ac["color"] = [VERDE if v == roi_ac["ROI"].max() else GRIS for v in roi_ac["ROI"]]
        fig_d1 = go.Figure(go.Bar(
            x=roi_ac["ROI"], y=roi_ac["Categoria"], orientation='h',
            marker_color=roi_ac["color"],
            text=[f"{v:.2f}" for v in roi_ac["ROI"]], textposition='outside',
            hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
        ))
        fig_d1.update_layout(
            title=f"<b>{cat_mejor_roi}: más personas por dólar invertido</b>",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
            yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_d1, use_container_width=True)
        st.success(f"**Solución:** Solo **{cat_mejor_roi}** en verde. Título que comunica el hallazgo.")
 
    with st.expander("Ver justificación — Comparativa 1"):
        st.markdown(f"""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme | Verde solo en {cat_mejor_roi} | Color como énfasis, no decoración |
| **Ordenación** | Sin orden | De menor a mayor ROI | El ojo va hacia la categoría dominante |
| **Título** | Descriptivo | Informativo | Comunica el hallazgo, no la variable |
| **Interactividad** | Estático | Hover con tooltip | Explora sin saturar la gráfica |
        """)
 
    st.divider()
    st.markdown("### Comparativa 2 — Detección de Anomalía")
    st.markdown("**Pregunta respondida:** ¿En qué segmento se concentran los retrasos de forma inesperada?")
 
    antes2, despues2 = st.columns(2)
    imp2 = (
        df.groupby('Nivel_Impacto')
        .apply(lambda x: pd.Series({
            'tasa':       round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n':          len(x),
            'retrasados': int((x['Estado'] == 'Retrasado').sum()),
            'pres_ret_M': round(x[x['Estado']=='Retrasado']['Presupuesto_USD'].sum() / 1e6, 1)
        }))
        .reset_index()
    )
    orden2 = ['Alto', 'Medio', 'Bajo']
    imp2['orden'] = imp2['Nivel_Impacto'].map({v: i for i, v in enumerate(orden2)})
    imp2 = imp2.sort_values('orden').reset_index(drop=True)
 
    if 'Alto' not in imp2['Nivel_Impacto'].values or 'Medio' not in imp2['Nivel_Impacto'].values:
        st.warning("La Comparativa 2 requiere niveles **Alto** y **Medio** activos.")
    else:
        tasa_alto2  = imp2.loc[imp2['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
        tasa_medio2 = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
        n_medio2    = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'retrasados'].values[0]
        pres_ret_m2 = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'pres_ret_M'].values[0]
        pres_ret_a2 = imp2.loc[imp2['Nivel_Impacto'] == 'Alto',  'pres_ret_M'].values[0]
        pres_ret_b2 = imp2.loc[imp2['Nivel_Impacto'] == 'Bajo',  'pres_ret_M'].values[0] if 'Bajo' in imp2['Nivel_Impacto'].values else 0
        brecha2     = tasa_medio2 - tasa_alto2
 
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
                yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
                height=300, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
            )
            st.plotly_chart(fig_a2, use_container_width=True)
            st.info("**Problema:** Todas las barras iguales. La anomalía existe pero es invisible.")
 
        with despues2:
            st.markdown("#### DESPUÉS — Figura / Fondo")
            colores2   = [ROJO if n == 'Medio' else GRIS for n in imp2['Nivel_Impacto']]
            etiquetas2 = [f"{v:.1f}%<br>({int(r)} de {int(n)})"
                          for v, n, r in zip(imp2['tasa'], imp2['n'], imp2['retrasados'])]
            fig_d2 = go.Figure(go.Bar(
                x=imp2['Nivel_Impacto'], y=imp2['tasa'],
                marker_color=colores2, width=0.5,
                text=etiquetas2, textposition='outside',
                hovertemplate="<b>Impacto %{x}</b><br>%{y:.1f}% retrasados<extra></extra>"
            ))
            fig_d2.add_hline(
                y=tasa_alto2, line_dash="dash", line_color=VERDE, line_width=2,
                annotation_text=f"Referencia Alto: {tasa_alto2:.1f}%",
                annotation_position="top right",
                annotation_font_color=VERDE, annotation_font_size=10
            )
            fig_d2.add_annotation(
                x='Medio', y=tasa_medio2,
                text=f"<b>{brecha2:.1f} pts sobre Alto</b>",
                showarrow=True, arrowhead=2, arrowcolor=ROJO,
                ax=60, ay=-50, font=dict(color=ROJO, size=10),
                bgcolor="#FFF5F5", bordercolor=ROJO, borderwidth=1
            )
            fig_d2.update_layout(
                title="<b>Impacto Medio: la anomalía que nadie vigila</b>",
                xaxis=dict(title="Nivel de Impacto", showgrid=False),
                yaxis=dict(title="% retrasados", tickformat=".0f", ticksuffix="%",
                           range=[0, max(imp2['tasa']) * 1.4], showgrid=True, gridcolor="#E2E8F0"),
                plot_bgcolor="white", paper_bgcolor="white",
                height=340, showlegend=False, margin=dict(l=40, r=40, t=50, b=30)
            )
            st.plotly_chart(fig_d2, use_container_width=True)
            st.success("**Solución:** Rojo solo en Medio. Línea de referencia. Etiqueta muestra retrasados reales.")
 
        with st.expander("Ver justificación — Comparativa 2"):
            st.markdown(f"""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme | Rojo en Medio, gris en el resto | Contraste Figura/Fondo |
| **Orientación** | Horizontal | Vertical | 3 grupos: eje X nominal es más natural |
| **Etiqueta** | Solo porcentaje | "X de Y proyectos" | Muestra retrasados reales, no el total |
| **Línea de referencia** | No existe | Línea verde en {tasa_alto2:.1f}% | Permite medir la brecha sin calcular |
| **Anotación** | No existe | "{brecha2:.1f} pts sobre Alto" | El insight está escrito en la gráfica |
| **Ordenación** | Alfabética | Alto → Medio → Bajo | Construye la sorpresa narrativa |
            """)
 
        st.divider()
        st.markdown("### Mensaje para la Gerencia")
        st.markdown(f"""
<div style="background:#1A202C; border-radius:12px; padding:2rem 2.5rem; margin-bottom:1rem;">
    <p style="color:#F7F7F5; font-size:1.05rem; line-height:1.9; margin:0;">
        <span style="color:#1D9E75; font-size:1.3rem; font-weight:800;">
            ¿Estamos invirtiendo donde más impacto generamos?
        </span><br><br>
        <strong style="color:#F7F7F5;">La respuesta corta es: en parte, sí. Pero hay un punto ciego operativo
        que hoy tiene USD {pres_ret_m2:.0f}M completamente parados.</strong>
        <br><br>
        El análisis revela que <strong style="color:#1D9E75;">{cat_mejor_roi} es la categoría más eficiente
        del portafolio</strong> — genera {val_mejor_roi:.0f} personas beneficiadas por cada mil dólares,
        casi el doble que {cat_menor_roi} ({val_menor_roi:.0f}).
        Cada peso adicional en {cat_mejor_roi} tiene el mayor retorno social disponible.
        <br><br>
        Pero hay una anomalía que los reportes estándar no detectan:
        <strong style="color:#C81D25;">los proyectos de impacto Medio tienen la mayor tasa de retrasos
        ({tasa_medio2:.1f}%), superando a los de Alto ({tasa_alto2:.1f}%) —
        exactamente al revés de lo esperado.</strong>
        De sus {int(n_medio2)} proyectos retrasados,
        <strong style="color:#C81D25;">USD {pres_ret_m2:.0f}M están parados hoy</strong> —
        sin avanzar, sin generar impacto. En contraste, Alto tiene USD {pres_ret_a2:.0f}M
        y Bajo USD {pres_ret_b2:.0f}M retrasados. El Medio concentra el problema.
        <br><br>
        <strong style="color:#F7F7F5;">La oportunidad no requiere más presupuesto.
        Requiere dirigir la atención al lugar correcto.</strong>
    </p>
</div>
""", unsafe_allow_html=True)
 
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.markdown(f"""
<div style="background:#F0FFF4; border-left:4px solid #1D9E75; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#276749; font-weight:800; font-size:1rem; margin:0 0 0.5rem 0;">
        ACCION 1 — Priorizar {cat_mejor_roi}
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.6;">
        En la próxima ronda de asignación, incrementar el peso de proyectos de
        <strong>{cat_mejor_roi}</strong>. El ROI de {val_mejor_roi:.0f} personas por $1,000
        justifica la decisión con datos — no con intuición.
    </p>
</div>
""", unsafe_allow_html=True)
 
        with col_rec2:
            st.markdown(f"""
<div style="background:#FFF5F5; border-left:4px solid #C81D25; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#C81D25; font-weight:800; font-size:1rem; margin:0 0 0.5rem 0;">
        ACCION 2 — Intervenir el punto ciego
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.6;">
        Activar seguimiento quincenal para los <strong>{int(n_medio2)} proyectos de impacto
        Medio retrasados</strong> con <strong>USD {pres_ret_m2:.0f}M parados</strong>.
        Reducir su tasa al nivel del Alto ({tasa_alto2:.1f}%) reactivaría recursos
        equivalentes a financiar proyectos nuevos de {cat_mejor_roi}.
    </p>
</div>
""", unsafe_allow_html=True)
 
    st.divider()
    st.markdown("### Principios aplicados")
    c1, c2, c3 = st.columns(3)
    c1.metric("Data-to-Ink Ratio", "Maximizado", "Ejes y bordes eliminados")
    c2.metric("Color selectivo", "1 categoría destacada", "Por gráfica")
    c3.metric("Anotaciones", "Insight en la gráfica", "No en texto externo")
