import streamlit as st
import pandas as pd
import os

# Configuración
st.set_page_config(page_title="Mi Ahorro", layout="centered")

# Archivo donde se guardarán los datos (Se queda en el servidor)
DB_FILE = "datos_ahorro.csv"

# Si el archivo no existe, lo creamos con datos iniciales
if not os.path.exists(DB_FILE):
    df_inicial = pd.DataFrame([
        {"usuario": "admin", "password": "123", "ahorro": 0.0, "meta": 1000000.0},
         {"usuario": "hfaggi", "password": "6dejulio", "ahorro": 0.0, "meta": 100000.0},
        {"usuario": "joan", "password": "Aa123456", "ahorro": 0.0, "meta": 100000.0}
    ])
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos():
    return pd.read_csv(DB_FILE)

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

# --- LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("💰 Mi Tablero de Ahorro")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        df = cargar_datos()
        user_match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
        if not user_match.empty:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
else:
    # --- APP PRINCIPAL ---
    usuario = st.session_state.user
    df = cargar_datos()
    
    # Obtener datos del usuario
    idx = df[df['usuario'] == usuario].index[0]
    ahorro = float(df.at[idx, 'ahorro'])
    meta = float(df.at[idx, 'meta'])

    st.title(f"Hola, {usuario} 👋")
    
    # Métricas
    col1, col2 = st.columns(2)
    col1.metric("Llevas", f"${ahorro:,.0f}")
    col2.metric("Meta", f"${meta:,.0f}")

    # Sumar Ahorro
    nuevo = st.number_input("Sumar cantidad:", min_value=0, step=100)
    if st.button("Confirmar Pago"):
        df.at[idx, 'ahorro'] = ahorro + nuevo
        guardar_datos(df)
        st.success("¡Ahorro guardado!")
        st.rerun()

    # Cuadritos
    st.markdown("---")
    valor_cuadro = 100
    total = int(meta // valor_cuadro)
    pintados = int((ahorro + nuevo) // valor_cuadro)
    
    grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(10px, 1fr)); gap: 3px;">'
    for i in range(total):
        color = "#00e676" if i < pintados else "#333"
        grid += f'<div style="background:{color}; width:10px; height:10px; border-radius:2px;"></div>'
    grid += '</div>'
    st.markdown(grid, unsafe_allow_html=True)
    
    if st.sidebar.button("Salir"):
        st.session_state.user = None
        st.rerun()

