import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Tablero de Ahorro Colectivo", layout="wide")

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
        width: 100%; border-radius: 20px;
        background: linear-gradient(45deg, #00c853, #b2ff59);
        color: black; font-weight: bold; border: none;
    }
    .cuadro-lleno { background: #00e676; box-shadow: 0 0 8px #00e676; border-radius: 2px; }
    .cuadro-vacio { background: #262730; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "datos_ahorro.csv"
LOG_FILE = "historial_ahorros.csv"

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

def registrar_log(user, accion, monto):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_log = pd.DataFrame([{"fecha": ahora, "usuario": user, "accion": accion, "monto": monto}])
    if not os.path.exists(LOG_FILE):
        nuevo_log.to_csv(LOG_FILE, index=False)
    else:
        nuevo_log.to_csv(LOG_FILE, mode='a', header=False, index=False)

def guardar_datos(df): df.to_csv(DB_FILE, index=False)

if 'user' not in st.session_state: st.session_state.user = None

# --- ACCESO ---
if st.session_state.user is None:
    st.title("🏦 Sistema de Ahorro Grupal")
    opcion = st.radio("Acción:", ["Entrar", "Crear Cuenta", "Recuperar Clave"], horizontal=True)
    df = cargar_datos()
    
    if opcion == "Entrar":
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INGRESAR"):
            match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
            if not match.empty:
                st.session_state.user = u
                st.rerun()
            else: st.error("Error en credenciales")

    elif opcion == "Crear Cuenta":
        new_u = st.text_input("Usuario")
        new_p = st.text_input("Clave", type="password")
        new_m = st.number_input("Meta ($)", min_value=1000, value=100000)
        if st.button("REGISTRAR"):
            if new_u in df['usuario'].values: st.warning("Ya existe.")
            else:
                df = pd.concat([df, pd.DataFrame([{"usuario": new_u, "password": new_p, "ahorro": 0.0, "meta": new_m}])], ignore_index=True)
                guardar_datos(df)
                registrar_log(new_u, "Creación de cuenta", 0)
                st.success("¡Cuenta lista!")

    elif opcion == "Recuperar Clave":
        rec_u = st.text_input("Usuario")
        rec_p = st.text_input("Nueva Clave", type="password")
        if st.button("RESETEAR"):
            if rec_u in df['usuario'].values:
                df.loc[df['usuario'] == rec_u, 'password'] = rec_p
                guardar_datos(df)
                registrar_log(rec_u, "Reset de clave", 0)
                st.success("Clave cambiada.")
            else: st.error("Usuario no encontrado.")

# --- APP PRINCIPAL ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    
    # --- VISTA ADMIN ---
    if usuario == "admin":
        st.title("👑 Panel Maestro")
        t1, t2, t3, t4 = st.tabs(["📊 Global", "👥 Usuarios", "📝 Historial", "💰 Mi Ahorro"])
        
        with t1:
            total_ahorrado = df['ahorro'].sum()
            total_metas = df['meta'].sum()
            st.subheader("Progreso Colectivo")
            c1, c2 = st.columns(2)
            c1.metric("Total entre todos", f"${total_ahorrado:,.0f}")
            c2.metric("Meta Grupal", f"${total_metas:,.0f}")
            st.progress(min(total_ahorrado/total_metas, 1.0))
            

        with t2:
            st.dataframe(df, use_container_width=True)
            u_mod = st.selectbox("Gestionar usuario:", df['usuario'].tolist())
            if st.button("Eliminar Usuario") and u_mod != "admin":
                df = df[df['usuario'] != u_mod]
                guardar_datos(df)
                st.rerun()

        with t3:
            if os.path.exists(LOG_FILE):
                log_df = pd.read_csv(LOG_FILE)
                st.table(log_df.tail(15)) # Muestra los últimos 15 movimientos
            else: st.write("Aún no hay movimientos registrados.")

        with t4:
            idx = df[df['usuario'] == "admin"].index[0]
            ahorro = float(df.at[idx, 'ahorro'])
            m = st.number_input("Sumar aporte personal:", min_value=0)
            if st.button("Guardar"):
                df.at[idx, 'ahorro'] = ahorro + m
                guardar_datos(df)
                registrar_log("admin", "Aporte", m)
                st.rerun()

    # --- VISTA USUARIO NORMAL ---
    else:
        idx = df[df['usuario'] == usuario].index[0]
        ahorro = float(df.at[idx, 'ahorro'])
        meta = float(df.at[idx, 'meta'])
        
        st.title(f"🎮 Panel de {usuario}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Llevas", f"${ahorro:,.0f}")
        c2.metric("Tu Meta", f"${meta:,.0f}")
        c3.metric("Te faltan", f"${max(0, meta-ahorro):,.0f}")

        m = st.number_input("¿Cuánto sumas hoy?", min_value=0)
        if st.button("CONFIRMAR APORTE"):
            df.at[idx, 'ahorro'] = ahorro + m
            guardar_datos(df)
            registrar_log(usuario, "Aporte", m)
            st.balloons()
            st.rerun()

        # Cuadrícula Visual
        st.markdown("---")
        total_c = int(meta // 100)
        pint_c = int(ahorro // 100)
        grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(10px, 1fr)); gap: 4px;">'
        for i in range(total_c):
            clase = "cuadro-lleno" if i < pint_c else "cuadro-vacio"
            grid += f'<div class="{clase}" style="width:10px; height:10px;"></div>'
        grid += '</div>'
        st.markdown(grid, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()
