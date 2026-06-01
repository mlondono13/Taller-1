import pandas as pd
import streamlit as st

@st.cache_data
def cargar_datos():
    df = pd.read_csv('dataset_evaluacion_unidad1.csv')
    df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
    return df

def calcular_stats(df):
    stats = (
        df.groupby("Categoria")[["Presupuesto_USD", "Poblacion_Beneficiada"]]
        .sum()
        .reset_index()
    )
    stats["ROI"]   = stats["Poblacion_Beneficiada"] / stats["Presupuesto_USD"] * 1000
    stats["Costo"] = stats["Presupuesto_USD"] / stats["Poblacion_Beneficiada"]

    meta = {
        "cat_mejor_roi":   stats.loc[stats["ROI"].idxmax(),   "Categoria"],
        "cat_menor_roi":   stats.loc[stats["ROI"].idxmin(),   "Categoria"],
        "cat_mayor_costo": stats.loc[stats["Costo"].idxmax(), "Categoria"],
        "val_mejor_roi":   stats["ROI"].max(),
        "val_menor_roi":   stats["ROI"].min(),
        "val_mayor_costo": stats["Costo"].max(),
    }
    return stats, meta

def calcular_kpis(df):
    retrasados     = df[df['Estado'] == 'Retrasado']
    pres_total     = df['Presupuesto_USD'].sum()
    pres_retrasado = retrasados['Presupuesto_USD'].sum()
    pct_riesgo     = pres_retrasado / pres_total * 100 if pres_total > 0 else 0
    return {
        "total":           len(df),
        "retrasados":      len(retrasados),
        "pct_retrasados":  len(retrasados) / len(df) * 100,
        "pres_total":      pres_total,
        "pres_retrasado":  pres_retrasado,
        "pct_riesgo":      pct_riesgo,
        "poblacion":       df['Poblacion_Beneficiada'].sum(),
    }