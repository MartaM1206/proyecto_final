# **Proyecto final**  
## Estudio de la contaminación atmosférica en la Comunidad de Madrid  

:book:**Descripción**

La contaminación atmosférica es uno de los mayores desafíos ambientales y de salud pública a nivel global. Según la OMS, millones de personas están expuestas diariamente a niveles peligrosos de contaminantes como PM<sub>2.5</sub>, PM<sub>10</sub>, NO<sub>2</sub> y ozono, lo que contribuye a problemas respiratorios, cardiovasculares y otras enfermedades crónicas. Este fenómeno es particularmente crítico en áreas urbanas densamente pobladas, donde las emisiones de vehículos, industrias y actividades humanas intensivas incrementan significativamente los niveles de polución.  

Además del impacto directo en la salud, la calidad del aire influye en otros aspectos como la economía, al aumentar los costos asociados a tratamientos médicos y pérdidas de productividad laboral. También afecta el medio ambiente, causando daños a ecosistemas, acelerando el cambio climático, y reduciendo la visibilidad en áreas naturales. Ciertos efectos de la contaminación, como la lluvia ácida también afectan a edificios y monumentos, lo que conlleva un aumento de gastos en su mantenimiento y restauración.  

Un estudio publicado en 2021 indicaba que Madrid encabeza la lista de ciudades europeas con mayor mortalidad atribuible a la contaminación. Por ello, la Comunidad de Madrid nos ha encargado un informe de contaminación del aire y una recomendación de las medidas a tomar.    

### Objetivos del proyecto y su impacto esperado  
•	Analizar patrones históricos y tendencias estacionales para localizar las principales áreas afectadas y los momentos de mayor contaminación.  
•	Presentar un entregable con los resultados a la C. de Madrid.  
•	Sugerencias de medidas a tomar según los resultados del análisis.  
        
:file_folder: <span style="color:lightgreen">**Estructura del Proyecto**</span>

    .
    ├── bbdd_scripts/                   
    │   └── create_tables.sql         # Script para la creación del esquema de la base de datos.
    ├── data/
    │   └── raw/                      # Almacena los datos brutos tal como se descargan de las fuentes originales.
    ├── entregables/                  # Carpeta para todos los entregables del proyecto.
    ├── notebooks/                    # Carpeta para todos los cuadernos Jupyter del proyecto.
    │   └── notebooks_EDA/            # Contiene los cuadernos para el Análisis Exploratorio de Datos (EDA).
    ├── src/                          # Directorio con el código fuente modularizado del proyecto.
    │   ├── __init__.py               # Archivo vacío que marca 'src' como un paquete Python.
    │   ├── funciones_dashboard.py    # Funciones de apoyo y utilidades específicas para la aplicación Streamlit.
    │   ├── funciones_eda.py          # Funciones reutilizables para el Análisis Exploratorio de Datos.
    │   ├── funciones_extract.py      # funciones para la extracción de datos desde las APIs.
    │   ├── funciones_load.py         # Funciones para la carga en la base de datos.
    │   ├── funciones_transform.py    # Lógica para la limpieza, normalización y transformación de los datos.
    │   └── funciones_update.py       # Funciones para la actualización incremental de datos en la base de datos (next steps)
    ├── dashboard.py                  # Script principal de la aplicación web interactiva desarrollada con Streamlit.
    ├── ETL.py                        # Script principal para ejecutar el pipeline completo de Extracción, Transformación y Carga.
    ├── ETL_update.py                  # Script para la actualización periódica de los datos del pipeline ETL (next steps)
    ├── README.md                     # Documento principal del proyecto con descripción, objetivos y guía.
    └──requirements.txt               # Lista de todas las dependencias de Python necesarias para ejecutar el proyecto.

🛠️ <span style="color:lightgreen">**Instalación y Requisitos**</span>

Este proyecto usa:

    - Python: Versión 3.13.0
    - Jupyter Notebook (ejecutado a través de VSCode)
    - Librerías: pandas, numpy, seaborn, matplotlib



📊 <span style="color:lightgreen">**Resultados y Conclusiones**</span>

**Análisis de ingresos:**  
 - En general, la tendencia en los ingresos es creciente, han aumentado entre 2013 y 2021.

 - La mayor parte de los ingresos corresponde en un 50 % a Receitas Correntes (ingresos regulares por tasas e impuestos habituales) y un 48% a Receitas de Capital (ingresos debidos a la venta de activos del gobierno, préstamos y financiación a largo plazo), por lo que son estas dos categorías las más analizadas.    

**Análisis de discrepancias:**

- Considerando el total de ingresos, exceptuando 2018, 2019 y 2021, el valor previsto es mayor que el realizado y este último experimenta una fuerte caída en 2020, posiblemente debido a la pandemia. 

- Las categorías con mayores discrepancias son Receitas Correntes y Receitas de Capital.

- Parece haber una infra recaudación de los impuestos, lo que provocaría las discrepancias en Receitas Correntes, que además son las que mayor porcentaje de ingresos supone.

- En cuanto a unidades gestoras, la que presenta mayor problemática es la Coordenacao De Orcamento E Financas Do Frgps si consideramos la diferencia absoluta entre ingresos previstos y realizados o la Reserva De Contingencia/Mef si consideramos la diferencia media. Si vamos a nivel de organismo superior, el Ministério Da Economia es el que presenta mayor diferencia total entre valor previsto y valor realizado. Sería conveniente analizar estas unidades gestoras y el Ministério Da Economia para encontrar el origen de la infra recaudación o el error en la planificación de las Receitas de Capital.



🔄 <span style="color:lightgreen">**Próximos Pasos**</span>

- Analizar detalladamente las unidades gestoras con mayores discrepancias, especialmente las dependientes del Ministério Da Economia, para identificar posibles causas de la infra recaudación y poder implementar mejoras en este aspecto



🤝 <span style="color:lightgreen">**Contribuciones**</span>

Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un pull request o una issue.
Si necesitas acceso a los archivos puedes escribirme mi correo electrónico: mm.llorden@gmail.com  
También puedes encontrarme en LinkedIn


✒️ <span style="color:lightgreen">**Autores y Agradecimientos**</span>

**Marta María Llordén Alonso** - [@MartaM1206](https://github.com/MartaM1206)
     

