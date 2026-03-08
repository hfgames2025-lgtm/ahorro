import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema de Ahorros Colectivo", layout="wide")

# SUSTITUYE ESTE LINK POR EL DE TU HOJA DE GOOGLE (Asegúrate de que termine en /edit?usp=sharing)
URL_EXCEL = "TU_LINK_DE_GOOGLE_SHEETS_AQUI"

# --- CONEXIÓN A BASE DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=URL_EXCEL)
except:
    st.error("Error al conectar con la base de datos. Verifica el link de Google Sheets.")
    st.stop()

# --- LÓGICA DE LOGIN ---
if 'usuario_logueado' not in st.session_state:
    st.session_state.usuario_logueado = None

def login():
    st.title("🔐 Acceso al Tablero")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        # Buscamos si el usuario existe en el Excel
        match = df[(df['usuario'] == user) & (df['password'].astype(str) == pw)]
        if not match.empty:
            st.session_state.usuario_logueado = user
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# --- PANEL PRINCIPAL ---
if st.session_state.usuario_logueado:
    user = st.session_state.usuario_logueado
    
    # Extraer datos del usuario actual
    datos_user = df[df['usuario'] == user].iloc[0]
    ahorro = float(datos_user['ahorro_actual'])
    meta = float(datos_user['meta'])
    
    st.sidebar.write(f"👤 Usuario: **{user}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.rerun()

    # --- VISTA DE ADMINISTRADOR (SOLO PARA TI) ---
    if user == "admin": # Tú serás el usuario 'admin'
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Panel Master")
        with st.sidebar.expander("Crear Nuevo Usuario"):
            nuevo_u = st.text_input("Nombre Nuevo")
            nuevo_p = st.text_input("Pass Nuevo")
            nueva_m = st.number_input("Meta Inicial", value=100000)
            if st.button("Registrar Usuario"):
                # Aquí agregaríamos la lógica para escribir en el Excel
                st.warning("Para guardar cambios permanentes, edita directamente tu Google Sheet por ahora.")

    # --- VISTA DEL TABLERO ---
    st.title(f"¡Hola, {user}! 👋")
    st.subheader(f"Tu meta actual es de ${meta:,}")
    
    # Cuadricula
    valor_cuadro = 100
    total_cuadros = int(meta // valor_cuadro)
    cuadros_pintados = int(ahorro // valor_cuadro)
    
    # Métricas
    c1, c2 = st.columns(2)
    c1.metric("Llevas ahorrado", f"${ahorro:,}")
    c2.progress(min(ahorro/meta, 1.0))

    # Dibujar Cuadritos
    html_grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(10px, 1fr)); gap: 3px;">'
    for i in range(total_cuadros):
        color = "#00e676" if i < cuadros_pintados else "#333"
        html_grid += f'<div style="width:10px; height:10px; background:{color}; border-radius:2px;"></div>'
    html_grid += '</div>'
    st.markdown(html_grid, unsafe_allow_html=True)

else:
    login()