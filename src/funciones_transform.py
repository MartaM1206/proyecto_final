# importamos librerías
import pandas as pd
import numpy as np
import os


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
    df_unido.to_csv(f"{carpeta_salida}/{nombre_salida}.csv", index=False)
    print(f"archivo {nombre_salida}.csv creado en {carpeta_salida}")


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
    1. Convierte las columnas de año, mes y día a tipo string.
    2. Rellena los valores de mes y día para que tengan siempre dos dígitos.
    3. Crea una nueva columna "fecha" combinando año, mes y día.
    4. Une las columnas de hora y validación mediante la función `combinar_h_v()`.
    5. Transforma las columnas de hora en filas mediante `pd.melt()`.
    6. Separa la validación del valor y deja únicamente la hora en la columna "hora".
    7. Ajusta el valor "24" en la hora a "23:59" y añade ":00" en las demás horas.
    8. Crea una columna "fecha_hora_f" en formato datetime.
    9. Extrae el estado de validación de la medida.
    10. Crea un identificador único "id_medida" para cada observación.

    Args:
        df : pd.DataFrame
        DataFrame con los datos de calidad del aire.

    Returns:
        pd.DataFrame
        DataFrame formateado con la estructura correcta.
    """
    # nos aseguramos de que las columnas de fecha son str
    df[["ano", "mes", "dia"]] = (df[["ano", "mes", "dia"]]).astype(str)
    # rellenamos mes y dia para que siempre tengan 2 dígitos
    df["mes"] = df["mes"].str.zfill(2)
    df["dia"] = df["dia"].str.zfill(2)
    # creamos la columna de fecha
    df["fecha"] = df["ano"] + "-" + df["mes"] + "-" + df["dia"]
    # combinamos las columnas de hora y validacion  
    df, columnas_creadas = combinar_h_v(df)
    # transformamos el df para que las columnas de hora queden en filas
    df = df.melt(
        id_vars = ["provincia", "municipio", "estacion", "magnitud", "punto_muestreo", "fecha"],  # Columnas que no se transforman
        value_vars = columnas_creadas,  # Columnas de horas que queremos transformar
        var_name = "hora",  # Nombre de la nueva columna que contiene las etiquetas de hora
        value_name = "valor"  # Nombre de la nueva columna que contiene los valores de las medidas
        )
    # ahora separamos la letra que acompaña al valor para crear la columna de validación y dejamos solo la hora en la columna hora
    df["hora"] = df["hora"].str.split("_", expand = True)[0].str.extract("(\\d+)")[0]
    # como tenemos un valor 24 para la hora y no lo admite datetime, lo sustituimos por 23:59 y añadimos un :00 en las demás horas
    df["hora"] = df["hora"].apply(lambda x: '23:59' if x == '24' else f"{str(x)}:00")
    # creamos una columna de fecha y hora con formato datetime para poder hacer operaciones con ella
    df["fecha_hora_f"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["hora"].astype(str))
    # obtenemos el estado de validación de la medida a partir de la columna de valor
    df["validacion"] = df["valor"].str.split(" ", expand = True)[1]
    df["valor"] = df["valor"].str.split(" ", expand = True)[0]
    #creamos un id de la medida único para cada fila (estacion, contaminante, fecha y hora)
    df["id_medida"] = df["punto_muestreo"] + "_" + df["fecha"] + "_" + df["hora"] + "_" + df["validacion"]
    
    return df