import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz # Librería para manejar zonas horarias

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Crediabby - Control Maestro", page_icon="🇻🇪", layout="centered")

# Definir la zona horaria de Venezuela
zona_ve = pytz.timezone('America/Caracas')

# 2. GESTIÓN DE SESIÓN
if 'nombre_cobrador' not in st.session_state:
    st.session_state.nombre_cobrador = ""

# 3. ESTILO VISUAL
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Gestión de Cobranza Crediabby")

# 4. GESTIÓN DE BASE DE DATOS
DB_FILE = "base_datos_pagos.csv"
COLUMNAS_OBJETIVO = ["Fecha Reporte", "Cobrador", "Cliente", "Fecha Pago", "Banco Destino", "Metodo", "Monto", "Referencia"]

if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE, sep=';', encoding='utf-8-sig')
        if not all(col in df.columns for col in COLUMNAS_OBJETIVO):
             df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)
    except:
        df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)
else:
    df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)

# 5. FORMULARIO
with st.form("form_credabby", clear_on_submit=True):
    st.subheader("📝 Nuevo Reporte de Pago")
    
    col_a, col_b = st.columns(2)
    with col_a:
        empleado = st.text_input("Nombre del Cobrador", value=st.session_state.nombre_cobrador)
    with col_b:
        cliente = st.text_input("Nombre del Cliente")

    col1, col2 = st.columns(2)
    with col1:
        banco_destino = st.selectbox("Banco donde pagó", ["BNC Personal", "BNC Jurídica", "Venezuela Jurídica"])
        metodo = st.selectbox("Método de Pago", ["Pago Móvil (BS)", "Transferencia", "Zelle", "Efectivo ($)", "Banesco Panamá", "Binance (USDT)"])
    
    with col2:
        monto = st.number_input("Monto Recibido", min_value=0.0, format="%.2f")
        # Fecha de pago sugerida con la hora de VE
        fecha_pago = st.date_input("Fecha en que el cliente pagó", datetime.now(zona_ve))
        referencia = st.text_input("Referencia (ÚLTIMOS 6 DÍGITOS)").strip()
    
    boton_enviar = st.form_submit_button("Validar y Registrar Pago")

# 6. LÓGICA DE PROCESAMIENTO
if boton_enviar:
    st.session_state.nombre_cobrador = empleado
    
    if len(referencia) != 6 or not referencia.isdigit():
        st.error("❌ ERROR: La referencia debe tener exactamente 6 números.")
    elif not empleado or not cliente or monto <= 0:
        st.warning("⚠️ Completa todos los campos obligatorios.")
    else:
        ref_buscada = str(referencia)
        
        if ref_buscada in df['Referencia'].astype(str).values:
            pago_existente = df[df['Referencia'].astype(str) == ref_buscada].iloc[-1]
            st.error(f"""
                ### ❌ ¡PAGO DUPLICADO DETECTADO!
                * **Reportado por:** {pago_existente['Cobrador']}
                * **Fecha del reporte:** {pago_existente['Fecha Reporte']}
                * **Cliente:** {pago_existente['Cliente']}
                * **Monto:** {pago_existente['Monto']}
            """)
        else:
            # CAPTURAR HORA ACTUAL DE VENEZUELA
            ahora_ve = datetime.now(zona_ve).strftime("%d/%m/%Y %H:%M:%S")
            
            nueva_entrada = {
                "Fecha Reporte": ahora_ve,
                "Cobrador": empleado,
                "Cliente": cliente,
                "Fecha Pago": fecha_pago.strftime("%d/%m/%Y"),
                "Banco Destino": banco_destino,
                "Metodo": metodo,
                "Monto": monto,
                "Referencia": ref_buscada
            }
            
            df = pd.concat([df, pd.DataFrame([nueva_entrada])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, sep=';', encoding='utf-8-sig')
            
            st.success(f"✅ Pago de **{cliente}** registrado con éxito a las {ahora_ve}.")
            st.rerun()

# 7. PANEL DE CONTROL
st.markdown("---")
with st.expander("📊 Ver Historial de Pagos (Hora VZLA)"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha Reporte", ascending=False), use_container_width=True)
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        
        # Nombre del archivo con fecha de Venezuela
        nombre_archivo = f'reporte_crediabby_{datetime.now(zona_ve).strftime("%Y%m%d")}.csv'
        
        st.download_button(label="📥 Descargar Reporte para Excel", data=csv_data, file_name=nombre_archivo, mime='text/csv')
    else:
        st.write("Esperando registros...")