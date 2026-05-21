import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Eficiencia por Categoría", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .metric-card { background: #F8F8F7; border-radius: 10px; padding: 1rem 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; color: #FFFFFF; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #FFFFFF; font-size: 1rem; font-weight: bold }
</style>
""", unsafe_allow_html=True)

df = pd.read_csv('dataset_evaluacion_unidad1.csv')
stats = df.groupby("Categoria")[["Presupuesto_USD", "Poblacion_Beneficiada"]].sum().reset_index()
stats["ROI"] = stats["Poblacion_Beneficiada"] / stats["Presupuesto_USD"] * 1000
stats["Costo"] = stats["Presupuesto_USD"] / stats["Poblacion_Beneficiada"]

VERDE  = "#1D9E75"
NARANJA = "#D85A30"
GRIS   = "#B4B2A9"
BG     = "#FFFFFF"
GRID   = "#EBEBEB"
TEXTO  = "#5F5E5A"

st.title("¿Cuál categoría entrega más con menos?")
st.divider()

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

col_a, col_b = st.columns(2)

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

# ── SECCIÓN ANOMALÍA ───────────────────────────────────────────────────────
st.title("¿Dónde están los proyectos que nadie vigila?")
st.caption("Detección de anomalía · Contraste Figura-Fondo por nivel de impacto")
st.divider()

imp = (
    df.groupby('Nivel_Impacto')
    .apply(lambda x: pd.Series({
        'tasa': round((x['Estado'] == 'Retrasado').sum() / len(x) * 100, 1),
        'n': len(x),
        'presupuesto_M': round(x['Presupuesto_USD'].sum() / 1e6, 1)
    }))
    .reset_index()
)
orden = ['Alto', 'Medio', 'Bajo']
imp['orden'] = imp['Nivel_Impacto'].map({v: i for i, v in enumerate(orden)})
imp = imp.sort_values('orden').reset_index(drop=True)

GRIS_A = '#B4B2A9'
ROJO   = '#C81D25'
BG_A   = '#F7F7F5'
DARK   = '#1A202C'
LIGHT  = '#718096'
VERDE_A = '#276749'

# Métricas de contexto
m1, m2, m3 = st.columns(3)
tasa_alto  = imp.loc[imp['Nivel_Impacto'] == 'Alto',  'tasa'].values[0]
tasa_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'tasa'].values[0]
pres_medio = imp.loc[imp['Nivel_Impacto'] == 'Medio', 'presupuesto_M'].values[0]
m1.metric("Retrasos — Alto impacto",  f"{tasa_alto:.1f}%",  "referencia esperada")
m2.metric("Retrasos — Medio impacto", f"{tasa_medio:.1f}%", f"+{tasa_medio - tasa_alto:.1f} pts ↑", delta_color="inverse")
m3.metric("Presupuesto en riesgo",    f"USD {pres_medio:.0f}M", "proyectos de impacto Medio")

st.divider()

fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=BG_A)
ax.set_facecolor(BG_A)

colores = [ROJO if row['Nivel_Impacto'] == 'Medio' else GRIS_A for _, row in imp.iterrows()]
bars = ax.barh(imp['Nivel_Impacto'], imp['tasa'], color=colores, height=0.5, zorder=3)

for bar, (_, row) in zip(bars, imp.iterrows()):
    es_anomalia = row['Nivel_Impacto'] == 'Medio'
    ax.text(bar.get_width() + 0.45, bar.get_y() + bar.get_height() / 2,
            f"{row['tasa']:.1f}%  ({row['n']} proyectos)",
            va='center', ha='left',
            fontsize=10 if es_anomalia else 9,
            fontweight='bold' if es_anomalia else 'normal',
            color=ROJO if es_anomalia else LIGHT)

ax.axvline(tasa_alto, color=VERDE_A, lw=1.5, ls=(0, (4, 3)), zorder=2)
ax.text(tasa_alto, -0.72, f'Referencia Alto\n{tasa_alto:.1f}%',
        ha='center', va='bottom', fontsize=8.5, color=VERDE_A, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.28', fc='#F0FFF4', ec=VERDE_A, lw=0.8))

brecha = tasa_medio - tasa_alto
ax.annotate(f'{brecha:.1f} pts\nmás que Alto',
    xy=(tasa_medio - 1.8, 1), xytext=(tasa_medio - 3, 0.35),
    fontsize=9, color=ROJO, fontweight='bold',
    arrowprops=dict(arrowstyle='-|>', color=ROJO, lw=1.4, shrinkA=5, shrinkB=5),
    bbox=dict(boxstyle='round,pad=0.45', fc='#FFF5F5', ec=ROJO, lw=1), ha='center')

ax.text(0.98, 0.06, f'USD {pres_medio:.0f}M comprometidos\nen proyectos de impacto Medio',
    transform=ax.transAxes, ha='right', fontsize=8.5, color=ROJO, style='italic',
    bbox=dict(boxstyle='round,pad=0.35', fc='#FFF5F5', ec=ROJO, lw=0.8))

ax.spines[['top', 'right']].set_visible(False)
ax.spines['left'].set_color('#D1D5DB')
ax.spines['bottom'].set_color('#D1D5DB')
ax.tick_params(left=False, bottom=True, colors=LIGHT)
ax.set_xlim(0, 30)
ax.set_ylim(2.6, -0.8)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
ax.set_xticklabels(['0%', '5%', '10%', '15%', '20%', '25%', '30%'], fontsize=8.5, color=LIGHT)
ax.set_yticks(range(len(imp)))
ax.set_yticklabels(imp['Nivel_Impacto'], fontsize=11, color=DARK, fontweight='bold')
ax.xaxis.grid(True, color='#E2E8F0', lw=0.8, linestyle='--', zorder=0)
ax.set_xlabel('% de proyectos retrasados', fontsize=9, color=LIGHT, labelpad=10)
ax.set_ylabel('Nivel de Impacto', fontsize=9, color=LIGHT, labelpad=10)
fig.suptitle('Los proyectos de impacto Medio presentan más retrasos que los de Alto impacto',
    fontsize=13, fontweight='bold', color=DARK, y=0.96)
fig.text(0.5, 0.91, 'Una anomalía operativa: reciben menos vigilancia pese al riesgo financiero asociado',
    ha='center', fontsize=9, color=LIGHT, style='italic')
plt.tight_layout(rect=[0, 0, 1, 0.88])

st.pyplot(fig)
st.divider()col2.metric("Presupuesto total", f"${df['Presupuesto_USD'].sum():,}")

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
