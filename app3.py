import streamlit as st
import pandas as pd
import os

# Configuración
st.set_page_config(page_title="Mi Ahorro", layout="centered")

DB_FILE = "datos_ahorro.csv"

if not os.path.exists(DB_FILE):
    df_inicial = pd.DataFrame([
        {"usuario": "admin", "password": "123", "ahorro": 0.0, "meta": 1000000.0},
      {"usuario": "hfaggi", "password": "6dejulio", "ahorro": 0.0, "meta": 100000.0},
        {"usuario": "joan", "password": "Aa123456", "ahorro": 0.0, "meta": 100000.0}
        {"usuario": "juan", "password": "456", "ahorro": 0.0, "meta": 500000.0}
    ])
    df_inicial.to_csv(DB_FILE, index=False)

def cargar_datos():
    return pd.read_csv(DB_FILE)

def guardar_datos(df):
    df.to_csv(DB_FILE, index=False)

if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("💰 Mi Tablero de Ahorro")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        df = cargar_datos()
        user_match = df[(df['usuario'] == u) & (df['password'].astype(str) == p)]
        if not user_match.empty:
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
else:
    usuario = st.session_state.user
    df = cargar_datos()
    idx = df[df['usuario'] == usuario].index[0]
    
    # Aseguramos que los valores sean flotantes para cálculos exactos
    ahorro_actual = float(df.at[idx, 'ahorro'])
    meta = float(df.at[idx, 'meta'])

    st.title(f"Hola, {usuario} 👋")
    
    # Métricas
    c1, c2 = st.columns(2)
    c1.metric("Llevas ahorrado", f"${ahorro_actual:,.0f}")
    c2.metric("Tu meta", f"${meta:,.0f}")

    # --- SECCIÓN PARA SUMAR O CORREGIR ---
    tab1, tab2 = st.tabs(["➕ Sumar Ahorro", "✏️ Corregir Error"])
    
    with tab1:
        monto = st.number_input("¿Cuánto sumas hoy?", min_value=0, step=100, key="sumar")
        if st.button("Confirmar Aporte"):
            df.at[idx, 'ahorro'] = ahorro_actual + monto
            guardar_datos(df)
            st.success(f"¡Sumados ${monto} correctamente!")
            st.rerun()

    with tab2:
        st.warning("Usa esto si te equivocaste en un número.")
        nuevo_total = st.number_input("Escribe el total real de tu ahorro:", min_value=0.0, value=ahorro_actual, key="corregir")
        if st.button("Sobrescribir Total"):
            df.at[idx, 'ahorro'] = nuevo_total
            guardar_datos(df)
            st.success("¡Total corregido!")
            st.rerun()

    # --- TABLERO DE CUADROS (Lógica corregida) ---
    st.markdown("---")
    valor_por_cuadro = 100 
    
    # Calculamos cuántos cuadros deben existir en total
    total_cuadros_meta = int(meta // valor_por_cuadro)
    
    # Calculamos cuántos cuadros deben estar pintados (Usamos división entera exacta)
    cuadros_a_pintar = int(ahorro_actual // valor_por_cuadro)
    
    st.subheader(f"Progreso Visual: {cuadros_a_pintar} / {total_cuadros_meta} cuadros")
    
    # Dibujar la cuadrícula
    grid = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(12px, 1fr)); gap: 4px;">'
    for i in range(total_cuadros_meta):
        # El cuadro se pinta solo si su índice es menor a los cuadros ganados
        color = "#00e676" if i < cuadros_a_pintar else "#333"
        grid += f'<div style="background:{color}; width:12px; height:12px; border-radius:2px;"></div>'
    grid += '</div>'
    st.markdown(grid, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()
