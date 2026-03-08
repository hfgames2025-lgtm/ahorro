import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración básica
st.set_page_config(page_title="Mi App de Ahorros", layout="wide")

# Conexión con Google Sheets (usa el link de los Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer datos actualizados
def cargar_datos():
    return conn.read(ttl=0)

# Estado de la sesión (Login)
if 'user' not in st.session_state:
    st.session_state.user = None

# --- PANTALLA DE LOGIN ---
if st.session_state.user is None:
    st.title("🚀 Acceso al Tablero")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        df = cargar_datos()
        # Verificamos si existe el usuario y coincide la contraseña
        check = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
        if not check.empty:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Datos incorrectos")

# --- APP PRINCIPAL ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    datos = df[df['usuario'] == usuario].iloc[0]
    
    ahorro = float(datos['ahorro_actual'])
    meta = float(datos['meta'])

    st.title(f"¡Hola, {usuario}!")
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"user": None}))

    # Métricas
    c1, c2 = st.columns(2)
    c1.metric("Llevas ahorrado", f"${ahorro:,.0f}")
    c2.metric("Tu meta", f"${meta:,.0f}")

    # Barra de progreso
    progreso = min(ahorro / meta, 1.0)
    st.progress(progreso)

    # --- BOTÓN PARA SUMAR DINERO ---
    st.subheader("➕ Sumar nuevo ahorro")
    monto = st.number_input("¿Cuánto vas a guardar hoy?", min_value=0, step=100)
    
    if st.button("Guardar Ahorro"):
        # 1. Calculamos el nuevo total
        nuevo_total = ahorro + monto
        # 2. Actualizamos nuestra tabla (DataFrame)
        df.loc[df['usuario'] == usuario, 'ahorro_actual'] = nuevo_total
        # 3. LO GUARDAMOS EN GOOGLE SHEETS
        conn.update(data=df)
        st.success(f"¡Guardado! Ahora tienes ${nuevo_total:,.0f}")
        st.rerun()

    # --- TABLERO DE CUADROS ---
    st.markdown("---")
    valor_cuadro = 100 
    total_cuadros = int(meta // valor_cuadro)
    pintados = int(ahorro // valor_cuadro)
    
    grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 4px;">'
    for i in range(total_cuadros):
        color = "#00e676" if i < pintados else "#333"
        grid += f'<div style="background:{color}; width:12px; height:12px; border-radius:2px;"></div>'
    grid += '</div>'
    st.markdown(grid, unsafe_allow_html=True)
