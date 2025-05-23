# Importamos librerías necesarias
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import math
import os
from dotenv import load_dotenv
from datetime import datetime
import psycopg2

# Configuración de Polars
pl.Config.set_tbl_rows(1000)  # Mostrar hasta 1000 filas
pl.Config.set_tbl_width_chars(500)  # Ajustar ancho para mejor visualización

# Importamos funciones de soporte
from src import funciones_load as fl
from src import funciones_dashboard as fdb

# Cargar variables de entorno
load_dotenv()

# Datos de conexión a la base de datos
conexion = os.getenv("conexion_bbdd")  
# Guardamos los datos en cache para no tener que volver a cargar los datos cada página
@st.cache_data
def obtener_datos():
    # Llamar a la función sin pasar la conexión directamente
    madrid = fdb.obtener_datos(conexion, 2018, 2024, "Madrid")
    return madrid

# Obtener los datos sin cachear la conexión
madrid = obtener_datos()

# Procesar los datos
df_mensual, df_diario, df_anual, estaciones, contaminantes, anios = fdb.separar_datos(madrid)
num_estaciones = len(estaciones)
num_contaminantes = len(contaminantes)
num_anios = len(anios)  # Corregí la variable para evitar confusión con la lista


# Sidebar para navegación
st.sidebar.title("Menú de navegación")
opcion = st.sidebar.radio("Selecciona una página", ["Inicio", "Gráficos por año", "Comparación de estaciones", "Filtros avanzados", "Conclusiones"])
# Página principal
if opcion == "Inicio":
    st.title("Análisis de la contaminación en Madrid")
    # Configuramos la pagina de inicio en 3 secciones
    # Primera sección: Introduccióm
    with st.container():
        st.subheader("🌍 ¿Por qué la contaminación es un problema?")
        st.write("La exposición a contaminantes como contaminantes como PM$_{2.5}$, PM$_{10}$, NO$_{2}$ y ozono " \
                "contribuye a problemas respiratorios, cardiovasculares y otras enfermedades crónicas.")
        st.write("Además del impacto directo en la salud, la calidad del aire influye en la economía, al aumentar los costes de "\
                "tratamientos médicos y las pérdidas de productividad laboral. Además de ocasionar gastos de mantenimiento y "\
                "restauración de edificios y monumentos")
        st.write("Este fenómeno es particularmente crítico en áreas urbanas densamente pobladas, como Madrid, que en 2021"
                "encabezaba la lista de ciudades europeas con mayor mortalidad atribuible a la contaminación.")

    # Segunda sección: Origen de los datos
    with st.container():
        st.subheader("📊 Los datos")
        st.write("Datos horarios de estaciones de calidad del aire desde 2001")
        st.write("API del Ayuntamiento de Madrid.")

    # Tercera sección: Extensión del análisis
    with st.container():
        st.subheader("🔎 Extensión del análisis")
        st.write(f"{num_estaciones} estaciones de medida")
        st.write(f"{num_contaminantes} contaminantes medidos")
        st.write(f"{num_anios} años analizados")
 
# Página de gráficos filtrados por año con Polars y Matplotlib
if opcion == "Gráficos por año":
    st.title("Gráficos de estaciones por año")
    anio_seleccionado = st.selectbox("Selecciona un año", anios)

    df_filtrado = madrid.filter(pl.col("año") == anio_seleccionado)

    # Crear gráfico con Matplotlib
    fig, ax = plt.subplots()
    for estacion in df_filtrado["estacion"].unique():
        datos_estacion = df_filtrado.filter(pl.col("Estación") == estacion)
        ax.plot(datos_estacion["fecha"].to_numpy(), datos_estacion["valor"].to_numpy(), label=estacion)

    ax.set_title(f"Datos de estaciones en {anio_seleccionado}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor")
    ax.legend()
    
    # Mostrar en Streamlit
    st.pyplot(fig)




