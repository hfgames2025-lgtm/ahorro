import streamlit as st
import pandas as pd
import os

# --- ESTILOS VISUALES PRO ---
st.set_page_config(page_title="Tablero de Ahorro Inteligente", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(45deg, #00c853, #b2ff59);
        color: black; font-weight: bold; border: none;
    }
    .cuadro-lleno { background: #00e676; box-shadow: 0 0 8px #00e676; border-radius: 2px; }
    .cuadro-vacio { background: #262730; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "datos_ahorro.csv"

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame([
            {"usuario": "admin", "password": "123", "ahorro": 0.0, "meta": 1000000.0},
            {"usuario": "hugo", "password": "Bb123456", "ahorro": 0.0, "meta": 100000.0},
            {"usuario": "joan", "password": "Aa123456", "ahorro": 0.0, "meta": 100000.0},
            {"usuario": "juan", "password": "456", "ahorro": 0.0, "meta": 500000.0}
        ])
        df.to_csv(DB_FILE, index=False)
        return df
    return pd.read_csv(DB_FILE)

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

# --- LÓGICA DE SESIÓN ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- PANTALLA DE ACCESO / REGISTRO ---
if st.session_state.user is None:
    st.title("🏦 Panel de Ahorros")
    
    opcion = st.radio("¿Qué deseas hacer?", ["Entrar", "Crear Cuenta", "Recuperar Clave"], horizontal=True)
    
    df = cargar_datos()
    
    if opcion == "Entrar":
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INGRESAR"):
            match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
            if not match.empty:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")

    elif opcion == "Crear Cuenta":
        new_u = st.text_input("Nuevo Usuario").strip()
        new_p = st.text_input("Asignar Clave", type="password")
        new_m = st.number_input("Tu Meta de Ahorro ($)", min_value=1000, value=100000, step=1000)
        
        if st.button("REGISTRARME"):
            if new_u in df['usuario'].values:
                st.warning("Ese usuario ya existe. Elige otro.")
            elif new_u == "":
                st.error("El nombre no puede estar vacío.")
            else:
                nueva_fila = pd.DataFrame([{"usuario": new_u, "password": new_p, "ahorro": 0.0, "meta": new_m}])
                df = pd.concat([df, nueva_fila], ignore_index=True)
                guardar_datos(df)
                st.success("¡Cuenta creada! Ahora puedes 'Entrar'.")

    elif opcion == "Recuperar Clave":
        st.info("Escribe tu usuario para pisar la clave anterior con una nueva.")
        rec_u = st.text_input("Usuario a recuperar")
        rec_p = st.text_input("Nueva Clave", type="password")
        
        if st.button("RESETEAR CLAVE"):
            if rec_u in df['usuario'].values:
                df.loc[df['usuario'] == rec_u, 'password'] = rec_p
                guardar_datos(df)
                st.success(f"¡Hecho! La clave de {rec_u} ha sido actualizada.")
            else:
                st.error("Ese usuario no existe en nuestra base.")

# --- APP PRINCIPAL (USUARIO LOGUEADO) ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    idx = df[df['usuario'] == usuario].index[0]
    ahorro = float(df.at[idx, 'ahorro'])
    meta = float(df.at[idx, 'meta'])
    
    st.markdown(f"### 🎮 Tablero de **{usuario}**")
    
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Ahorrado", f"${ahorro:,.0f}")
    c2.metric("Meta", f"${meta:,.0f}")
    c3.metric("Faltan", f"${max(0, meta-ahorro):,.0f}")

    # Acciones dentro de la app
    t1, t2 = st.tabs(["💰 SUMAR", "📊 ESTADO"])
    
    with t1:
        m = st.number_input("¿Cuánto sumamos?", min_value=0, step=100)
        if st.button("GUARDAR APORTE"):
            df.at[idx, 'ahorro'] = ahorro + m
            guardar_datos(df)
            st.balloons()
            st.rerun()

    with t2:
        st.write(f"Progreso: {int((ahorro/meta)*100)}%")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.user = None
            st.rerun()

    # --- CUADRÍCULA VISUAL ---
    st.markdown("---")
    valor_cuadro = 100
    total_cuadros = int(meta // valor_cuadro)
    pintados = int(ahorro // valor_cuadro)
    
    grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 5px;">'
    for i in range(total_cuadros):
        clase = "cuadro-lleno" if i < pintados else "cuadro-vacio"
        grid_html += f'<div class="{clase}" style="width:12px; height:12px;"></div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)
