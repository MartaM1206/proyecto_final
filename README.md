# **Proyecto final**  
## :leaves: Estudio de la contaminación atmosférica en la Comunidad de Madrid  

### :book: <span style="color:green">**Descripción**</span>

La contaminación atmosférica es uno de los mayores desafíos ambientales y de salud pública a nivel global. Según la OMS, millones de personas están expuestas diariamente a niveles peligrosos de contaminantes como PM<sub>2.5</sub>, PM<sub>10</sub>, NO<sub>2</sub> y ozono, lo que contribuye a problemas respiratorios, cardiovasculares y otras enfermedades crónicas. Este fenómeno es particularmente crítico en áreas urbanas densamente pobladas, donde las emisiones de vehículos, industrias y actividades humanas intensivas incrementan significativamente los niveles de polución.  

Además del impacto directo en la salud, la calidad del aire influye en otros aspectos como la economía, al aumentar los costos asociados a tratamientos médicos y pérdidas de productividad laboral. También afecta el medio ambiente, causando daños a ecosistemas, acelerando el cambio climático, y reduciendo la visibilidad en áreas naturales. Ciertos efectos de la contaminación, como la lluvia ácida también afectan a edificios y monumentos, lo que conlleva un aumento de gastos en su mantenimiento y restauración.  

Un estudio publicado en 2021 indicaba que Madrid encabeza la lista de ciudades europeas con mayor mortalidad atribuible a la contaminación. Por ello, la Comunidad de Madrid nos ha encargado un informe de contaminación del aire y una recomendación de las medidas a tomar.    

### :dart: <span style="color:green"> Objetivos del proyecto</span>  
•	Analizar patrones históricos y tendencias estacionales para localizar las principales áreas afectadas y los momentos de mayor contaminación.  
•	Presentar un entregable con los resultados a la C. de Madrid.  
•	Sugerencias de medidas a tomar según los resultados del análisis.  
        
### :file_folder: <span style="color:green">**Estructura del Proyecto**</span>

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

### 🛠️ <span style="color:green">**Instalación y Requisitos**</span>

Este proyecto usa:

    - Python: Versión 3.13.0
    - Jupyter Notebook (ejecutado a través de VSCode)
    - Librerías: pandas, numpy, seaborn, matplotlib, plotly, requests, polars, psycopg2
    - PostgreSQL a través de DBeaver 
    - Streamlit 



### 📊 <span style="color:green">**Resultados y Conclusiones**</span>

**Análisis de las estaciones:**  
- Aunque hay 24 estaciones y se miden 14 contaminantes distintos, no todas las estaciones miden todos los contaminantes. Los óxidos de nitrógeno, dióxido de nitrógeno y monóxido de nitrógeno sí se miden en todas las estaciones, por lo que son lo que se han usado para poder comparar.
- Por otro lado, los contaminantes medidos en las distintas estaciones han ido variando con los años, se ha dejado de medir el monóxido de carbono en algunas y han aumentado las estaciones que miden partículas en suspensión.

**Patrones de contaminación:**   
- En general se aprecia un patrón anual muy similar en los contaminantes más medidos (óxidos de nitrógeno, dióxido de nitrógeno y monóxido de nitrógeno): de enero a marzo tiene una pronunciada caída, se mantiene relativamente bajo de marzo a octubre y vuelve a subir a valores similares a los de enero entre octubre y diciembre. 
- El ozono sigue una tendencia opuesta, es decir, alcanza sus máximos en los meses cálidos (marzo a septiembre) y los mínimos a principio y final de año. Es normal, puesto que el ozono se produce en presencia de luz solar.
- Otro contaminante bastante medido (12 - 14 estaciones) es las partículas en suspensión PM<10. Este no tiene un patrón identificable, se mantiene en niveles bajos durante todo el año aunque en algunos meses hay picos.

**Efectos del confinamiento:**  
Para comprobar si el confinamiento por la pandemia de 2020 tuvo efectos sobre los niveles de contaminación, se han representado los valores diarios de las estaciones elegidas entre febrero y junio de 2020 y,casi todos los contaminantes han caído, incluso a 0.

**Conclusiones:**   
- La mayor parte de la contaminación procede del tráfico, lo que resulta evidente al ver la caída de las medias diarias en los meses de confinaminento, quedando los contaminantes que se mantienen "de base", es decir, los que no proceden del tráfico, como los derivados de las calefacciones o las centrales térmicas y otras industrias o el ozono, generado a partir de contaminantes presentes en la atmósfera.  
- Por otro lado, los valores medidos en la estación del Parque del Retiro son menores que los medidos en otras estaciones, lo que sugiere que un aumento de las zonas verdes podría contribuir a reducir la contaminación.  
 - Los datos muestran un descenso en los valores medios anuales, lo que sugiere que las medidas tomadas por el gobierno, como pueden ser las restricciones de tráfico, el fomento del transporte público o la sustitución de calderas antiguas por otras más eficientes han dado resultado.



### 🔄 <span style="color:green">**Próximos Pasos**</span>

- Análisis de patrones horarios detallados para identificar patrones diarios de contaminación en cada estación.
- Implementar un pipeline de actualización de datos. 
- Elaboración de un Dashboard en Power BI.
- Añadir métricas como el índice de calidad del aire para facilitar la comprensión de los datos.
- Integrar datos meteorológicos para ver sus efectos sobre los niveles de contaminación.

### 🤝 <span style="color:green">**Contribuciones**</span>

Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un pull request o una issue.
Si necesitas acceso a los archivos puedes escribirme mi correo electrónico: mm.llorden@gmail.com  
También puedes encontrarme en LinkedIn.


✒️ <span style="color:green">**Autores y Agradecimientos**</span>

**Marta María Llordén Alonso** - [@MartaM1206](https://github.com/MartaM1206)
     

