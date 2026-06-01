import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.colores import VERDE, ROJO, GRIS

def calcular_impacto(df):
    imp = (
        df.groupby('Nivel_Impacto')
        .apply(lambda x: pd.Series({
            'tasa': round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
            'n': len(x),
            'presupuesto_ret_M': round(x[x['Estado'] == 'Retrasado']['Presupuesto_USD'].sum() / 1e6, 1),
            'retrasados': int((x['Estado'] == 'Retrasado').sum()),
        }))
        .reset_index()
    )
    orden = ['Alto', 'Medio', 'Bajo']
    imp['orden'] = imp['Nivel_Impacto'].map({v: i for i, v in enumerate(orden)})
    return imp.sort_values('orden').reset_index(drop=True)


def render(df, meta):
    st.subheader("¿Dónde están los proyectos que nadie vigila?")
    st.divider()

    imp = calcular_impacto(df)

    if 'Alto' not in imp['Nivel_Impacto'].values or 'Medio' not in imp['Nivel_Impacto'].values:
        st.warning("Esta visualización requiere los niveles **Alto** y **Medio** activos en el sidebar.")
        st.stop()

    # Valores clave
    tasa_alto = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
    tasa_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
    n_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'retrasados'].values[0]
    n_ret_alto = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'retrasados'].values[0]
    n_ret_bajo = imp.loc[imp['Nivel_Impacto'] == 'Bajo',  'retrasados'].values[0] if 'Bajo' in imp['Nivel_Impacto'].values else 0
    pres_ret_alto = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'presupuesto_ret_M'].values[0]
    pres_ret_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'presupuesto_ret_M'].values[0]
    pres_ret_bajo = imp.loc[imp['Nivel_Impacto'] == 'Bajo',  'presupuesto_ret_M'].values[0] if 'Bajo' in imp['Nivel_Impacto'].values else 0
    brecha = tasa_medio - tasa_alto

    kpis(tasa_alto, tasa_medio, brecha, pres_ret_medio, n_medio)
    st.divider()
    grafica_barras(imp, tasa_alto, tasa_medio, brecha)
    presupuesto_riesgo(pres_ret_alto, pres_ret_medio, pres_ret_bajo, n_ret_alto, n_medio, n_ret_bajo)
    st.divider()
    conclusion(n_medio, pres_ret_medio, tasa_alto, meta['cat_mejor_roi'])


def kpis(tasa_alto, tasa_medio, brecha, pres_ret_medio, n_medio):
    m1, m2, m3 = st.columns(3)
    m1.metric("Retrasos — Alto impacto",  f"{tasa_alto:.1f}%", "referencia esperada")
    m2.metric("Retrasos — Medio impacto", f"{tasa_medio:.1f}%",
              f"{brecha:.1f} pts sobre Alto", delta_color="inverse")
    m3.metric("Presupuesto Medio parado", f"USD {pres_ret_medio:.0f}M",
              f"{int(n_medio)} proyectos retrasados", delta_color="inverse")


def grafica_barras(imp, tasa_alto, tasa_medio, brecha):
    colores = [ROJO if n == 'Medio' else GRIS for n in imp['Nivel_Impacto']]
    etiquetas = [f"{v:.1f}%<br>({int(r)} de {int(n)})"
                 for v, n, r in zip(imp['tasa'], imp['n'], imp['retrasados'])]

    fig = go.Figure(go.Bar(
        x=imp['Nivel_Impacto'], y=imp['tasa'],
        marker_color=colores,
        text=etiquetas, textposition='outside',
        hovertemplate="<b>Impacto %{x}</b><br>Tasa retraso: %{y:.1f}%<extra></extra>"
    ))
    fig.add_hline(
        y=tasa_alto, line_dash="dash", line_color=VERDE, line_width=2,
        annotation_text=f"Referencia Alto: {tasa_alto:.1f}%",
        annotation_position="top right",
        annotation_font_color=VERDE, annotation_font_size=11
    )
    fig.add_annotation(
        x='Medio', y=tasa_medio,
        text=f"<b>+{brecha:.1f} pts sobre Alto</b>",
        showarrow=True, arrowhead=2, arrowcolor=ROJO,
        ax=-80, ay=-50, font=dict(color=ROJO, size=11),
        bgcolor="#FFF5F5", bordercolor=ROJO, borderwidth=1, xanchor='right'
    )
    fig.update_layout(
        title=dict(
            text="<b>Los proyectos de impacto Medio presentan más retrasos que los de Alto</b><br>"
                 "<sup>Una anomalía operativa: reciben menos vigilancia pese al riesgo financiero</sup>",
            font_size=20),
        xaxis=dict(title="Nivel de Impacto", showgrid=False),
        yaxis=dict(title="% de proyectos retrasados", tickformat=".0f", ticksuffix="%",
                   range=[0, max(imp['tasa']) * 1.55], showgrid=True, gridcolor="#E2E8F0"),
        plot_bgcolor="white", paper_bgcolor="white",
        height=420, showlegend=False, margin=dict(l=40, r=40, t=90, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def presupuesto_riesgo(pres_ret_alto, pres_ret_medio, pres_ret_bajo,
                         n_ret_alto, n_medio, n_ret_bajo):
    st.subheader("Presupuesto real en riesgo por nivel de impacto")
    st.caption("Solo proyectos con estado 'Retrasado' — no el presupuesto total de cada nivel")
    pa, pm, pb = st.columns(3)
    pa.metric("Alto — presupuesto retrasado",  f"USD {pres_ret_alto:.0f}M",
              f"{int(n_ret_alto)} proyectos", delta_color="inverse")
    pm.metric("Medio — presupuesto retrasado", f"USD {pres_ret_medio:.0f}M",
              f"{int(n_medio)} proyectos", delta_color="inverse")
    pb.metric("Bajo — presupuesto retrasado",  f"USD {pres_ret_bajo:.0f}M",
              f"{int(n_ret_bajo)} proyectos", delta_color="inverse")


def conclusion(n_medio, pres_ret_medio, tasa_alto, cat_mejor_roi):
    st.markdown(f"""
<div style="background:#FFF5F5; border-left:4px solid #C81D25; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#C81D25; font-weight:800; font-size:1rem; margin:0 0 0.4rem 0;">
        Conclusión — ¿Qué hacer con esto?
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.7;">
        Los <strong>{int(n_medio)} proyectos de impacto Medio retrasados</strong> tienen
        <strong>USD {pres_ret_medio:.0f}M parados</strong> — sin avanzar, sin generar impacto.
        Activar seguimiento quincenal para este grupo específico reduciría su tasa al nivel
        del Alto ({tasa_alto:.1f}%), reactivando presupuesto equivalente a financiar proyectos
        nuevos de {cat_mejor_roi}.
        <strong>No se necesita más dinero — se necesita atención dirigida.</strong>
    </p>
</div>
""", unsafe_allow_html=True)