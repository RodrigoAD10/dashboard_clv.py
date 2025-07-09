
import streamlit as st
import pandas as pd

# Cargar datos
df = pd.read_csv("predicciones_finales.csv")

# Título
st.title("🎯 Panel de Valor del Cliente Predictivo (Modo Controlado)")

# Filtros
st.sidebar.header("🧩 Filtros")

edad = st.sidebar.slider("Edad (normalizada)", float(df["Age"].min()), float(df["Age"].max()), (float(df["Age"].min()), float(df["Age"].max())))
genero = st.sidebar.multiselect("Género", df["Gender_Male"].unique(), default=df["Gender_Male"].unique())
descuento = st.sidebar.multiselect("Descuento aplicado", df["Discount Applied_Yes"].unique(), default=df["Discount Applied_Yes"].unique())
envio = st.sidebar.multiselect("Tipo de envío pickup", df["Shipping Type_Store Pickup"].unique(), default=df["Shipping Type_Store Pickup"].unique())

# Aplicar filtros
df_filtrado = df[
    (df["Age"] >= edad[0]) & (df["Age"] <= edad[1]) &
    (df["Gender_Male"].isin(genero)) &
    (df["Discount Applied_Yes"].isin(descuento)) &
    (df["Shipping Type_Store Pickup"].isin(envio))
]

# Mostrar métricas básicas
st.metric("👥 Total de clientes filtrados", len(df_filtrado))
st.write("Puedes ajustar los filtros a la izquierda para segmentar a los clientes.")
