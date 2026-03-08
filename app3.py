import streamlit as st
import pandas as pd
import os

# Configuración con Estilo CSS Personalizado (El "maquillaje" de la app)
st.set_page_config(page_title="Tablero de Ahorro PRO", layout="centered")

st.markdown("""
<style>
    /* Fondo general oscuro */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Tarjetas de métricas tipo cristal */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Botones con estilo */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(45deg, #00c853, #b2ff59);
        color: black;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #00e676;
    }

    /* Estilo para los cuadros de ahorro */
    .cuadro-lleno {
        background: #00e676;
        box-shadow: 0 0 8px #00e676;
        border-radius: 3px;
    }
    .cuadro-vacio {
        background: #262730;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "datos_ahorro.csv"

# Mantenemos tus datos intactos
if not os.path.exists(DB_FILE):
    df_inicial = pd.DataFrame([
        {"usuario": "admin", "password": "123", "ahorro": 0.0, "meta": 1000000.0},
        {"usuario": "hugo", "password": "Bb123456", "ahorro": 0.0, "meta": 100000.0},
        {"usuario": "joan", "password": "Aa123456", "ahorro": 0.0, "meta": 100000.0},
        {"usuario": "juan", "password": "456", "ahorro": 0.0, "meta": 500000.0}
    ])
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos(): return pd.read_csv(DB_FILE)
def guardar_datos(df): df.to_csv(DB_FILE, index=False)

if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🏦 Ahorro Inteligente")
    with st.container():
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INICIAR SESIÓN"):
            df = cargar_datos()
            user_match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
            if not user_match.empty:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    usuario = st.session_state.user
    df = cargar_datos()
    idx = df[df['usuario'] == usuario].index[0]
    ahorro = float(df.at[idx, 'ahorro'])
    meta = float(df.at[idx, 'meta'])
    
    st.markdown(f"### 🎮 ¡Bienvenido, **{usuario}**!")
    
    # Métricas con estilo visual
    c1, c2, c3 = st.columns(3)
    c1.metric("Ahorrado", f"${ahorro:,.0f}")
    c2.metric("Meta", f"${meta:,.0f}")
    c3.metric("Faltante", f"${max(0, meta-ahorro):,.0f}")

    # Pestañas modernas
    t1, t2 = st.tabs(["💰 SUMAR", "⚙️ AJUSTES"])
    with t1:
        m = st.number_input("¿Cuánto depositas?", min_value=0, step=100)
        if st.button("CARGAR DINERO"):
            df.at[idx, 'ahorro'] = ahorro + m
            guardar_datos(df)
            st.balloons()
            st.rerun()
            
    with t2:
        if st.button("Cerrar Sesión"):
            st.session_state.user = None
            st.rerun()

    # --- EL TABLERO VISUAL (El corazón de la app) ---
    st.markdown("---")
    valor_cuadro = 100
    total_cuadros = int(meta // valor_cuadro)
    pintados = int(ahorro // valor_cuadro)
    
    st.write(f"🚀 **Tu progreso:** {int((ahorro/meta)*100)}%")
    
    # Generar cuadrícula con efectos de brillo
    grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 5px;">'
    for i in range(total_cuadros):
        clase = "cuadro-lleno" if i < pintados else "cuadro-vacio"
        grid_html += f'<div class="{clase}" style="width:12px; height:12px;"></div>'
    grid_html += '</div>'
    
    st.markdown(grid_html, unsafe_allow_html=True)
