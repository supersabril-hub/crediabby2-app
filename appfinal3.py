import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz
import base64 # Librería para incrustar el logo de forma segura

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión de Cobranza Crediabby", page_icon="🇻🇪", layout="centered")

# Definir la zona horaria de Venezuela
zona_ve = pytz.timezone('America/Caracas')

# Función para convertir la imagen del logo en formato base64 (para incrustar en HTML)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. GESTIÓN DE SESIÓN
if 'nombre_cobrador' not in st.session_state:
    st.session_state.nombre_cobrador = "Seleccione su nombre"

# 3. ESTILO VISUAL Y LOGO
# Ruta local del logo que subiste a GitHub
LOGO_PATH = "logo.png"

# Intentamos cargar el logo si existe
try:
    if os.path.exists(LOGO_PATH):
        logo_base64 = get_base64_of_bin_file(LOGO_PATH)
        st.markdown(
            f"""
            <style>
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 20px;
            }}
            .main {{ background-color: #f0f2f6; }}
            .stButton>button {{
                width: 100%;
                border-radius: 8px;
                height: 3em;
                background-color: #004a99; /* Azul Crediabby */
                color: white;
                font-weight: bold;
            }}
            </style>
            <div class="container">
                <img src="data:image/png;base64,{logo_base64}" width="200">
                <h1 style='color: #004a99; text-align: center; margin-top: 10px;'>Gestión de Cobranza</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Si no hay logo, mostramos el título normal
        st.title("🛡️ Gestión de Cobranza Crediabby")
except Exception as e:
    # Manejo de error si algo sale mal con la carga del logo
    st.title("🛡️ Gestión de Cobranza Crediabby")

st.markdown("---")

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

# 5. FORMULARIO ÁGIL
with st.form("form_credabby", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        lista_cobradores = ["Seleccione su nombre", "Anthony", "Gabriela", "Emely", "Ninoska"]
        indice_previo = 0
        if st.session_state.nombre_cobrador in lista_cobradores:
            indice_previo = lista_cobradores.index(st.session_state.nombre_cobrador)
        empleado = st.selectbox("Nombre del Cobrador", lista_cobradores, index=indice_previo)
    with col_b:
        cliente = st.text_input("Nombre del Cliente")

    col1, col2 = st.columns(2)
    with col1:
        banco_destino = st.selectbox("Banco / Sucursal de Destino", [
            "BNC Personal", 
            "BNC Jurídica", 
            "Venezuela Jurídica",
            "Ciudad Varyna",
            "Don Samuel",
            "Dominga Ortiz"
        ])
        metodo = st.selectbox("Método de Pago", [
            "Pago Móvil (BS)", 
            "Transferencia", 
            "Zelle", 
            "Efectivo ($)", 
            "Banesco Panamá", 
            "Binance (USDT)"
        ])
    
    with col2:
        monto = st.number_input("Monto Recibido ($)", min_value=0.0, format="%.2f")
        fecha_pago = st.date_input("Fecha en que el cliente pagó", datetime.now(zona_ve))
        referencia = st.text_input("Referencia (6 dígitos)").strip()
    
    boton_enviar = st.form_submit_button("Validar y Registrar Pago")

# 6. LÓGICA DE PROCESAMIENTO
if boton_enviar:
    st.session_state.nombre_cobrador = empleado
    
    es_efectivo = (metodo == "Efectivo ($)")
    
    if empleado == "Seleccione su nombre":
        st.warning("⚠️ Selecciona tu nombre de la lista.")
    elif not cliente or monto <= 0:
        st.warning("⚠️ Completa los datos del cliente y el monto.")
    elif not es_efectivo and (len(referencia) != 6 or not referencia.isdigit()):
        st.error("❌ ERROR: Para este método la referencia debe tener 6 números.")
    else:
        ref_final = referencia if referencia else "-"
        
        duplicado = False
        if ref_final != "-":
            if ref_final in df['Referencia'].astype(str).values:
                duplicado = True
        
        if duplicado:
            pago_existente = df[df['Referencia'].astype(str) == ref_final].iloc[-1]
            st.error(f"❌ ¡PAGO DUPLICADO! Registrado por {pago_existente['Cobrador']} el {pago_existente['Fecha Reporte']}")
        else:
            ahora_ve = datetime.now(zona_ve).strftime("%d/%m/%Y %H:%M:%S")
            nueva_entrada = {
                "Fecha Reporte": ahora_ve,
                "Cobrador": empleado,
                "Cliente": cliente,
                "Fecha Pago": fecha_pago.strftime("%d/%m/%Y"),
                "Banco Destino": banco_destino,
                "Metodo": metodo,
                "Monto": monto,
                "Referencia": ref_final
            }
            
            df = pd.concat([df, pd.DataFrame([nueva_entrada])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, sep=';', encoding='utf-8-sig')
            
            st.success(f"✅ Pago de **{cliente}** registrado con éxito.")
            st.rerun()

# 7. PANEL DE CONTROL
st.markdown("---")
with st.expander("📊 Ver Historial de Pagos"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha Reporte", ascending=False), use_container_width=True)
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        nombre_archivo = f'reporte_crediabby_{datetime.now(zona_ve).strftime("%Y%m%d")}.csv'
        st.download_button(label="📥 Descargar para Excel", data=csv_data, file_name=nombre_archivo, mime='text/csv')