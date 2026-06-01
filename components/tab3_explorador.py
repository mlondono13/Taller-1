import pandas as pd
import streamlit as st

def render(df, meta):
    st.subheader("Explorador de proyectos")
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

    # Alerta contextual cuando se filtra por Retrasado
    if estado_filtro == 'Retrasado':
        medio_ret = df_tabla[df_tabla['Nivel_Impacto'] == 'Medio']
        if len(medio_ret) > 0:
            pres_medio = medio_ret['Presupuesto_USD'].sum() / 1e6
            st.warning(
                f"Estos son los proyectos del punto ciego: "
                f"**{len(medio_ret)} proyectos de impacto Medio retrasados** "
                f"con **USD {pres_medio:.0f}M parados**. "
                "Son el foco de intervención prioritaria."
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