
import streamlit as st
import pandas as pd
import altair as alt

# Configuración de la página (debe estar al inicio)
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

# Manejo de errores para columnas faltantes
if "Unidad_de_negocio_asignada" not in df.columns or "Fuente_original" not in df.columns:
    st.error("El archivo cargado no contiene las columnas necesarias: 'Unidad_de_negocio_asignada' o 'Fuente_original'.")
    st.stop()

# Título del dashboard
st.title("Dashboard Interactivo de Oportunidades de Venta")

# Filtros
unidad_negocio = st.multiselect("Selecciona Unidad de Negocio:", options=df["Unidad_de_negocio_asignada"].unique())
fuente_original = st.multiselect("Selecciona Fuente Original:", options=df["Fuente_original"].unique())

# Aplicar filtros
df_filtered = df.copy()
if unidad_negocio:
    df_filtered = df_filtered[df_filtered["Unidad_de_negocio_asignada"].isin(unidad_negocio)]
if fuente_original:
    df_filtered = df_filtered[df_filtered["Fuente_original"].isin(fuente_original)]

# Gráficos
st.subheader("Distribución por Etapas")
etapas_chart = alt.Chart(df_filtered).mark_bar().encode(
    x=alt.X("Etapa_del_negocio:N", title="Etapas"),
    y=alt.Y("count():Q", title="Cantidad"),
    color="Etapa_del_negocio:N"
).properties(width=600, height=400)
st.altair_chart(etapas_chart, use_container_width=True)

st.subheader("Distribución por Fuente Original")
fuente_chart = alt.Chart(df_filtered).mark_bar().encode(
    x=alt.X("Fuente_original:N", title="Fuente Original"),
    y=alt.Y("count():Q", title="Cantidad"),
    color="Fuente_original:N"
).properties(width=600, height=400)
st.altair_chart(fuente_chart, use_container_width=True)

st.subheader("Resultados de Modelos Probit y Logit")
st.text("Modelo Probit:")
st.text("""Resultados no disponibles en esta vista.""")
st.text("Modelo Logit:")
st.text("""Resultados no disponibles en esta vista.""")

# Resumen y conclusiones
st.subheader("Resumen y Conclusiones")
st.markdown("""
- Las **Fuentes sin conexión** y **Redes sociales de pago** tienen alta probabilidad de conversión a la etapa de Nutrición.
- **Referencias** tienen un impacto negativo en la conversión.
- Estas observaciones pueden ayudar a priorizar recursos en canales más efectivos.
""")
