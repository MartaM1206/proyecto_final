# Para tratamiento de datos

import pandas as pd




## definimos una función que nos genere un reporte
def reporte(df):
    """Genera un reporte de valores nulos, porcentaje de nulos y tipo de dato
    para cada columna de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame para el cual se generará el reporte.

    Returns:
        pd.DataFrame: Un DataFrame que contiene el reporte. Las columnas son:
            - index: Nombre de la columna original del DataFrame de entrada.
            - valores_nulos: Cantidad de valores nulos en la columna.
            - porcentaje_nulos: Porcentaje de valores nulos en la columna.
            - tipo_dato: Tipo de dato de la columna.
    """
    
    df_reporte = pd.DataFrame()
    df_reporte["valores_nulos"] = df.isnull().sum()
    df_reporte["porcentaje_nulos"] = round(((df.isnull().sum())/df.shape[0])*100,2)
    df_reporte["tipo_dato"]=df.dtypes
    df_reporte = df_reporte.reset_index(drop=False)
    return df_reporte

def reemplazar(df, columnas, viejo, nuevo):
    """
    Reemplaza todas las ocurrencias de un valor viejo por un nuevo valor en las columnas especificadas de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se realizará el reemplazo.
        viejo (str): El valor que se desea reemplazar.
        nuevo (str): El nuevo valor que reemplazará al valor viejo.

    Returns:
        pd.DataFrame: El DataFrame con los valores reemplazados.
    """
    for columna in columnas:
        df[columna] = df[columna].str.replace(viejo, nuevo)
    return df


def espacios(df, columnas):
    """
    Elimina los espacios en blanco al inicio y al final de los valores en las columnas especificadas de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se eliminarán los espacios en blanco.

    Returns:
        pd.DataFrame: El DataFrame con los valores ajustados.
    """
    for columna in columnas:
        df[columna] = df[columna].str.strip()
    return df


def minus(df, columnas):
    """
    Convierte todos los valores de las columnas especificadas de un DataFrame a minúsculas.

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se convertirán los valores a minúsculas.

    Returns:
        pd.DataFrame: El DataFrame con los valores en minúsculas.
    """
    for columna in columnas:
        df[columna] = df[columna].str.lower()
    return df



def mayus(df, columnas):
    """
    Convierte todos los valores de las columnas especificadas de un DataFrame a mayúsculas.

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se convertirán los valores a mayúsculas.

    Returns:
        pd.DataFrame: El DataFrame con los valores en mayúsculas.
    """
    for columna in columnas:
        df[columna] = df[columna].str.upper()
    return df




def titulo(df, columnas):
    """
    Convierte todos los valores de las columnas especificadas de un DataFrame a formato de título (primera letra de cada palabra en mayúscula).

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se convertirán los valores a formato de título.

    Returns:
        pd.DataFrame: El DataFrame con los valores en formato de título.
    """
    for columna in columnas:
        df[columna] = df[columna].str.title()
    return df



def comparar_reportes(reportes, columnas):
    """
    Compara si los DataFrames en la lista de reportes son iguales en las columnas especificadas.
    Se detiene y retorna False si encuentra alguna discrepancia.

    Args:
        reportes (list): Lista de DataFrames a comparar.
        columnas (list): Lista de nombres de las columnas a comparar.

    Returns:
        bool: True si todos los DataFrames son iguales en las columnas especificadas, False en caso contrario.
    """
    son_iguales = True
    for i in range(len(reportes) - 1):
        if not reportes[i][columnas].equals(reportes[i + 1][columnas]):
            son_iguales = False
            break
    return son_iguales


def a_numero(df, columnas):
    """
    Reemplaza todas las ocurrencias de un valor viejo por un nuevo valor en las columnas especificadas de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame en el que se realizará la operación.
        columnas (list): Lista de nombres de las columnas donde se realizará el reemplazo.
        viejo (str): El valor que se desea reemplazar.
        nuevo (str): El nuevo valor que reemplazará al valor viejo.

    Returns:
        pd.DataFrame: El DataFrame con los valores reemplazados.
    """
    for columna in columnas:
        df[columna] = pd.to_numeric(df[columna], errors ="coerce")
    return df