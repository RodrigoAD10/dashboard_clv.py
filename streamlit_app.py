import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv('predicciones_finales.csv')

# Título
st.title("🎯 Dashboard CLV Predictivo")

# Filtros laterales
st.sidebar.header("🎛️ Filtros")
age = st.sidebar.slider("Edad (normalizada)", float(df["Age"].min()), float(df["Age"].max()), (float(df["Age"].min()), float(df["Age"].max())))
gender = st.sidebar.multiselect("Género", df["Gender_Male"].unique(), default=df["Gender_Male"].unique())
discount = st.sidebar.multiselect("Descuento aplicado", df["Discount Applied_Yes"].unique(), default=df["Discount Applied_Yes"].unique())
shipping = st.sidebar.multiselect("Tipo de envío pickup", df["Shipping Type_Store Pickup"].unique(), default=df["Shipping Type_Store Pickup"].unique())

# Aplicar filtros
df_filtered = df[
    (df["Age"] >= age[0]) & (df["Age"] <= age[1]) &
    (df["Gender_Male"].isin(gender)) &
    (df["Discount Applied_Yes"].isin(discount)) &
    (df["Shipping Type_Store Pickup"].isin(shipping))
]

# Métricas
col1, col2 = st.columns(2)
col1.metric("Total Clientes", len(df_filtered))
col2.metric("CLV Promedio", f"{df_filtered['Probabilidad_CLV_Alto'].mean():.2f}")

# Gráfico 1: Distribución por género según CLV
fig1 = px.histogram(df_filtered, x="CLV_Predicho", color="Gender_Male", barmode="group", 
                    labels={"CLV_Predicho": "CLV Predicho", "Gender_Male": "Género"},
                    title="Distribución de CLV Predicho por Género")
st.plotly_chart(fig1)

# Gráfico 2: Influencia de descuentos
fig2 = px.histogram(df_filtered, x="CLV_Predicho", color="Discount Applied_Yes", barmode="group",
                    title="Influencia del Descuento en el CLV Predicho")
st.plotly_chart(fig2)

# Gráfico 3: Probabilidad de CLV Alto
fig3 = px.histogram(df_filtered, x="Probabilidad_CLV_Alto", nbins=20, title="Distribución de Probabilidad CLV Alto")
st.plotly_chart(fig3)

# Gráfico 4: Modo de Envío Pickup vs CLV
fig4 = px.histogram(df_filtered, x="CLV_Predicho", color="Shipping Type_Store Pickup", barmode="group",
                    title="Relación entre Pickup y CLV Predicho")
st.plotly_chart(fig4)
