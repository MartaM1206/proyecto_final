# Para tratamiento de datos
import polars as pl
import math
# Para visualizaciones
import seaborn as sns 
import matplotlib.pyplot as plt
import plotly.express as px
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
    # Inicializamos conexión y cursor
    conn, cur = None, None
    # Intentamos conectar a la base de datos
    try:
        conn, cur = fl.conectar_postgres(conexion)
        
        # Verificar que la conexión es válida antes de continuar
        if conn is None or cur is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        # Query que ejecutamos
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
        # Ejecutar query con los parámetros que entran en la función y obtener los datos
        cur.execute(query, (anio_inicio, anio_fin, zona))
        datos = cur.fetchall()
        
        # Definir nombres de columnas para el df de polars
        column_names = ["estacion", "contaminante", "hora_medida", "valor", "unidad", "id_medida", "tipo_estacion"]
        
        # Convertir resultados en un DataFrame de Polars
        df = pl.DataFrame(datos, schema=column_names, orient="row")
        
        return df
    # si hay error al conectar o en la consulta
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

    # Extraemos df con las medias mensuales
    df_mensual = (
        df.group_by(["estacion", "contaminante", "mes", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_mensual"))
        .sort(["estacion", "contaminante", "año", "mes"])
    )

    # Extraemos df con las medias diarias
    df_diario = (
        df.group_by(["estacion", "contaminante", "fecha"])
        .agg(pl.col("valor").mean().round(2).alias("media_diaria"))
        .sort(["estacion", "contaminante", "fecha"])
    )

    # Extraemos df con las medias anuales
    df_anual = (
        df.group_by(["estacion", "contaminante", "año"])
        .agg(pl.col("valor").mean().round(2).alias("media_anual"))
        .sort(["estacion", "contaminante", "año"])
    )

    # Extraer listas únicas para visualizaciones
    estaciones = df["estacion"].unique().to_list()
    contaminantes = df["contaminante"].unique().to_list()
    anios = df["año"].unique().to_list()
    return df_mensual, df_diario, df_anual, estaciones, contaminantes, anios


def estacion_anio_interactivo(df_mensual, contaminantes, año_seleccionado, estacion_seleccionada):
    """
    Genera un gráfico interactivo de medias mensuales de contaminantes para una estación específica y un año seleccionado.

    Args:
        df_mensual (pl.DataFrame): DataFrame con los datos mensuales.
        contaminantes (list[str]): Lista de contaminantes a graficar.
        año_seleccionado (int): Año a filtrar.
        estacion_seleccionada (str): Estación seleccionada para el análisis.

    Returns:
        plotly.graph_objects.Figure: Gráfico interactivo de evolución de medias mensuales.
    """
    # Filtramos el df por año, estación y contaminantes seleccionados
    df_filtrado = df_mensual.filter(
        (pl.col("año") == año_seleccionado) &
        (pl.col("estacion") == estacion_seleccionada) &
        (pl.col("contaminante").is_in(contaminantes))
    ).sort("mes")

    # Creamos gráfico interactivo con plotly
    fig = px.line(
        df_filtrado, x="mes", y="media_mensual", color="contaminante", markers=True,
        title=f"Medias Mensuales en {estacion_seleccionada} - {año_seleccionado}",
        labels={"media_mensual": "Media Mensual", "mes": "Mes"},
        hover_data={"media_mensual": ":.2f", "mes": True} # Para mostrar la media con 2 decimales y el mes en la etiqueta al pasar el cursor
    )

    # Rotamos las etiquetas del eje x
    fig.update_layout(xaxis_tickangle=-45)

    return fig


def evolucion_anual_interactivo(df_anual, contaminantes, estacion):
    """
    Genera un gráfico interactivo de líneas que representa la evolución de las medias anuales
    de los contaminantes en una estación específica.

    Args:
        df_anual (pl.DataFrame): DataFrame con medias anuales de contaminantes.
        contaminantes (list[str]): Lista de contaminantes a graficar.
        estacion (str): Nombre de la estación seleccionada.

    Returns:
        plotly.graph_objects.Figure: Gráfico interactivo con la evolución de medias anuales.
    """
    # Filtramos el df por la estación seleccionada y los contaminantes requeridos
    df_estacion = df_anual.filter((pl.col("estacion") == estacion) & (pl.col("contaminante").is_in(contaminantes))).sort("año")

    # Creamo el gráfico interactivo con plotly
    fig = px.line(
        df_estacion, x="año", y="media_anual", color="contaminante", markers=True,
        title=f"Evolución de Medias Anuales - {estacion}",
        labels={"media_anual": "Media Anual", "año": "Año"},
        hover_data={"media_anual": ":.2f", "año": True} # Para mostrar la media con 2 decimales y el año en la etiqueta al pasar el cursor
    )
     # Rotamos las etiquetas del eje x
    fig.update_layout(xaxis_tickangle=-45)
    return fig
        

def evolucion_maximos_interactivo(df_diario, contaminantes, estacion):
    """
    Genera un gráfico interactivo de los valores máximos anuales de cada contaminante en la estación seleccionada.
    
    Args:
        df_diario (pl.DataFrame): DataFrame con datos diarios de contaminación.
        contaminantes (list[str]): Lista de contaminantes a graficar.
        estacion (str): Nombre de la estación seleccionada.

    Returns:
        plotly.graph_objects.Figure: Gráfico interactivo de evolución de máximos anuales.
        pl.DataFrame: DataFrame con las fechas de los máximos.
    """
    # Extraemos el año de la columna 'fecha'
    df_diario = df_diario.with_columns(pl.col("fecha").dt.year().alias("año"))

    # Filtramos por estación y obtenemod los valores máximos por año y contaminante
    df_maximos = df_diario.filter(
        (pl.col("estacion") == estacion) & (pl.col("contaminante").is_in(contaminantes))
    ).group_by(["año", "contaminante"]).agg(
        pl.col("media_diaria").max().alias("maximo_anual"),
        pl.col("fecha").filter(pl.col("media_diaria") == pl.col("media_diaria").max()).first().alias("fecha_maximo")
    ).sort("año")
    # Creamos un gráfico interactivo con plotly
    fig = px.line(df_maximos, x="año", y="maximo_anual", color="contaminante", markers=True,
                hover_data={"fecha_maximo": True, "maximo_anual": ":.2f", "año": True},
                title=f"Máximos Anuales por Contaminante - {estacion}",
                labels={"maximo_anual": "Valor Máximo", "año": "Año", "fecha_maximo": "Fecha del Máximo"})

     # Rotamos las etiquetas del eje x
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def graficar_medias_diarias_interactivo(df_filtrado, contaminantes, estacion_seleccionada, fecha_inicio, fecha_fin):
    """
    Genera un gráfico interactivo de las medias diarias de los contaminantes medidos en una estación específica
    y en un rango de fechas determinado

    Args:
        df_filtrado (pl.DataFrame): DataFrame con los datos filtrados por estación y contaminante.
        contaminante_seleccionado (str): Contaminante a visualizar.
        estacion_seleccionada (str): Nombre de la estación seleccionada.
        fecha_inicio (str): Fecha de inicio del período.
        fecha_fin (str): Fecha de fin del período.

    Returns:
        plotly.graph_objects.Figure: Gráfico interactivo de medias diarias.
    """
    # Crear gráfico interactivo con Plotly
    fig = px.line(
        df_filtrado, x="fecha", y="media_diaria", color= "contaminante", markers=True,
        title=f"Medias diarias en {estacion_seleccionada} ({fecha_inicio} - {fecha_fin})",
        labels={"media_diaria": "Media Diaria", "fecha": "Fecha"},
        hover_data={"media_diaria": ":.2f", "fecha": True}
    )

    # Rotamos las etiquetas del eje x
    fig.update_layout(xaxis_tickangle=-45)
    

    return fig

