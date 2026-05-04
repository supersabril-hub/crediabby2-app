import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Crediabby - Control Maestro", page_icon="🇻🇪", layout="centered")

# 2. ESTILO VISUAL
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

# 3. GESTIÓN DE BASE DE DATOS (Versión ultra-resistente)
DB_FILE = "base_datos_pagos.csv"
COLUMNAS_OBJETIVO = [
    "Fecha Reporte", "Cobrador", "Cliente", "Fecha Pago", 
    "Banco Destino", "Metodo", "Monto", "Referencia"
]

if os.path.exists(DB_FILE):
    try:
        df = pd.read_csv(DB_FILE, sep=';', encoding='utf-8-sig')
        # Si la estructura no coincide, reiniciamos para evitar errores
        if not all(col in df.columns for col in COLUMNAS_OBJETIVO):
             df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)
    except:
        df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)
else:
    df = pd.DataFrame(columns=COLUMNAS_OBJETIVO)

# 4. FORMULARIO CON REGLA DE 6 DÍGITOS
with st.form("formulario_pago"):
    st.subheader("📝 Nuevo Reporte de Pago")
    
    col_a, col_b = st.columns(2)
    with col_a:
        empleado = st.text_input("Nombre del Cobrador")
    with col_b:
        cliente = st.text_input("Nombre del Cliente")

    col1, col2 = st.columns(2)
    with col1:
        banco_destino = st.selectbox("Banco donde pagó", ["BNC Personal", "BNC Jurídica", "Venezuela Jurídica"])
        metodo = st.selectbox("Método de Pago", ["Pago Móvil (BS)", "Transferencia", "Zelle", "Efectivo ($)", "Binance"])
    
    with col2:
        monto = st.number_input("Monto Recibido", min_value=0.0, format="%.2f")
        fecha_pago = st.date_input("Fecha en que el cliente pagó", datetime.now())
        # Nueva instrucción para la referencia
        referencia = st.text_input("Referencia (ÚLTIMOS 6 DÍGITOS)", help="Ingresa solo los últimos 6 números del comprobante").strip()
    
    enviado = st.form_submit_button("Validar y Registrar Pago")

# 5. LÓGICA DE VALIDACIÓN MEJORADA
if enviado:
    # REGLA: Validar que la referencia tenga exactamente 6 dígitos
    if len(referencia) != 6 or not referencia.isdigit():
        st.error("❌ ERROR: La referencia debe tener exactamente 6 números. Ni más, ni menos.")
    elif not empleado or not cliente or monto <= 0:
        st.warning("⚠️ Completa todos los campos obligatorios.")
    else:
        ref_buscada = str(referencia)
        
        if ref_buscada in df['Referencia'].astype(str).values:
            datos_previos = df[df['Referencia'].astype(str) == ref_buscada].iloc[-1]
            st.error(f"""
                ### ❌ ¡PAGO DUPLICADO DETECTADO!
                Esta referencia de 6 dígitos ya existe.
                * **Cliente:** {datos_previos['Cliente']}
                * **Reportado por:** {datos_previos['Cobrador']}
            """)
        else:
            nueva_entrada = {
                "Fecha Reporte": datetime.now().strftime("%d/%m/%Y %H:%M"),
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
            st.success(f"✅ Pago de {cliente} registrado correctamente.")

# 6. PANEL DE CONTROL
st.markdown("---")
with st.expander("📊 Ver Historial de Pagos"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha Reporte", ascending=False), use_container_width=True)
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(label="📥 Descargar para Excel", data=csv_data, file_name='reporte_crediabby.csv', mime='text/csv')