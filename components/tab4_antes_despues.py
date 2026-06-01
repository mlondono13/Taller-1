import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.colores import VERDE, ROJO, GRIS

def render(df, stats, meta):
    st.subheader("Fase 2: Composición del Mensaje")
    st.caption("Transformación de gráficas exploratorias en argumentos visuales aclaratorios")
    st.divider()

    comparativa_1(stats, meta)
    st.divider()
    comparativa_2(df, meta)
    st.divider()

# Comparativa 1 
def comparativa_1(stats, meta):
    st.markdown("### Comparativa 1 — Eficiencia por Categoría")
    st.markdown("**Pregunta respondida:** ¿Qué categoría genera más impacto social por dólar invertido?")

    roi_exp = stats.sort_values("ROI", ascending=True)
    antes, despues = st.columns(2)

    with antes:
        st.markdown("#### ANTES — Gráfica exploratoria")
        fig = go.Figure(go.Bar(
            x=roi_exp["ROI"], y=roi_exp["Categoria"], orientation='h',
            marker_color='steelblue',
            text=[f"{v:.2f}" for v in roi_exp["ROI"]], textposition='outside',
        ))
        fig.update_layout(
            title="ROI Social por Categoría",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB"),
            yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("**Problema:** Todas las barras en el mismo azul. El ojo no sabe dónde ir.")

    with despues:
        st.markdown("#### DESPUÉS — Gráfica aclaratoria")
        roi_ac = roi_exp.copy()
        roi_ac["color"] = [VERDE if v == roi_ac["ROI"].max() else GRIS for v in roi_ac["ROI"]]
        fig = go.Figure(go.Bar(
            x=roi_ac["ROI"], y=roi_ac["Categoria"], orientation='h',
            marker_color=roi_ac["color"],
            text=[f"{v:.2f}" for v in roi_ac["ROI"]], textposition='outside',
            hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
        ))
        fig.update_layout(
            title=f"<b>{meta['cat_mejor_roi']}: más personas por dólar invertido</b>",
            xaxis=dict(title="Personas por $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
            yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
            height=320, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"**Solución:** Solo **{meta['cat_mejor_roi']}** en verde. Título que comunica el hallazgo.")

    with st.expander("Ver justificación — Comparativa 1"):
        st.markdown(f"""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme | Verde solo en {meta['cat_mejor_roi']} | Color como énfasis, no decoración |
| **Ordenación** | Sin orden | De menor a mayor ROI | El ojo va hacia la categoría dominante |
| **Título** | Descriptivo | Informativo | Comunica el hallazgo, no la variable |
| **Interactividad** | Estático | Hover con tooltip | Explora sin saturar la gráfica |
        """)

#  Comparativa 2 
def calcular_impacto(df):
    imp = (
        df.groupby('Nivel_Impacto')
        .apply(lambda x: pd.Series({
            'tasa':       round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n':          len(x),
            'retrasados': int((x['Estado'] == 'Retrasado').sum()),
            'pres_ret_M': round(x[x['Estado'] == 'Retrasado']['Presupuesto_USD'].sum() / 1e6, 1),
        }))
        .reset_index()
    )
    orden = ['Alto', 'Medio', 'Bajo']
    imp['orden'] = imp['Nivel_Impacto'].map({v: i for i, v in enumerate(orden)})
    return imp.sort_values('orden').reset_index(drop=True)

def comparativa_2(df, meta):
    st.markdown("### Comparativa 2 — Detección de Anomalía")
    st.markdown("**Pregunta respondida:** ¿En qué segmento se concentran los retrasos de forma inesperada?")

    imp2 = calcular_impacto(df)

    if 'Alto' not in imp2['Nivel_Impacto'].values or 'Medio' not in imp2['Nivel_Impacto'].values:
        st.warning("La Comparativa 2 requiere niveles **Alto** y **Medio** activos en los filtros.")
        return

    tasa_alto2  = imp2.loc[imp2['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
    tasa_medio2 = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
    n_medio2    = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'retrasados'].values[0]
    pres_ret_m2 = imp2.loc[imp2['Nivel_Impacto'] == 'Medio', 'pres_ret_M'].values[0]
    pres_ret_a2 = imp2.loc[imp2['Nivel_Impacto'] == 'Alto',  'pres_ret_M'].values[0]
    pres_ret_b2 = imp2.loc[imp2['Nivel_Impacto'] == 'Bajo',  'pres_ret_M'].values[0] if 'Bajo' in imp2['Nivel_Impacto'].values else 0
    brecha2     = tasa_medio2 - tasa_alto2

    antes2, despues2 = st.columns(2)

    with antes2:
        st.markdown("#### ANTES — Sin contraste")
        fig_a = go.Figure(go.Bar(
            x=imp2['tasa'], y=imp2['Nivel_Impacto'], orientation='h',
            marker_color='steelblue', width=0.5,
            text=[f"{v:.1f}%" for v in imp2['tasa']], textposition='outside',
        ))
        fig_a.update_layout(
            title="Tasa de retraso por nivel de impacto",
            xaxis=dict(title="% retrasados", range=[0, 25], showgrid=True, gridcolor="#EBEBEB"),
            yaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
            height=300, showlegend=False, margin=dict(l=10, r=60, t=40, b=30)
        )
        st.plotly_chart(fig_a, use_container_width=True)
        st.info("**Problema:** Todas las barras iguales. La anomalía existe pero es invisible.")

    with despues2:
        st.markdown("#### DESPUÉS — Figura / Fondo")
        colores2   = [ROJO if n == 'Medio' else GRIS for n in imp2['Nivel_Impacto']]
        etiquetas2 = [f"{v:.1f}%<br>({int(r)} de {int(n)})"
                      for v, n, r in zip(imp2['tasa'], imp2['n'], imp2['retrasados'])]
        fig_d = go.Figure(go.Bar(
            x=imp2['Nivel_Impacto'], y=imp2['tasa'],
            marker_color=colores2, width=0.5,
            text=etiquetas2, textposition='outside',
            hovertemplate="<b>Impacto %{x}</b><br>%{y:.1f}% retrasados<extra></extra>"
        ))
        fig_d.add_hline(
            y=tasa_alto2, line_dash="dash", line_color=VERDE, line_width=2,
            annotation_text=f"Referencia Alto: {tasa_alto2:.1f}%",
            annotation_position="top right",
            annotation_font_color=VERDE, annotation_font_size=10
        )
        fig_d.add_annotation(
            x='Medio', y=tasa_medio2,
            text=f"<b>+{brecha2:.1f} pts sobre Alto</b>",
            showarrow=True, arrowhead=2, arrowcolor=ROJO,
            ax=-80, ay=-50, font=dict(color=ROJO, size=10),
            bgcolor="#FFF5F5", bordercolor=ROJO, borderwidth=1, xanchor='right'
        )
        fig_d.update_layout(
            title="<b>Impacto Medio: la anomalía que nadie vigila</b>",
            xaxis=dict(title="Nivel de Impacto", showgrid=False),
            yaxis=dict(title="% retrasados", tickformat=".0f", ticksuffix="%",
                       range=[0, max(imp2['tasa']) * 1.55], showgrid=True, gridcolor="#E2E8F0"),
            plot_bgcolor="white", paper_bgcolor="white",
            height=340, showlegend=False, margin=dict(l=40, r=40, t=50, b=30)
        )
        st.plotly_chart(fig_d, use_container_width=True)
        st.success("**Solución:** Rojo solo en Medio. Línea de referencia. Etiqueta muestra retrasados reales.")

    with st.expander("Ver justificación — Comparativa 2"):
        st.markdown(f"""
| Decisión | Antes | Después | Justificación |
|----------|-------|---------|---------------|
| **Color** | Azul uniforme | Rojo en Medio, gris en el resto | Contraste Figura/Fondo |
| **Orientación** | Horizontal | Vertical | 3 grupos: eje X nominal es más natural |
| **Etiqueta** | Solo porcentaje | "X de Y proyectos" | Muestra retrasados reales, no el total |
| **Línea de referencia** | No existe | Línea verde en {tasa_alto2:.1f}% | Permite medir la brecha sin calcular |
| **Anotación** | No existe | "+{brecha2:.1f} pts sobre Alto" | El insight está escrito en la gráfica |
| **Ordenación** | Alfabética | Alto → Medio → Bajo | Construye la sorpresa narrativa |
        """)

    st.divider()
    mensaje_gerencia(meta, tasa_alto2, tasa_medio2, n_medio2, pres_ret_m2, pres_ret_a2, pres_ret_b2)

def mensaje_gerencia(meta, tasa_alto2, tasa_medio2, n_medio2,
                       pres_ret_m2, pres_ret_a2, pres_ret_b2):
    st.markdown("### Mensaje para la Gerencia")
    st.markdown(f"""
<div style="background:#1A202C; border-radius:12px; padding:2rem 2.5rem; margin-bottom:1rem;">
    <p style="color:#F7F7F5; font-size:1.05rem; line-height:1.9; margin:0;">
        <span style="color:#1D9E75; font-size:1.3rem; font-weight:800;">
            ¿Estamos invirtiendo donde más impacto generamos?
        </span><br><br>
        <strong style="color:#F7F7F5;">La respuesta corta es: en parte, sí. Pero hay un punto ciego
        operativo que hoy tiene USD {pres_ret_m2:.0f}M completamente parados.</strong>
        <br><br>
        El análisis revela que
        <strong style="color:#1D9E75;">{meta['cat_mejor_roi']} es la categoría más eficiente
        del portafolio</strong> — genera {meta['val_mejor_roi']:.0f} personas beneficiadas
        por cada mil dólares, casi el doble que {meta['cat_menor_roi']}
        ({meta['val_menor_roi']:.0f}).
        Cada peso adicional en {meta['cat_mejor_roi']} tiene el mayor retorno social disponible.
        <br><br>
        Pero hay una anomalía que los reportes estándar no detectan:
        <strong style="color:#C81D25;">los proyectos de impacto Medio tienen la mayor tasa
        de retrasos ({tasa_medio2:.1f}%), superando a los de Alto ({tasa_alto2:.1f}%) —
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div style="background:#F0FFF4; border-left:4px solid #1D9E75; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#276749; font-weight:800; font-size:1rem; margin:0 0 0.5rem 0;">
        ACCION 1 — Priorizar {meta['cat_mejor_roi']}
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.6;">
        En la próxima ronda de asignación, incrementar el peso de proyectos de
        <strong>{meta['cat_mejor_roi']}</strong>.
        El ROI de {meta['val_mejor_roi']:.0f} personas por $1,000
        justifica la decisión con datos — no con intuición.
    </p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div style="background:#FFF5F5; border-left:4px solid #C81D25; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#C81D25; font-weight:800; font-size:1rem; margin:0 0 0.5rem 0;">
        ACCION 2 — Intervenir el punto ciego
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.6;">
        Activar seguimiento quincenal para los
        <strong>{int(n_medio2)} proyectos de impacto Medio retrasados</strong>
        con <strong>USD {pres_ret_m2:.0f}M parados</strong>.
        Reducir su tasa al nivel del Alto ({tasa_alto2:.1f}%) reactivaría recursos
        equivalentes a financiar proyectos nuevos de {meta['cat_mejor_roi']}.
    </p>
</div>
""", unsafe_allow_html=True)