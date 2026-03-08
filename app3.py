import streamlit as st
import pandas as pd
import os

# --- ESTILOS VISUALES PRO ---
st.set_page_config(page_title="Tablero de Ahorro PRO", layout="wide")

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

if 'user' not in st.session_state:
    st.session_state.user = None

# --- PANTALLA DE ACCESO ---
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
        new_m = st.number_input("Tu Meta ($)", min_value=1000, value=100000)
        if st.button("REGISTRARME"):
            if new_u in df['usuario'].values: st.warning("El usuario ya existe.")
            else:
                df = pd.concat([df, pd.DataFrame([{"usuario": new_u, "password": new_p, "ahorro": 0.0, "meta": new_m}])], ignore_index=True)
                guardar_datos(df)
                st.success("¡Cuenta creada!")

    elif opcion == "Recuperar Clave":
        rec_u = st.text_input("Usuario")
        rec_p = st.text_input("Nueva Clave", type="password")
        if st.button("RESETEAR"):
            if rec_u in df['usuario'].values:
                df.loc[df['usuario'] == rec_u, 'password'] = rec_p
                guardar_datos(df)
                st.success("Clave actualizada.")
            else: st.error("No existe el usuario.")

# --- APP PRINCIPAL ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    
    # --- PANEL DE ADMINISTRADOR (SOLO PARA ADMIN) ---
    if usuario == "admin":
        st.title("👑 Panel Maestro (Admin)")
        t_admin1, t_admin2, t_admin3 = st.tabs(["👥 Ver Usuarios", "🛠️ Gestionar", "💰 Mi Ahorro"])
        
        with t_admin1:
            st.write("Lista completa de aportes:")
            st.dataframe(df, use_container_width=True)
            total_colectivo = df['ahorro'].sum()
            st.metric("Ahorro Total de todos", f"${total_colectivo:,.0f}")

        with t_admin2:
            st.subheader("Modificar o Borrar")
            user_to_mod = st.selectbox("Selecciona un usuario", df['usuario'].tolist())
            col_a, col_b = st.columns(2)
            with col_a:
                nueva_pass = st.text_input("Nueva clave para este usuario")
                if st.button("Actualizar Clave"):
                    df.loc[df['usuario'] == user_to_mod, 'password'] = nueva_pass
                    guardar_datos(df)
                    st.success(f"Clave de {user_to_mod} cambiada.")
            with col_b:
                if st.button("❌ BORRAR USUARIO"):
                    if user_to_mod != "admin":
                        df = df[df['usuario'] != user_to_mod]
                        guardar_datos(df)
                        st.warning(f"Usuario {user_to_mod} eliminado.")
                        st.rerun()
                    else: st.error("No puedes borrar al admin.")
        
        # El admin también tiene su propio ahorro en la pestaña 3
        with t_admin3:
            idx = df[df['usuario'] == "admin"].index[0]
            # (Aquí va la misma lógica de ahorro que abajo, pero para el admin)
            ahorro = float(df.at[idx, 'ahorro'])
            meta = float(df.at[idx, 'meta'])
            st.metric("Mi Ahorro Personal", f"${ahorro:,.0f}")
            m = st.number_input("Sumar a mi cuenta:", min_value=0)
            if st.button("Guardar Mi Aporte"):
                df.at[idx, 'ahorro'] = ahorro + m
                guardar_datos(df)
                st.rerun()

    # --- PANEL DE USUARIO NORMAL ---
    else:
        idx = df[df['usuario'] == usuario].index[0]
        ahorro = float(df.at[idx, 'ahorro'])
        meta = float(df.at[idx, 'meta'])
        
        st.markdown(f"### 🎮 Tablero de **{usuario}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Ahorrado", f"${ahorro:,.0f}")
        c2.metric("Meta", f"${meta:,.0f}")
        c3.metric("Faltan", f"${max(0, meta-ahorro):,.0f}")

        m = st.number_input("¿Cuánto sumamos?", min_value=0, step=100)
        if st.button("GUARDAR APORTE"):
            df.at[idx, 'ahorro'] = ahorro + m
            guardar_datos(df)
            st.balloons()
            st.rerun()

    # --- CUADRÍCULA (Visible para todos) ---
    if usuario != "admin": # El admin ve sus cuadros en su pestaña o puedes dejarlo general
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
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()
