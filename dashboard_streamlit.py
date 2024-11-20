import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

try:
    import statsmodels.api as sm
except ModuleNotFoundError:
    st.error("La librería 'statsmodels' no está instalada. Por favor, instala las dependencias listadas en 'requirements.txt'.")
    st.stop()

# Configuración de la página
st.set_page_config(page_title="Dashboard Avanzado de Oportunidades de Venta", layout="wide")

# Cargar los datos
try:
    df = pd.read_csv('marketing_data_clean.csv')  # Asegúrate de exportar el DataFrame limpio a un archivo CSV.
    st.success("Archivo cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# Clasificación de etapas
etapa_map = {
    "Ganado": 1,
    "SQL En pipe comercial": 1,
    "Transferido a Sales": 1,
    "Nutrición": 0,
    "Descartado (contacto si interés)": 0,
    "Negocio perdido": 0
}
df['Etapa_binaria'] = df['Etapa_del_negocio'].map(etapa_map)

# Validar la variable objetivo
if df['Etapa_binaria'].isnull().any() or not set(df['Etapa_binaria'].unique()).issubset({0, 1}):
    st.error("La variable 'Etapa_binaria' contiene valores fuera del intervalo [0, 1]. Revise los datos.")
    st.stop()

# Listar columnas relevantes para análisis
unidad_columns = [col for col in df.columns if col.startswith('Unidad_de_negocio_asignada')]
fuente_columns = [col for col in df.columns if col.startswith('Fuente_original')]

if not unidad_columns or not fuente_columns:
    st.error("No se encontraron columnas relacionadas con unidades de negocio o fuentes originales en el archivo.")
    st.stop()

# Dashboards Interactivos
st.title("Dashboards Interactivos de Oportunidades de Venta")

# Distribución de leads por fuente y etapa
st.header("Distribución de Leads por Fuente y Etapa")
fuente_etapa_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Fuente_original:N', title="Fuente Original"),
    y=alt.Y('count():Q', title="Cantidad de Leads"),
    color=alt.Color('Etapa_del_negocio:N', title="Etapa del Negocio"),
    tooltip=['Fuente_original', 'Etapa_del_negocio', 'count()']
).properties(width=800, height=400)
st.altair_chart(fuente_etapa_chart, use_container_width=True)

# Conversión por unidad de negocio
st.header("Tasa de Conversión por Unidad de Negocio")
conversion_data = df.groupby(unidad_columns).agg(
    total_leads=('Etapa_binaria', 'count'),
    conversion_rate=('Etapa_binaria', 'mean')
).reset_index()
conversion_chart = alt.Chart(conversion_data).mark_bar().encode(
    x=alt.X('conversion_rate:Q', title="Tasa de Conversión (%)", scale=alt.Scale(domain=[0, 1])),
    y=alt.Y('Unidad_de_negocio_asignada:N', title="Unidad de Negocio"),
    color=alt.Color('conversion_rate:Q', scale=alt.Scale(scheme='greenblue')),
    tooltip=['Unidad_de_negocio_asignada', 'conversion_rate', 'total_leads']
).properties(width=800, height=400)
st.altair_chart(conversion_chart, use_container_width=True)

# Comparativa de tasas de éxito por fuente
st.header("Comparativa de Tasas de Éxito por Fuente")
success_data = df.groupby(fuente_columns).agg(
    total_leads=('Etapa_binaria', 'count'),
    success_rate=('Etapa_binaria', 'mean')
).reset_index()
success_chart = alt.Chart(success_data).mark_circle(size=200).encode(
    x=alt.X('total_leads:Q', title="Total de Leads"),
    y=alt.Y('success_rate:Q', title="Tasa de Éxito (%)", scale=alt.Scale(domain=[0, 1])),
    color=alt.Color('Fuente_original:N', title="Fuente Original"),
    tooltip=['Fuente_original', 'total_leads', 'success_rate']
).properties(width=800, height=400)
st.altair_chart(success_chart, use_container_width=True)

# Resumen y conclusiones
st.subheader("Resumen y Conclusiones")
st.markdown("""
- **Distribución de leads**: Identifica las fuentes más productivas y las etapas en que se concentran los leads.
- **Tasa de conversión**: Analiza qué unidades de negocio están logrando mejores conversiones.
- **Tasa de éxito por fuente**: Compara el desempeño de las distintas fuentes para priorizar esfuerzos de marketing.
""")



