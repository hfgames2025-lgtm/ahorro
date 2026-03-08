import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Metas", layout="wide")

# Estilo visual mejorado
st.markdown("""
<style>
    .user-badge { background-color: #1e1e1e; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    .stProgress > div > div > div > div { background-color: #00e676; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Forzamos la limpieza de caché para ver cambios en tiempo real
    return conn.read(ttl=0)

# --- ESTADO DE SESIÓN ---
if 'usuario_logueado' not in st.session_state:
    st.session_state.usuario_logueado = None

# --- PANTALLA DE LOGIN ---
if st.session_state.usuario_logueado is None:
    st.title("🎯 Bienvenid@ a tu Tablero")
    with st.form("login_form"):
        user_input = st.text_input("Nombre de Usuario").strip()
        pass_input = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            df = cargar_datos()
            # Verificamos credenciales
            user_data = df[(df['usuario'] == user_input) & (df['password'].astype(str) == pass_input)]
            
            if not user_data.empty:
                st.session_state.usuario_logueado = user_input
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# --- APP UNA VEZ LOGUEADO ---
else:
    df = cargar_datos()
    usuario_actual = st.session_state.usuario_logueado
    datos_user = df[df['usuario'] == usuario_actual].iloc[0]
    
    # Datos del usuario
    ahorro = float(datos_user['ahorro_actual'])
    meta = float(datos_user['meta'])
    es_admin = (usuario_actual.lower() == "admin")

    # Barra lateral
    with st.sidebar:
        st.markdown(f'<div class="user-badge">👤 Conectado como:<br><b>{usuario_actual}</b></div>', unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_logueado = None
            st.rerun()
        
        st.markdown("---")
        if es_admin:
            st.subheader("🛠️ Panel Master")
            st.info("Como Admin, puedes ver y editar todos los usuarios directamente en el Google Sheet.")

    # Cuerpo principal
    st.title(f"¡Hola de nuevo, {usuario_actual}! 👋")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    porcentaje = min(ahorro / meta, 1.0)
    
    col1.metric("Ahorro Actual", f"${ahorro:,.0f}")
    col2.metric("Meta Objetivo", f"${meta:,.0f}")
    col3.metric("Faltan", f"${(meta - ahorro):,.0f}")

    st.write(f"**Progreso:** {porcentaje*100:.1f}%")
    st.progress(porcentaje)

    # --- TABLERO DE CUADROS ---
    st.markdown("---")
    valor_cuadro = 100 # Puedes cambiar esto o hacerlo dinámico
    total_cuadros = int(meta // valor_cuadro)
    cuadros_pintados = int(ahorro // valor_cuadro)
    
    st.subheader(f"Tu progreso visual ({cuadros_pintados:,} de {total_cuadros:,} cuadros)")
    
    # Generar cuadrícula eficiente
    html_grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 4px;">'
    for i in range(total_cuadros):
        color = "#00e676" if i < cuadros_pintados else "#2d2d2d"
        # Brillo neón para los pintados
        estilo = f'background-color: {color}; width: 12px; height: 12px; border-radius: 2px;'
        if i < cuadros_pintados:
            estilo += "box-shadow: 0 0 5px #00e676;"
        html_grid += f'<div style="{estilo}"></div>'
    html_grid += '</div>'
    
    st.markdown(html_grid, unsafe_allow_html=True)

    # --- BOTÓN PARA SUMAR (Solo para el usuario logueado) ---
    st.markdown("---")
    with st.expander("➕ Añadir nuevo ahorro"):
        monto_nuevo = st.number_input("¿Cuánto vas a sumar hoy?", min_value=0, step=100)
        if st.button("Confirmar Aporte"):
            # Lógica para actualizar Google Sheets
            nuevo_total = ahorro + monto_nuevo
            # Actualizar en el dataframe y subir
            df.loc[df['usuario'] == usuario_actual, 'ahorro_actual'] = nuevo_total
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df)
            st.success(f"¡Genial! Has sumado ${monto_nuevo}. El tablero se actualizará en unos segundos.")
            st.rerun()