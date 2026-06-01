import plotly.graph_objects as go
import streamlit as st
from utils.colores import VERDE, NARANJA, GRIS

def render(stats, meta):
    st.subheader("¿Cuál categoría entrega más con menos?")
    st.caption("Eficiencia social del portafolio · ROI y Costo por beneficiario")
    st.divider()

    grafica_roi(stats, meta)
    st.divider()
    grafica_costo(stats, meta)
    st.divider()
    conclusion(meta)

def grafica_roi(stats, meta):
    roi = stats.sort_values("ROI", ascending=True).copy()
    roi["color"] = [VERDE if v == roi["ROI"].max() else GRIS for v in roi["ROI"]]

    fig = go.Figure(go.Bar(
        x=roi["ROI"], y=roi["Categoria"], orientation='h',
        marker_color=roi["color"],
        text=[f"{v:.2f}" for v in roi["ROI"]], textposition='outside',
        hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f} personas/$1.000<extra></extra>"
    ))
    fig.update_layout(
        title=dict(
            text=f"<b>{meta['cat_mejor_roi']}: más personas por cada mil dólares invertidos</b>",
            font_size=14),
        xaxis=dict(title="Personas por USD $1.000", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=40), height=320, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def grafica_costo(stats, meta):
    costo = stats.sort_values("Costo", ascending=True).copy()
    costo["color"] = [NARANJA if v == costo["Costo"].max() else GRIS for v in costo["Costo"]]

    fig = go.Figure(go.Bar(
        x=costo["Costo"], y=costo["Categoria"], orientation='h',
        marker_color=costo["color"],
        text=[f"${v:.1f}" for v in costo["Costo"]], textposition='outside',
        hovertemplate="<b>%{y}</b><br>Costo: $%{x:.1f} por persona<extra></extra>"
    ))
    fig.update_layout(
        title=dict(
            text=f"<b>{meta['cat_mayor_costo']}: mayor costo por persona beneficiada</b>",
            font_size=14),
        xaxis=dict(title="USD por beneficiario", showgrid=True, gridcolor="#EBEBEB", zeroline=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=40), height=320, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def conclusion(meta):
    brecha = meta["val_mejor_roi"] / meta["val_menor_roi"]
    st.markdown(f"""
<div style="background:#F0FFF4; border-left:4px solid #1D9E75; border-radius:6px; padding:1.2rem 1.5rem;">
    <p style="color:#276749; font-weight:800; font-size:1rem; margin:0 0 0.4rem 0;">
        Conclusión — ¿Qué hacer con esto?
    </p>
    <p style="color:#1A202C; font-size:0.92rem; margin:0; line-height:1.7;">
        <strong>{meta['cat_mejor_roi']}</strong> genera
        <strong>{meta['val_mejor_roi']:.0f} personas beneficiadas por cada $1,000</strong> —
        {brecha:.1f}x más eficiente que {meta['cat_menor_roi']}
        ({meta['val_menor_roi']:.0f} personas/$1,000).
        En la próxima ronda de asignación presupuestal, cada peso adicional destinado a
        <strong>{meta['cat_mejor_roi']}</strong> tiene el mayor retorno social del portafolio.
        <strong>{meta['cat_mayor_costo']}</strong> necesita justificar su costo
        con impacto diferencial demostrable.
    </p>
</div>
""", unsafe_allow_html=True)