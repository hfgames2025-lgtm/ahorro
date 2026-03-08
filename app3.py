import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la App
st.set_page_config(page_title="Mi App de Ahorros", layout="wide")

# Conectamos con el motor de Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 obliga a la app a leer datos frescos del Excel cada vez
    return conn.read(ttl=0)

if 'user' not in st.session_state:
    st.session_state.user = None

# --- LOGIN ---
if st.session_state.user is None:
    st.title("🔐 Acceso")
    u = st.text_input("Usuario").strip()
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        df = cargar_datos()
        check = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
        if not check.empty:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")

# --- TABLERO ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    
    # Buscamos los datos de este usuario específico
    try:
        datos = df[df['usuario'] == usuario].iloc[0]
        ahorro = float(datos['ahorro_actual'])
        meta = float(datos['meta'])
    except:
        st.error("Error al leer tus datos. Revisa las columnas del Excel.")
        st.stop()

    st.title(f"👋 ¡Hola, {usuario}!")
    
    # Métricas
    c1, c2 = st.columns(2)
    c1.metric("Ahorrado", f"${ahorro:,.0f}")
    c2.metric("Meta", f"${meta:,.0f}")
    
    st.progress(min(ahorro/meta, 1.0))

    # --- GUARDAR NUEVO AHORRO ---
    st.markdown("---")
    with st.expander("💰 Añadir dinero"):
        monto = st.number_input("Monto a sumar:", min_value=0, step=100)
        if st.button("Confirmar y Guardar"):
            # Calculamos y actualizamos localmente
            nuevo_total = ahorro + monto
            df.loc[df['usuario'] == usuario, 'ahorro_actual'] = nuevo_total
            
            # GUARDAR EN GOOGLE SHEETS (La parte crítica)
            try:
                conn.update(data=df)
                st.success(f"¡Guardado con éxito! Total: ${nuevo_total:,.0f}")
                st.rerun()
            except Exception as e:
                st.error(f"Error de permisos: Asegúrate de que el Excel esté en modo 'Editor'.")

    # --- CUADRICULA ---
    st.subheader("Tu progreso visual")
    valor_cuadro = 100 
    total_cuadros = int(meta // valor_cuadro)
    pintados = int(ahorro // valor_cuadro)
    
    grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 4px;">'
    for i in range(total_cuadros):
        color = "#00e676" if i < pintados else "#333"
        grid_html += f'<div style="background:{color}; width:12px; height:12px; border-radius:2px;"></div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()
