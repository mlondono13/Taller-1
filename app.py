import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Eficiencia por Categoría", layout="wide")

# Estilo global
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-card { background: #F8F8F7; border-radius: 10px; padding: 1rem 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; color: #FFFFFF; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #FFFFFF; font-size: 1rem;  font-weight: bold}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv('dataset_evaluacion_unidad1.csv')
stats = df.groupby("Categoria")[["Presupuesto_USD", "Poblacion_Beneficiada"]].sum().reset_index()
stats["ROI"] = stats["Poblacion_Beneficiada"] / stats["Presupuesto_USD"] * 1000
stats["Costo"] = stats["Presupuesto_USD"] / stats["Poblacion_Beneficiada"]

VERDE = "#1D9E75"
NARANJA = "#D85A30"
GRIS = "#B4B2A9"
BG = "#FFFFFF"
GRID = "#EBEBEB"
TEXTO = "#5F5E5A"

# Header
st.title("¿Cuál categoría entrega más con menos?")

st.divider()

# Métricas
col1, col2 = st.columns(2)
col1.metric("Proyectos", len(df))
col2.metric("Presupuesto total", f"${df['Presupuesto_USD'].sum():,}")

st.divider()

def limpiar_ax(ax):
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_facecolor(BG)

# Layout: dos columnas
col_a, col_b = st.columns(2)

# Gráfica 1: ROI
with col_a:
    st.subheader("ROI Social")
    st.caption("Personas beneficiadas por cada $1.000 invertidos · Mayor es mejor")

    roi = stats.sort_values("ROI")
    top_roi = roi["ROI"].nlargest(1).min()
    colores_roi = [VERDE if v >= top_roi else GRIS for v in roi["ROI"]]

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor(BG)
    bars = ax.barh(roi["Categoria"], roi["ROI"], color=colores_roi, height=0.5)
    for bar, val in zip(bars, roi["ROI"]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}", va="center", fontsize=10, color=TEXTO)
    for label, color in zip(ax.get_yticklabels(), colores_roi):
        label.set_color(color)
        if color == VERDE:
            label.set_fontweight("bold")
    limpiar_ax(ax)
    ax.set_xlabel("Personas por $1.000", color=TEXTO, fontsize=10)
    ax.set_xlim(6, roi["ROI"].max() + 0.6)
    fig.tight_layout()
    st.pyplot(fig)

# Gráfica 2: Costo
with col_b:
    st.subheader("Costo por Beneficiario")
    st.caption("Dólares invertidos por cada persona atendida · Menor es mejor")

    costo = stats.sort_values("Costo")
    top_costo = costo["Costo"].nlargest(1).min()
    colores_costo = [NARANJA if v >= top_costo else GRIS for v in costo["Costo"]]

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor(BG)
    bars = ax.barh(costo["Categoria"], costo["Costo"], color=colores_costo, height=0.5)
    for bar, val in zip(bars, costo["Costo"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"${val:.1f}", va="center", fontsize=10, color=TEXTO)
    for label, color in zip(ax.get_yticklabels(), colores_costo):
        label.set_color(color)
        if color == NARANJA:
            label.set_fontweight("bold")
    limpiar_ax(ax)
    ax.set_xlabel("USD por persona", color=TEXTO, fontsize=10)
    ax.set_xlim(90, costo["Costo"].max() + 8)
    fig.tight_layout()
    st.pyplot(fig)

st.divider()
