import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Crediabby - Control de Pagos", page_icon="🇻🇪", layout="centered")

# 2. ESTILO VISUAL (CORREGIDO)
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Control Crediabby")
st.info("Herramienta de validación de pagos para evitar registros duplicados.")

# 3. GESTIÓN DE BASE DE DATOS (CSV)
DB_FILE = "base_datos_pagos.csv"

# Cargar datos existentes o crear el archivo si no existe
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["Fecha", "Empleado", "Metodo", "Monto", "Referencia"])

# 4. FORMULARIO DE REGISTRO
with st.container():
    with st.form("formulario_pago"):
        st.subheader("📝 Registrar Nuevo Reporte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            empleado = st.text_input("Nombre del Cobrador", placeholder="Ej: Juan Pérez")
            metodo = st.selectbox("Método de Pago", [
                "Pago Móvil (BS)", 
                "Transferencia Banesco", 
                "Zelle", 
                "Efectivo Divisas ($)", 
                "Banesco Panamá", 
                "Binance (USDT)"
            ])
        
        with col2:
            monto = st.number_input("Monto Recibido", min_value=0.0, step=0.01, format="%.2f")
            referencia = st.text_input("Número de Referencia", help="Ingresa los números del comprobante").strip()
        
        # Botón de acción
        enviado = st.form_submit_button("Validar y Guardar")

# 5. LÓGICA DE VALIDACIÓN
if enviado:
    if not empleado or not referencia or monto <= 0:
        st.warning("⚠️ Debes completar todos los campos y el monto debe ser mayor a 0.")
    else:
        # Convertimos la referencia a texto para comparar sin errores
        ref_buscada = str(referencia)
        
        # Verificar si la referencia ya existe en el archivo
        if ref_buscada in df['Referencia'].astype(str).values:
            # Extraer los datos del registro original para mostrar quién lo hizo
            datos_previos = df[df['Referencia'].astype(str) == ref_buscada].iloc[-1]
            st.error(f"""
                ### ❌ ¡REFERENCIA DUPLICADA!
                Este pago ya fue registrado anteriormente.
                * **Reportado por:** {datos_previos['Empleado']}
                * **Fecha del registro:** {datos_previos['Fecha']}
                * **Monto reportado:** {datos_previos['Monto']}
            """)
        else:
            # Si es nuevo, lo guardamos
            nueva_entrada = {
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Empleado": empleado,
                "Metodo": metodo,
                "Monto": monto,
                "Referencia": ref_buscada
            }
            
            # Actualizar DataFrame y guardar en CSV
            df = pd.concat([df, pd.DataFrame([nueva_entrada])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            
            st.success(f"✅ ¡Éxito! Pago de {monto} con referencia {referencia} guardado correctamente.")

# 6. VISTA PARA TU ESPOSA (ADMIN)
st.divider()
with st.expander("📊 Ver Historial de Pagos (Administración)"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
        
        # Botón para descargar a Excel
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Completo (CSV)",
            data=csv_data,
            file_name=f'reporte_crediabby_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.write("Aún no hay pagos registrados hoy.")