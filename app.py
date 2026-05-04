import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Crediabby - Control Maestro", page_icon="🇻🇪", layout="centered")

# 2. ESTILO VISUAL PROFESIONAL
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
    .stHeader { color: #004a99; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Gestión de Cobranza Crediabby")
st.markdown("---")

# 3. GESTIÓN DE BASE DE DATOS (CSV Excel-Friendly)
DB_FILE = "base_datos_pagos.csv"

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE, sep=';', encoding='utf-8-sig')
else:
    df = pd.DataFrame(columns=[
        "Fecha Reporte", "Cobrador", "Cliente", "Fecha Pago", 
        "Banco Destino", "Metodo", "Monto", "Referencia"
    ])

# 4. FORMULARIO DE REGISTRO DETALLADO
with st.form("formulario_pago"):
    st.subheader("📝 Nuevo Reporte de Pago")
    
    # Fila 1: Datos de quien reporta y el cliente
    col_a, col_b = st.columns(2)
    with col_a:
        empleado = st.text_input("Nombre del Cobrador", placeholder="¿Quién reporta?")
    with col_b:
        cliente = st.text_input("Nombre del Cliente", placeholder="Nombre o Razón Social")

    # Fila 2: Datos bancarios
    col1, col2 = st.columns(2)
    with col1:
        banco_destino = st.selectbox("Banco donde pagó", [
            "BNC Personal", 
            "BNC Jurídica", 
            "Venezuela Jurídica"
        ])
        metodo = st.selectbox("Método de Pago", [
            "Pago Móvil (BS)", 
            "Transferencia (Mismo Banco)", 
            "Transferencia (Otros Bancos)",
            "Zelle", 
            "Efectivo Divisas ($)", 
            "Banesco Panamá", 
            "Binance (USDT)"
        ])
    
    # Fila 3: Monto, Fecha y Referencia
    with col2:
        monto = st.number_input("Monto Recibido", min_value=0.0, format="%.2f")
        fecha_pago = st.date_input("Fecha en que el cliente pagó", datetime.now())
        referencia = st.text_input("Número de Referencia (Comprobante)").strip()
    
    enviado = st.form_submit_button("Validar y Registrar Pago")

# 5. LÓGICA DE VALIDACIÓN ANTI-DUPLICADOS
if enviado:
    if not empleado or not cliente or not referencia or monto <= 0:
        st.warning("⚠️ Por favor, complete todos los campos obligatorios.")
    else:
        ref_buscada = str(referencia)
        
        # Validación de duplicidad
        if ref_buscada in df['Referencia'].astype(str).values:
            datos_previos = df[df['Referencia'].astype(str) == ref_buscada].iloc[-1]
            st.error(f"""
                ### ❌ ¡PAGO YA EXISTENTE!
                Esta referencia ya fue reportada anteriormente.
                * **Cliente:** {datos_previos['Cliente']}
                * **Reportado por:** {datos_previos['Cobrador']}
                * **Monto:** {datos_previos['Monto']}
            """)
        else:
            # Registro de nueva entrada
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
            # Guardamos con punto y coma y codificación especial para que Excel no dañe los acentos
            df.to_csv(DB_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.success(f"✅ Pago de {cliente} por {monto} registrado con éxito.")

# 6. PANEL DE CONTROL PARA TU ESPOSA
st.markdown("---")
with st.expander("📊 Panel de Revisión Administrativa"):
    if not df.empty:
        # Mostramos la tabla ordenada por lo más reciente
        st.dataframe(df.sort_values(by="Fecha Reporte", ascending=False), use_container_width=True)
        
        # Botón de descarga optimizado para Excel
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Base de Datos para Excel",
            data=csv_data,
            file_name=f'reporte_crediabby_{datetime.now().strftime("%d_%m_%Y")}.csv',
            mime='text/csv',
        )
    else:
        st.write("No hay registros en la base de datos actualmente.")