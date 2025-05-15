# **Documentación del Pipeline ETL: Análisis de Contaminación del Aire en la Comunidad de Madrid**

## **1️⃣ Introducción**

Este proyecto tiene como objetivo analizar los datos de **contaminación del aire** en la Comunidad de Madrid para identificar **zonas y períodos críticos** y proponer medidas para mejorar la calidad del aire.

## **2️⃣ Extracción de datos**

Los datos se obtienen a través de las **APIs del Ayuntamiento de Madrid y la Comunidad de Madrid**, en formato **CSV**, incluyendo:

- **Medidas horarias de contaminación**
- **Información sobre estaciones de medición**
- **Lista de contaminantes medidos**

## **3️⃣ Transformación de datos**

El proceso de transformación incluye:

- **Unificación de formatos**: Los datos de medidas y estaciones tenían diferencias en las fuentes, por lo que se ha **normalizado** la estructura y fusionado la información.
- **Transformación de medidas**: Los datos inicialmente estaban en **columnas** y se han convertido a **filas**, facilitando el análisis.
- **Gestión de contaminantes**: La lista de contaminantes fue extraída desde un **PDF** de la Comunidad de Madrid.

## **4️⃣ Carga de datos**

Los datos procesados se almacenan en una **base de datos PostgreSQL** para su posterior análisis.

Estructura de la base de datos:

- **Medidas**
- **Contaminantes y unidades**
- **Técnicas de medición**
- **Estaciones de medición**
- **Municipios**
- **Zonas de calidad del aire**
- **Provincias**

Se ofrece una explicación detallada de la base de datos en el archivo explicacion_BBDD.md
Además, los datos se cargarán en **Power BI** para crear un **dashboard**, aunque también se valora el uso de **Streamlit** como alternativa.

## **5️⃣ Herramientas y tecnologías utilizadas**

- **Python**: Lenguaje de programación base.
- **pandas**: Manipulación y limpieza de datos.
- **psycopg2**: Conexión con PostgreSQL.
- **json**: Transformación de respuestas de la API.
- **camelot**: Extracción de tablas desde PDF.
- **os y zipfile**: Gestión de archivos y extracción de datos comprimidos.
- **requests**: Descarga de datos desde APIs.

## **6️⃣ Desafíos y aprendizajes**

Principales retos del proceso:

- **Integración de múltiples fuentes**: Se tuvo que **normalizar los nombres de columnas** y estructuras de datos para lograr una combinación coherente.
- **Actualización de la base de datos:** Un desafío pendiente es definir el mejor método para actualizar la tabla `medidas`, asegurando que los nuevos registros se incorporen sin comprometer la integridad de los existentes. Se explorarán estrategias como `ON CONFLICT`, triggers en PostgreSQL o funciones en Python para gestionar la actualización eficiente de los datos.

## **7️⃣ Próximos pasos**

- **🔍 Pendiente:** Implementar `tqdm` para mejorar la visibilidad del progreso
- **🔍 Pendiente:** Determinar el mejor método para **actualizar los datos de `medidas`**.

---