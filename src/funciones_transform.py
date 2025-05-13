# importamos librerías
import pandas as pd
import numpy as np
import os
from unidecode import unidecode

def unir_archivos(carpeta_entrada, patron_nombre, carpeta_salida, nombre_salida):
    """
    Une los archivos de una carpera según el nombre dado y los guarda como un único csv en la carpeta de salida

    Parámetros:
        carpeta_entrada (str): ruta de la carpeta donde se encuentran los archivos que queremos unir.
        patron_nombre (str): patrón de nombre de los archivos a unir
        carpeta_salida (str): ruta de la carpeta donde se guardan los archivos unidos.
        nombre_salida (str): nombre del archivo de salida (sin extensión).

    Retorna:
        archivos: Lista con los nombres de los archivos unidos.
    """
    carpeta = carpeta_entrada
    archivos = [archivo for archivo in os.listdir(carpeta) if patron_nombre.lower() in archivo.lower()]
    df_lista = [pd.read_csv(os.path.join(carpeta, archivo), sep=";", parse_dates = True, encoding="latin1") for archivo in archivos]
    print (archivos)
    df_unido = pd.concat(df_lista, ignore_index=True)
    df_unido.to_parquet(f"{carpeta_salida}/{nombre_salida}.parquet", index=False)
    print(f"archivo {nombre_salida}.csv creado en {carpeta_salida}")
    return df_unido


def combinar_h_v(df):
    """
    Combina pares de columnas que empiezan por 'h' y 'v' en un DataFrame,
    creando nuevas columnas con los valores combinados. Además, devuelve
    una lista de las columnas creadas.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        pd.DataFrame: DataFrame con columnas combinadas añadidas.
        list: Lista de nombres de las columnas creadas.
    """
    columnas_h = [col for col in df.columns if col.startswith('h')]
    columnas_v = [col for col in df.columns if col.startswith('v')]
    
    columnas_creadas = []  # Lista para almacenar nombres de las columnas creadas

    for col_h, col_v in zip(columnas_h, columnas_v):
        nueva_columna = f"{col_h}_{col_v}"  # Nombre de la nueva columna
        df[nueva_columna] = df[col_h].astype(str) + " " + df[col_v].astype(str)
        columnas_creadas.append(nueva_columna)  # Agregar el nombre de la columna a la lista
    
    return df, columnas_creadas

def formato_df(df):
    """
    Formatea un DataFrame con datos de calidad del aire, asegurando un formato homogéneo y estructurado.

    Pasos realizados:
    1. Convierte las columnas "ano", "mes" y "dia" a tipo string.
    2. Rellena los valores de mes y día para que tengan siempre dos dígitos.
    3. Crea una nueva columna "fecha" combinando año, mes y día.
    4. Une las columnas de hora y validación mediante la función `combinar_h_v()`.
    5. Transforma las columnas de hora en filas mediante `pd.melt()`.
    6. Separa la validación del valor y deja únicamente la hora en la columna "hora".
    7. Ajusta el valor "24" en la columna "hora" a "23:59" y añade ":00" en las demás horas.
    8. Crea una columna "fecha_hora_f" en formato datetime.
    9. Extrae el estado de validación de la medida desde la columna "valor".
    10. **Corrige los valores con comas decimales**, reemplazando `,` por `.` en la columna "valor".
    11. Convierte la columna "valor" a tipo float para realizar operaciones numéricas.
    12. Crea un identificador único "id_medida" para cada observación.
    13. Une "provincia", "municipio" y "estacion" en "codigo_estacion" con formato estandarizado.

    Args:
        df : pd.DataFrame
            DataFrame con los datos de calidad del aire.

    Returns:
        pd.DataFrame
            DataFrame formateado con la estructura correcta.
    """
    # Nos aseguramos de que las columnas de fecha sean str
    df[["ano", "mes", "dia"]] = df[["ano", "mes", "dia"]].astype(str)

    # Rellenamos mes y día para que siempre tengan 2 dígitos
    df["mes"] = df["mes"].str.zfill(2)
    df["dia"] = df["dia"].str.zfill(2)

    # Creamos la columna de fecha
    df["fecha"] = df["ano"] + "-" + df["mes"] + "-" + df["dia"]

    # Combinamos las columnas de hora y validación
    df, columnas_creadas = combinar_h_v(df)

    # Transformamos el DataFrame para que las columnas de hora queden en filas
    df = df.melt(
        id_vars=["provincia", "municipio", "estacion", "magnitud", "punto_muestreo", "fecha"],
        value_vars=columnas_creadas,
        var_name="hora",
        value_name="valor"
    )

    # Ahora separamos la letra que acompaña al valor para crear la columna de validación y dejamos solo la hora
    df["hora"] = df["hora"].str.split("_", expand=True)[0].str.extract("(\\d+)")[0]

    # Ajustamos el formato de la hora para casos especiales
    df["hora"] = df["hora"].apply(lambda x: '23:59' if x == '24' else f"{str(x)}:00")

    # Creamos una columna de fecha y hora con formato datetime
    df["fecha_hora_f"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["hora"].astype(str))

    # Extraemos el estado de validación de la medida
    df["validacion"] = df["valor"].str.split(" ", expand=True)[1]
    df["valor"] = df["valor"].str.split(" ", expand=True)[0]

    # **Corrige los valores con comas decimales antes de convertir a float**
    df["valor"] = df["valor"].str.replace(",", ".")  # Reemplaza comas por puntos en decimales

    # Convertimos "valor" a float
    df["valor"] = df["valor"].astype(float)

    # Creamos un id único para cada medida
    df["id_medida"] = df["punto_muestreo"] + "_" + df["fecha"] + "_" + df["hora"] + "_" + df["validacion"]

    # Formamos el código de estación
    df["codigo_estacion"] = df["provincia"].astype(str).str.zfill(2) + \
                            df["municipio"].astype(str).str.zfill(3) + \
                            df["estacion"].astype(str).str.zfill(3)

    return df

def formato_df_madrid(df):
    """
    Formatea el DataFrame de Madrid para que tenga el mismo formato que el de la Comunidad de Madrid.

    Args:
        df (pd.DataFrame): DataFrame original de Madrid.

    Returns:
        pd.DataFrame: DataFrame formateado.
    """
   
    # eliminamos duplicados
    df.drop_duplicates(inplace=True)
    # eliminamos una columna con muchos nulos
    df = df.drop('ï»¿PROVINCIA', axis=1)
    # pasamos todos los encabezdos a minúsculas
    df.columns = df.columns.str.lower()
    # añadimos la columna de provincia al principio
    df.insert(0, "provincia", 28)
    return df

def formato_contaminantes(df):
    """
    Formatea el DataFrame de contaminantes para que tenga el formato adecuado.

    Args:
        df (pd.DataFrame): DataFrame original de contaminantes.

    Returns:
        pd.DataFrame: DataFrame formateado.
    """
    # cambiamos el nombre de las columnas a snake_case y quitamos las tildes
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df.columns = df.columns.map(unidecode)
    return df