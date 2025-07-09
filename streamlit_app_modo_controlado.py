import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors

st.set_page_config(page_title="Dashboard CLV y Recomendaciones", layout="wide", page_icon="🧠")
st.title("🧠 Dashboard de Valor del Cliente y Recomendaciones")

# Archivos
archivo_modelo = "csv.csv"
archivo_registro = "registros_clientes.csv"

@st.cache_data
def cargar_modelo():
    return pd.read_csv(archivo_modelo)

df_modelo = cargar_modelo()

# Registro
try:
    registros = pd.read_csv(archivo_registro)
except FileNotFoundError:
    registros = pd.DataFrame(columns=[
        "Edad", "Género", "Descuento aplicado", "Envío pickup",
        "Edad real", "Edad normalizada", "Retiro en tienda",
        "Probabilidad de Alto Valor", "Cliente de Alto Valor",
        "Productos recomendados"
    ])

modo = st.sidebar.radio("Seleccionar modo:", ["📋 Registro", "📊 Visualización"])

def normalizar_edad(edad_real):
    min_edad, max_edad = 18, 70
    return (edad_real - min_edad) / (max_edad - min_edad)

def predecir_cliente(df, edad_norm, genero, descuento, envio):
    columnas = ["Age", "Gender_Male", "Discount Applied_Yes", "Shipping Type_Store Pickup"]
    if not all(col in df.columns for col in columnas):
        raise KeyError(columnas)

    entrada = pd.DataFrame([{
        "Age": edad_norm,
        "Gender_Male": genero == "Masculino",
        "Discount Applied_Yes": descuento,
        "Shipping Type_Store Pickup": envio
    }])

    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(df[columnas])
    _, idx = knn.kneighbors(entrada)
    idx = idx[0][0]

    prob = df.loc[idx, "Probabilidad_CLV_Alto"]
    predicho = df.loc[idx, "CLV_Predicho"]
    return predicho, prob, idx

def obtener_recomendaciones(df, idx):
    productos = [col for col in df.columns if col.startswith("Item Purchased_")]
    comprados = df.loc[idx, productos]
    return comprados[comprados == 1].index.str.replace("Item Purchased_", "").tolist()

# MODO REGISTRO
if modo == "📋 Registro":
    with st.form("form"):
        st.subheader("📝 Formulario de Registro")
        edad_real = st.slider("Edad del cliente (años)", 18, 70, 30)
        genero = st.radio("Género", ["Femenino", "Masculino"])
        descuento = st.checkbox("¿Aplicó descuento?")
        envio = st.checkbox("¿Usó retiro en tienda (pickup)?")
        enviar = st.form_submit_button("✅ Registrar cliente")

    if enviar:
        edad_norm = normalizar_edad(edad_real)

        try:
            predicho, prob, idx = predecir_cliente(df_modelo, edad_norm, genero, descuento, envio)
            productos = obtener_recomendaciones(df_modelo, idx)

            nuevo = {
                "Edad": edad_norm,
                "Género": genero,
                "Descuento aplicado": "Sí" if descuento else "No",
                "Envío pickup": "Sí" if envio else "No",
                "Edad real": edad_real,
                "Edad normalizada": edad_norm,
                "Retiro en tienda": envio,
                "Probabilidad de Alto Valor": round(prob, 4),
                "Cliente de Alto Valor": "Sí" if predicho == 1 else "No",
                "Productos recomendados": ", ".join(productos)
            }

            duplicado = registros[
                (registros["Edad real"] == edad_real) &
                (registros["Género"] == genero) &
                (registros["Descuento aplicado"] == nuevo["Descuento aplicado"]) &
                (registros["Envío pickup"] == nuevo["Envío pickup"])
            ]

            if not duplicado.empty:
                st.warning("⚠️ Cliente ya registrado anteriormente.")
            else:
                registros = pd.concat([registros, pd.DataFrame([nuevo])], ignore_index=True)
                registros.to_csv(archivo_registro, index=False)
                st.success("✅ Cliente registrado.")
                st.markdown("🎯 **Clasificación:** " + ("🟢 Alto Valor" if predicho == 1 else "🔴 Bajo Valor"))
                st.markdown("🎁 **Productos recomendados:** " + ", ".join(productos))

        except KeyError as e:
            st.error(f"❌ Error al clasificar cliente: {e}")

# MODO VISUALIZACIÓN
elif modo == "📊 Visualización":
    st.subheader("📦 Registros guardados")
    if registros.empty:
        st.info("No hay registros disponibles.")
    else:
        # Filtros
        with st.sidebar:
            st.markdown("### 🔍 Filtros")
            filtro_genero = st.multiselect("Género", registros["Género"].unique(), default=registros["Género"].unique())
            filtro_valor = st.multiselect("Alto Valor", registros["Cliente de Alto Valor"].unique(),
                                          default=registros["Cliente de Alto Valor"].unique())
            filtro_descuento = st.multiselect("Descuento", registros["Descuento aplicado"].unique(),
                                              default=registros["Descuento aplicado"].unique())

        filtrado = registros[
            (registros["Género"].isin(filtro_genero)) &
            (registros["Cliente de Alto Valor"].isin(filtro_valor)) &
            (registros["Descuento aplicado"].isin(filtro_descuento))
        ]

        st.dataframe(filtrado.reset_index(drop=True), use_container_width=True)
        st.download_button("⬇️ Descargar CSV", filtrado.to_csv(index=False), file_name="clientes_filtrados.csv")
