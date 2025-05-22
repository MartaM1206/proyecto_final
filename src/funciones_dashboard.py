# Para tratamiento de datos
import polars as pl
import math
# Para visualizaciones
import seaborn as sns 
import matplotlib.pyplot as plt
# Para gestión de fechas
from datetime import datetime
# Para conectar a la base de datos
import psycopg2
# Cargar variables de entorno
import os
from dotenv import load_dotenv
# Configuracion de Polars para mostrar todas las columnas y hasta 25 filas
pl.Config.set_tbl_rows(25)  # Asegura que se muestren hasta 1000 filas
pl.Config.set_tbl_width_chars(500)  # Aumenta el ancho para evitar cortes
# importamos funciones de soporte
from src import funciones_load as fl

def obtener_datos(conexion, anio_inicio, anio_fin, zona):
    """
    Conecta a la base de datos PostgreSQL y ejecuta una consulta SQL para obtener datos 
    de contaminación en la zona especificada dentro del rango de años indicado. Devuelve 
    los resultados en un DataFrame de Polars.

    Args:
        conexion (str): 
            Cadena de conexión a la base de datos PostgreSQL.
        anio_inicio (int): 
            Año inicial del rango de consulta.
        anio_fin (int): 
            Año final del rango de consulta.
        zona (str): 
            Nombre de la zona geográfica para la consulta (ej. "Madrid").

    Returns:
        pl.DataFrame: 
            DataFrame de Polars con las siguientes columnas:
            ['estacion', 'contaminante', 'hora_medida', 'valor', 'unidad', 'id_medida', 'tipo_estacion'].
            Si la conexión falla o hay un error en la consulta, retorna `None`.
    """
    conn, cur = None, None
    
    try:
        conn, cur = fl.conectar_postgres(conexion)
        
        # Verificar que la conexión es válida antes de continuar
        if conn is None or cur is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        
        query = """SELECT estaciones.nombre_estacion AS estacion,
                        contaminantes.descripcion_magnitud AS contaminante,
                        fecha_hora_f AS hora_medida, 
                        valor,
                        contaminantes.unidad AS unidad,
                        id_medida,
                        estaciones.tipo_estacion
                FROM medidas
                JOIN contaminantes ON medidas.magnitud = contaminantes.codigo_magnitud
                JOIN estaciones ON medidas.codigo_estacion = estaciones.codigo_estacion
                JOIN zonas ON estaciones.codigo_zona = zonas.codigo_zona
                WHERE EXTRACT(YEAR FROM fecha_hora_f) BETWEEN %s AND %s
                AND zonas.descripcion = %s"""

        cur.execute(query, (anio_inicio, anio_fin, zona))
        datos = cur.fetchall()
        
        # Definir nombres de columnas
        column_names = ["estacion", "contaminante", "hora_medida", "valor", "unidad", "id_medida", "tipo_estacion"]
        
        # Convertir resultados en un DataFrame de Polars
        df = pl.DataFrame(datos, schema=column_names, orient="row")
        
        return df

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None

    finally:
        # Cerrar cursor y conexión
        cur.close()
        conn.close()


def separar_datos(df):
    """
    Realiza el preprocesamiento de los datos de contaminación en un DataFrame de Polars.
    Convierte la columna "valor" a float, agrega columnas "mes", "año" y "fecha",
    y calcula la media mensual, diaria y anual de los valores.

    Args:
        df : pl.DataFrame
            DataFrame de Polars con datos de contaminación, incluyendo las columnas
            ["estacion", "contaminante", "hora_medida", "valor"].

    Returns:
        tuple (pl.DataFrame, pl.DataFrame, pl.DataFrame, list, list)
            - `df_mensual` (pl.DataFrame): Media mensual por estación y contaminante.
            - `df_diario` (pl.DataFrame): Media diaria por estación y contaminante.
            - `df_anual` (pl.DataFrame): Media anual por estación y contaminante.
            - `estaciones` (list): Lista de estaciones únicas en los datos.
            - `contaminantes` (list): Lista de contaminantes únicos en los datos.
    """

    # Convertimos la columna "valor" a float64
    df = df.with_columns(pl.col("valor").cast(pl.Float64))

    # Extraemos "mes", "año" y "fecha"
    df = df.with_columns([
        pl.col("hora_medida").dt.month().alias("mes"),
        pl.col("hora_medida").dt.year().alias("año"),
        pl.col("hora_medida").dt.date().alias("fecha")
    ])

    # ✅ Media mensual
    df_mensual = (
        df.group_by(["estacion", "contaminante", "mes", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_mensual"))
        .sort(["estacion", "contaminante", "año", "mes"])
    )

    # ✅ Media diaria
    df_diario = (
        df.group_by(["estacion", "contaminante", "fecha"])
        .agg(pl.col("valor").mean().round(2).alias("media_diaria"))
        .sort(["estacion", "contaminante", "fecha"])
    )

    # ✅ Media anual
    df_anual = (
        df.group_by(["estacion", "contaminante", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_anual"))
        .sort(["estacion", "contaminante", "año"])
    )

    # Extraer listas únicas para visualizaciones
    estaciones = df["estacion"].unique().to_list()
    contaminantes = df["contaminante"].unique().to_list()

    return df_mensual, df_diario, df_anual, estaciones, contaminantes