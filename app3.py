import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tablero de Ahorro Social", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px; padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        width: 100%; border-radius: 20px;
        background: linear-gradient(45deg, #00c853, #b2ff59);
        color: black; font-weight: bold; border: none;
    }
    .cuadro-lleno { background: #00e676; box-shadow: 0 0 8px #00e676; border-radius: 2px; }
    .cuadro-vacio { background: #262730; border-radius: 2px; }
    .mensaje-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        border-left: 5px solid #00e676;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "datos_ahorro.csv"
LOG_FILE = "historial_ahorros.csv"
MSG_FILE = "mensajes.csv"

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

def gestionar_mensajes(accion, de=None, para=None, texto=None):
    if not os.path.exists(MSG_FILE):
        pd.DataFrame(columns=["fecha", "de", "para", "texto"]).to_csv(MSG_FILE, index=False)
    
    if accion == "enviar":
        ahora = datetime.now().strftime("%d/%m %H:%M")
        nuevo = pd.DataFrame([{"fecha": ahora, "de": de, "para": para, "texto": texto}])
        nuevo.to_csv(MSG_FILE, mode='a', header=False, index=False)
    elif accion == "leer":
        return pd.read_csv(MSG_FILE)

def registrar_log(user, accion, monto):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pd.DataFrame([{"fecha": ahora, "usuario": user, "accion": accion, "monto": monto}]).to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

def guardar_datos(df): df.to_csv(DB_FILE, index=False)

if 'user' not in st.session_state: st.session_state.user = None

# --- ACCESO ---
if st.session_state.user is None:
    st.title("🏦 Ahorro Grupal")
    opcion = st.radio("Acción:", ["Entrar", "Crear Cuenta", "Recuperar"], horizontal=True)
    df = cargar_datos()
    if opcion == "Entrar":
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INGRESAR"):
            match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
            if not match.empty:
                st.session_state.user = u
                st.rerun()
            else: st.error("Credenciales incorrectas")
    elif opcion == "Crear Cuenta":
        new_u = st.text_input("Usuario")
        new_p = st.text_input("Clave", type="password")
        new_m = st.number_input("Meta ($)", min_value=1000, value=100000)
        if st.button("REGISTRAR"):
            if new_u in df['usuario'].values: st.warning("Ya existe.")
            else:
                df = pd.concat([df, pd.DataFrame([{"usuario": new_u, "password": new_p, "ahorro": 0.0, "meta": new_m}])], ignore_index=True)
                guardar_datos(df)
                st.success("¡Cuenta creada!")
    elif opcion == "Recuperar":
        rec_u = st.text_input("Usuario")
        rec_p = st.text_input("Nueva Clave", type="password")
        if st.button("RESETEAR"):
            if rec_u in df['usuario'].values:
                df.loc[df['usuario'] == rec_u, 'password'] = rec_p
                guardar_datos(df)
                st.success("Clave actualizada.")

# --- APP PRINCIPAL ---
else:
    df = cargar_datos()
    usuario = st.session_state.user
    
    if usuario == "admin":
        st.title("👑 Panel Maestro")
        t1, t2, t3, t4, t5 = st.tabs(["📊 Global", "👥 Usuarios", "💬 Mensajería", "📝 Logs", "💰 Mi Ahorro"])
        
        with t1:
            total_ah = df['ahorro'].sum()
            total_me = df['meta'].sum()
            st.metric("Total entre todos", f"${total_ah:,.0f}")
            st.progress(min(total_ah/total_me, 1.0))

        with t2:
            u_sel = st.selectbox("Usuario:", df['usuario'].tolist())
            clv = st.text_input("Nueva clave")
            if st.button("Cambiar Clave"):
                df.loc[df['usuario'] == u_sel, 'password'] = clv
                guardar_datos(df); st.success("OK")
            if st.button("❌ BORRAR") and u_sel != "admin":
                df = df[df['usuario'] != u_sel]
                guardar_datos(df); st.rerun()

        with t3:
            st.subheader("Buzón Maestro")
            m_para = st.selectbox("Enviar a:", ["Todos"] + df['usuario'].tolist())
            m_txt = st.text_area("Mensaje de Admin:")
            if st.button("Enviar"):
                gestionar_mensajes("enviar", de="admin", para=m_para, texto=m_txt)
                st.success("Enviado")
            
            st.markdown("---")
            msgs = gestionar_mensajes("leer")
            if not msgs.empty:
                for _, m in msgs.tail(10).iterrows():
                    st.markdown(f'<div class="mensaje-card"><b>De: {m["de"]} Para: {m["para"]}</b><br>{m["texto"]} <small>({m["fecha"]})</small></div>', unsafe_allow_html=True)

        with t4:
            if os.path.exists(LOG_FILE): st.table(pd.read_csv(LOG_FILE).tail(10))

        with t5:
            idx = df[df['usuario'] == "admin"].index[0]
            st.metric("Mi Ahorro", f"${df.at[idx, 'ahorro']:,.0f}")
            m_a = st.number_input("Sumar:", min_value=0)
            if st.button("Sumar"):
                df.at[idx, 'ahorro'] += m_a
                guardar_datos(df); st.rerun()

    else:
        # VISTA USUARIO
        idx = df[df['usuario'] == usuario].index[0]
        ahorro = float(df.at[idx, 'ahorro'])
        meta = float(df.at[idx, 'meta'])
        
        st.title(f"🎮 {usuario}")
        c1, c2 = st.columns(2)
        c1.metric("Ahorrado", f"${ahorro:,.0f}")
        c2.metric("Meta", f"${meta:,.0f}")

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("💰 Aportar")
            m = st.number_input("Monto:", min_value=0)
            if st.button("GUARDAR"):
                df.at[idx, 'ahorro'] += m
                guardar_datos(df); registrar_log(usuario, "Aporte", m); st.rerun()
        
        with col_r:
            st.subheader("💬 Mensajes")
            m_txt = st.text_input("Escribir a alguien:")
            m_dest = st.selectbox("Para:", ["Todos", "admin"] + [u for u in df['usuario'].tolist() if u != usuario])
            if st.button("Enviar Mensaje"):
                gestionar_mensajes("enviar", de=usuario, para=m_dest, texto=m_txt)
                st.toast("Mensaje enviado!")

        # Muro de mensajes para el usuario
        msgs = gestionar_mensajes("leer")
        if not msgs.empty:
            st.markdown("---")
            st.write("📩 **Tu Muro:**")
            mis_msgs = msgs[(msgs['para'] == usuario) | (msgs['para'] == 'Todos') | (msgs['de'] == usuario)]
            for _, m in mis_msgs.tail(5).iterrows():
                tag = "Yo" if m["de"] == usuario else m["de"]
                st.markdown(f'<div class="mensaje-card"><b>{tag}:</b> {m["texto"]}</div>', unsafe_allow_html=True)

        # Cuadritos
        st.markdown("---")
        total_c = int(meta // 100); pint_c = int(ahorro // 100)
        grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(10px, 1fr)); gap: 4px;">'
        for i in range(total_c):
            clase = "cuadro-lleno" if i < pint_c else "cuadro-vacio"
            grid += f'<div class="{clase}" style="width:10px; height:10px;"></div>'
        grid += '</div>'
        st.markdown(grid, unsafe_allow_html=True)

    if st.sidebar.button("Salir"):
        st.session_state.user = None; st.rerun()
