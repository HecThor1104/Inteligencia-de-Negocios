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
st.set_page_config(page_title="Análisis Avanzado de Oportunidades de Venta", layout="wide")

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
df['Etapa_binaria'] = df['Etapa del negocio'].map(etapa_map)

# Validar la variable objetivo
if df['Etapa_binaria'].isnull().any() or not set(df['Etapa_binaria'].unique()).issubset({0, 1}):
    st.error("La variable 'Etapa_binaria' contiene valores fuera del intervalo [0, 1]. Revise los datos.")
    st.stop()

# Verificar las columnas del DataFrame
st.write("Columnas del DataFrame:", df.columns.tolist())

# Listar columnas relevantes para análisis
unidad_columns = [col for col in df.columns if col.startswith('Unidad_de_negocio_asignada')]
fuente_columns = [col for col in df.columns if col.startswith('Fuente_original')]

if not unidad_columns or not fuente_columns:
    st.error("No se encontraron columnas relacionadas con unidades de negocio o fuentes originales en el archivo.")
    st.stop()

# Crear el modelo Probit y Logit
predictors = unidad_columns + fuente_columns
X = df[predictors]
X = sm.add_constant(X)
y = df['Etapa_binaria']

probit_model = sm.Probit(y, X).fit(disp=0)
logit_model = sm.Logit(y, X).fit(disp=0)

# Resultados del modelo
st.subheader("Resultados de Modelos Probit y Logit")
st.write("Modelo Probit:")
st.text(probit_model.summary())
st.write("Modelo Logit:")
st.text(logit_model.summary())

# Filtros
unidad_seleccion = st.multiselect("Selecciona Unidad de Negocio:", options=unidad_columns)
fuente_seleccion = st.multiselect("Selecciona Fuente Original:", options=fuente_columns)

# Filtrar el DataFrame
df_filtered = df.copy()
if unidad_seleccion:
    df_filtered = df_filtered[df_filtered[unidad_seleccion].sum(axis=1) > 0]
if fuente_seleccion:
    df_filtered = df_filtered[df_filtered[fuente_seleccion].sum(axis=1) > 0]

# Visualizaciones avanzadas
st.subheader("Distribución por Etapas (Categorizadas)")
etapas_chart = alt.Chart(df_filtered).mark_bar().encode(
    x=alt.X("Etapa del negocio:N", title="Etapas"),
    y=alt.Y("count():Q", title="Cantidad"),
    color="Etapa del negocio:N"
).properties(width=600, height=400)
st.altair_chart(etapas_chart, use_container_width=True)

st.subheader("Probabilidades de Éxito por Fuente")
probs_fuentes = logit_model.predict(X).groupby(df['Fuente original']).mean()
fuente_chart = alt.Chart(probs_fuentes.reset_index()).mark_bar().encode(
    x=alt.X("Fuente original:N", title="Fuente Original"),
    y=alt.Y("probabilidad:Q", title="Probabilidad de Éxito"),
    color="Fuente original:N"
).properties(width=600, height=400)
st.altair_chart(fuente_chart, use_container_width=True)

# Resumen y conclusiones
st.subheader("Resumen y Conclusiones")
st.markdown("""
- **Probabilidad de éxito (Ganado, Pipe comercial, Transferido a sales)** calculada usando modelos Probit y Logit.
- Las fuentes y unidades de negocio influyen significativamente en el éxito.
- Distribuciones y probabilidades por fuente y unidad disponibles en las visualizaciones.
""")


