import streamlit as st
import os
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Tablero de Ahorros", page_icon="💰", layout="wide")

# --- LÓGICA DE ARCHIVOS (Ahora usamos JSON para guardar múltiples ajustes) ---
ARCHIVO_CONFIG = "config_ahorros.json"

def cargar_todo():
    defaults = {"ahorro_total": 0, "meta": 1000000, "valor_cuadro": 100}
    if os.path.exists(ARCHIVO_CONFIG):
        with open(ARCHIVO_CONFIG, "r") as f:
            return {**defaults, **json.load(f)}
    return defaults

def guardar_todo(datos):
    with open(ARCHIVO_CONFIG, "w") as f:
        json.dump(datos, f)

# Inicializar datos en la sesión
if 'datos' not in st.session_state:
    st.session_state.datos = cargar_todo()

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(8px, 1fr));
        gap: 4px;
        padding: 10px;
    }
    .cuadro {
        width: 12px; height: 12px;
        background-color: #21262d;
        border-radius: 2px;
    }
    .pintado {
        background-color: #238636;
        box-shadow: 0 0 8px #2ea043;
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Configuración y Aportes) ---
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # Sección para cambiar la Meta
    with st.expander("Ajustar Meta y Valores"):
        nueva_meta = st.number_input("Meta Total ($)", value=st.session_state.datos['meta'], step=1000)
        nuevo_valor_cuadro = st.number_input("Valor por cuadro ($)", value=st.session_state.datos['valor_cuadro'], min_value=1, step=10)
        
        if st.button("Guardar Configuración"):
            st.session_state.datos['meta'] = nueva_meta
            st.session_state.datos['valor_cuadro'] = nuevo_valor_cuadro
            guardar_todo(st.session_state.datos)
            st.success("¡Configuración actualizada!")
            st.rerun()

    st.markdown("---")
    st.title("💵 Aportar")
    monto_aporte = st.number_input("Monto a sumar:", min_value=0, step=100)
    if st.button("Confirmar Aporte"):
        st.session_state.datos['ahorro_total'] += monto_aporte
        guardar_todo(st.session_state.datos)
        st.toast(f"¡Sumaste ${monto_aporte}!")
        st.rerun()

    if st.button("Reiniciar Ahorros a $0"):
        st.session_state.datos['ahorro_total'] = 0
        guardar_todo(st.session_state.datos)
        st.rerun()

# --- CUERPO PRINCIPAL ---
datos = st.session_state.datos
meta = datos['meta']
total = datos['ahorro_total']
valor_c = datos['valor_cuadro']

# Cálculos
total_cuadros = meta // valor_c
cuadros_pintados = min(total // valor_c, total_cuadros)
porcentaje = (total / meta) * 100 if meta > 0 else 0

st.title(f"🎯 Objetivo: ${meta:,}")

# Métricas visuales
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><h3>Ahorrado</h3><h2>${total:,}</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><h3>Progreso</h3><h2>{porcentaje:.1f}%</h2></div>', unsafe_allow_html=True)
with col3:
    faltante = max(meta - total, 0)
    st.markdown(f'<div class="metric-card"><h3>Faltan</h3><h2>${faltante:,}</h2></div>', unsafe_allow_html=True)

st.markdown("---")

# --- DIBUJO DE LA CUADRÍCULA ---
st.subheader(f"Tablero de {total_cuadros:,} cuadros (Cada cuadro = ${valor_c})")

html_grid = '<div class="grid-container">'
for i in range(total_cuadros):
    clase = "cuadro pintado" if i < cuadros_pintados else "cuadro"
    html_grid += f'<div class="{clase}"></div>'
html_grid += '</div>'

st.markdown(html_grid, unsafe_allow_html=True)