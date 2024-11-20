import streamlit as st
import pandas as pd
import altair as alt

# Configuración de la página
st.set_page_config(page_title="Dashboard de Marketing", layout="wide")

# Cargar los datos
try:
    df = pd.read_csv('marketing_data_clean.csv')  # Asegúrate de exportar el DataFrame limpio a un archivo CSV.
    st.success("Archivo cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# Verificar las columnas del DataFrame
st.write("Columnas del DataFrame:", df.columns.tolist())

# Listar columnas relevantes para filtros y gráficos
unidad_columns = [col for col in df.columns if col.startswith('Unidad_de_negocio_asignada')]
fuente_columns = [col for col in df.columns if col.startswith('Fuente_original')]

if not unidad_columns or not fuente_columns:
    st.error("No se encontraron columnas relacionadas con unidades de negocio o fuentes originales en el archivo.")
    st.stop()

# Combinar nombres de columnas para filtros amigables
unidad_map = {col: col.replace('Unidad_de_negocio_asignada_', '') for col in unidad_columns}
fuente_map = {col: col.replace('Fuente_original_', '') for col in fuente_columns}

# Filtros
unidad_seleccion = st.multiselect("Selecciona Unidad de Negocio:", options=list(unidad_map.values()))
fuente_seleccion = st.multiselect("Selecciona Fuente Original:", options=list(fuente_map.values()))

# Filtrar el DataFrame
df_filtered = df.copy()
if unidad_seleccion:
    selected_unidades = [key for key, val in unidad_map.items() if val in unidad_seleccion]
    df_filtered = df_filtered[df_filtered[selected_unidades].sum(axis=1) > 0]

if fuente_seleccion:
    selected_fuentes = [key for key, val in fuente_map.items() if val in fuente_seleccion]
    df_filtered = df_filtered[df_filtered[selected_fuentes].sum(axis=1) > 0]

# Gráficos
st.subheader("Distribución por Etapas")
etapas_chart = alt.Chart(df_filtered).mark_bar().encode(
    x=alt.X("Etapa_del_negocio:N", title="Etapas"),
    y=alt.Y("count():Q", title="Cantidad"),
    color="Etapa_del_negocio:N"
).properties(width=600, height=400)
st.altair_chart(etapas_chart, use_container_width=True)

st.subheader("Distribución por Fuente Original")
fuente_chart = alt.Chart(df_filtered).transform_fold(
    fuente_columns,
    as_=['Fuente', 'Value']
).transform_filter(
    alt.datum.Value > 0
).mark_bar().encode(
    x=alt.X("Fuente:N", title="Fuente Original"),
    y=alt.Y("sum(Value):Q", title="Cantidad"),
    color="Fuente:N"
).properties(width=600, height=400)
st.altair_chart(fuente_chart, use_container_width=True)

# Resumen y conclusiones
st.subheader("Resumen y Conclusiones")
st.markdown("""
- Las **Fuentes sin conexión** y **Redes sociales de pago** tienen alta probabilidad de conversión a la etapa de Nutrición.
- **Referencias** tienen un impacto negativo en la conversión.
- Estas observaciones pueden ayudar a priorizar recursos en canales más efectivos.
""")

