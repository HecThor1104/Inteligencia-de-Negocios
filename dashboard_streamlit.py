import streamlit as st
import pandas as pd
import altair as alt
import statsmodels.api as sm
import numpy as np

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
    "Pipe comercial": 1,
    "Transferido a sales": 1,
    "Nutrición": 0,
    "Descartado": 0,
    "Localizando": 0
}
df['Etapa_binaria'] = df['Etapa_del_negocio'].map(etapa_map)

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
    x=alt.X("Etapa_del_negocio:N", title="Etapas"),
    y=alt.Y("count():Q", title="Cantidad"),
    color="Etapa_del_negocio:N"
).properties(width=600, height=400)
st.altair_chart(etapas_chart, use_container_width=True)

st.subheader("Probabilidades de Éxito por Fuente")
probs_fuentes = logit_model.predict(X).groupby(df['Fuente_original']).mean()
fuente_chart = alt.Chart(probs_fuentes.reset_index()).mark_bar().encode(
    x=alt.X("Fuente_original:N", title="Fuente Original"),
    y=alt.Y("probabilidad:Q", title="Probabilidad de Éxito"),
    color="Fuente_original:N"
).properties(width=600, height=400)
st.altair_chart(fuente_chart, use_container_width=True)

# Resumen y conclusiones
st.subheader("Resumen y Conclusiones")
st.markdown("""
- **Probabilidad de éxito (Ganado, Pipe comercial, Transferido a sales)** calculada usando modelos Probit y Logit.
- Las fuentes y unidades de negocio influyen significativamente en el éxito.
- Distribuciones y probabilidades por fuente y unidad disponibles en las visualizaciones.
""")


