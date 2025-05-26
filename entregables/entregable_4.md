# Entregable 4: Informe final
## Objetivos del proyecto
El problema central abordado por este proyecto es la grave contaminación atmosférica en la Comunidad de Madrid, que afecta la salud pública (con Madrid encabezando la mortalidad atribuible a la polución en Europa) y tiene impactos negativos económicos y ambientales.

El objetivo principal del proyecto es analizar los datos de calidad del aire para identificar patrones históricos y tendencias estacionales que permitan localizar las principales áreas y momentos de mayor contaminación. 

Las tecnologías y herramientas a emplear incluyen la API de la Comunidad de Madrid para la extracción de datos (ETL), SQL y Python para el procesamiento, y Streamlit o PowerBI para la visualización del dashboard.

---
## Proceso de Extracción, Transformación y Carga (ETL)

El proceso de ETL es fundamental para este proyecto, asegurando que los datos de contaminación del aire sean utilizables para el análisis.

1. Extracción: Los datos se obtienen de las APIs del Ayuntamiento y la Comunidad de Madrid, principalmente en formato CSV. Se extraen medidas horarias de contaminación, información de estaciones de medición y listas de contaminantes.
2. Transformación: Los datos se normalizan y se unifican los formatos. Las medidas horarias se transforman a formato largo (filas) para facilitar el análisis. Se extrae información de contaminantes desde PDFs. La agregación a medias diarias es un paso clave para simplificar el análisis de tendencias.
3. Carga: Los datos procesados se cargan en una base de datos PostgreSQL, diseñada para ser ampliable a otras Comunidades Autónomas. La base de datos incluye tablas para medidas, contaminantes, estaciones, municipios, provincias y zonas de calidad del aire.

**Desafíos en el proceso de ETL**

Durante el proceso de ETL, se abordaron varios desafíos clave:

- Integración de Múltiples Fuentes: Los datos de las APIs del Ayuntamiento y la Comunidad de Madrid presentaban diferencias en los formatos y nombres de columnas, lo que requirió una normalización y unificación exhaustiva para lograr una combinación coherente de la información.
- Extracción de Datos de PDFs: La obtención de la lista de contaminantes desde documentos PDF requirió el uso de herramientas específicas (camelot) para su extracción y estructuración.
- Presencia de valores nulos y/o extraños: debido a la progesiva implantación de estaciones en diversos municipios y zonas, se han encontrado numerosos valores nulos debido y extraños, posiblemente debidos a que se han rellenado datos de estaciones que aún no estaban implantadas. Para evitar errores en la carga y reducir el peso del archivo, esos valores nulos y extraños se han eliminado.
- Lentitud extrema de proceso de carga: intentar insertar fila por fila los aproximadamente 50 millones de registros de medidas horarias a través de sentencias INSERT individuales era inviable, ya que el proceso se proyectaba para durar hasta 18 horas. Para superar este cuello de botella, se optó por utilizar el comando COPY de PostgreSQL.
---
## Enfoque del análisis y marco temporal (2018-2024)
* **Enfoque del análisis: Madrid Capital**

Aunque la API de la Comunidad de Madrid ofrece datos de calidad del aire de diversas estaciones distribuidas por toda la región, para este proyecto, el análisis se ha centrado específicamente en las estaciones de la ciudad de Madrid (Madrid capital).

La razón principal de esta decisión estratégica es la mayor densidad y cantidad de estaciones de medición ubicadas dentro de la capital. Al concentrarnos en Madrid ciudad, hemos podido comparar entre diferentes tipos de estaciones (tráfico, fondo urbano) que están geográficamente cercanas y, por lo tanto, tienen condiciones atmosféricas, climáticas y fuentes de contaminación similares pero con influencias locales distintas, lo que facilita la identificación de áreas problemáticas específicas y la evaluación del impacto de medidas localizadas, como las restricciones de tráfico o las zonas de bajas emisiones, que son más prevalentes en la capital.

* **Período de Análisis: 2018-2024**

El análisis de la calidad del aire se ha centrado en el período comprendido entre 2018 y 2024. Los motivos principales para elegir este rango temporal son:

- Impacto de la pandemia de COVID-19 (2020):  debido a las restricciones de movilidad y los confinamientos derivados de la pandemia de COVID-19, este periodo ofreció una oportunidad única para observar una reducción drástica y atípica de las emisiones procedentes del tráfico, permitiendo aislar su impacto en la calidad del aire y entender qué contaminantes están directamente relacionados con la actividad humana convencional.
- Evaluación de medidas antipolución: Desde 2018, la ciudad de Madrid ha implementado diversas políticas y medidas para combatir la contaminación, como la Zona de Bajas Emisiones (anteriormente Madrid Central), restricciones al tráfico de vehículos más contaminantes, y programas de fomento del transporte público o la renovación de calderas. Al incluir los años anteriores y posteriores a la implementación de estas medidas, el análisis permite evaluar su efectividad a lo largo del tiempo y observar si han contribuido a una mejora sostenida de la calidad del aire.
---
## Análisis de los insights obtenidos
El Análisis Exploratorio de Datos (EDA) ha revelado varios insights críticos sobre la contaminación en Madrid:

* **Cobertura y cambios en los contaminantes medidos**
Un aspecto identificado durante el EDA es la variabilidad en la medición de contaminantes a través de las estaciones y a lo largo del tiempo. Aunque la red de estaciones mide hasta 14 contaminantes distintos, es importante destacar que no todos estos contaminantes se miden en todas las estaciones. Esta heterogeneidad significa que, para ciertas comparaciones (especialmente a nivel de toda la ciudad o entre un gran número de estaciones), solo un subconjunto de contaminantes es apto para un análisis robusto. Los óxidos de nitrógeno (NO, NO<sub>2</sub>, NO<sub>x</sub>) son los que se encuentran en todas las estaciones, convirtiéndose en los indicadores principales para análisis transversales.

Además de esta disparidad espacial, el conjunto de contaminantes medidos en las diferentes estaciones ha evolucionado a lo largo de los años. Se ha observado que algunas estaciones han dejado de medir ciertos contaminantes (como el monóxido de carbono, CO, en varias ubicaciones), mientras que otras han incorporado la medición de nuevos contaminantes, como el aumento en el número de estaciones que ahora registran partículas en suspensión (PM). Esto influye en la disponibilidad de datos históricos para análisis de tendencias a largo plazo de contaminantes específicos en ciertas estaciones, por lo que se debe tener en cuenta a la hora de realziar análisis temporales o comparaciones entre estaciones.

* **Patrones estacionales**:
    * Los **óxidos de nitrógeno (NO, NO<sub>2</sub>, NO<sub>x</sub>)** muestran un patrón anual consistente: caen de enero a marzo, se mantienen bajos hasta octubre y vuelven a subir hacia finales de año. Este comportamiento está fuertemente ligado al aumento de emisiones por calefacción y tráfico en invierno, agravado por las situaciones de inversión térmica que se dan por la topografía de Madrid.
    * El **ozono (O<sub>3</sub>)** exhibe un patrón opuesto, alcanzando sus máximos en los meses cálidos (marzo a septiembre). Esto se debe a que el ozono es un contaminante secundario que se forma por la reacción de otros contaminantes (principalmente óxidos de nitrógeno) en presencia de luz solar, por lo que en verano aumentan sus niveles.
    * Las **partículas en suspensión (PM<sub>10</sub>)** no muestran un patrón estacional tan definido, con niveles generalmente bajos y picos esporádicos que pueden estar relacionados con eventos como la calima (polvo africano) o actividades específicas locales.
* **Impacto del tráfico y el confinamiento**:
    * El análisis de las medias diarias durante el **confinamiento de 2020** (febrero-junio) reveló una caída drástica, incluso a cero, en la mayoría de los contaminantes. Esto confirma que una parte sustancial de la contaminación atmosférica, especialmente NO<sub>2</sub> y NO, tiene su origen principal en las **emisiones del tráfico rodado**. Los contaminantes "de base" (ej., calefacciones o centrales térmicas) mostraron una menor variación.
* **Diferencias geográficas**:
    * La comparación entre estaciones ha demostrado que las estaciones de **tráfico** consistentemente registran valores más altos de contaminantes primarios (como NO<sub>2</sub>) en comparación con las estaciones de **fondo** o las ubicadas en **zonas verdes**. La estación del Parque del Retiro, por ejemplo, presenta valores significativamente menores. Esto resalta el efecto positivo de las áreas verdes como "pulmones" urbanos y la influencia directa de la proximidad a vías con alto volumen de tráfico.
* **Evolución general**:
    * En general, se observa un **descenso en los valores medios anuales** de los principales contaminantes entre 2018 y 2024. Este es un hallazgo alentador que sugiere que las medidas implementadas a nivel municipal y regional están teniendo un efecto positivo en la mejora de la calidad del aire.

---
## Dashboard interactivo

Para la visualización de los resultados del análisis, se ha decidido desarrollar el dashboard utilizando Streamlit, debido a que, puesto que todo el desarrollo del proceso se ha llevado a cabo en Python (utilizando librerías como Polars, Pandas y Matplotlib), continuar con Streamlit permite la incorporación de funciones y gráficos empleados en el proyecto; además, Streamlit ofrece la posibilidad de añadir selectores interactivos e intuitivos.

El dashboard incluye las siguientes **visualizaciones clave** y funcionalidades:

* **Tráfico vs. Fondo**:
    * **Funcionalidad**: comparar los niveles de contaminación entre una estación de tráfico y una estación de fondo para un año seleccionado.
    * **Insight**: Ayuda a identificar diferencias geográficas en los niveles de contaminación. Los niveles de contaminación procedentes del tráfico son más altos en las estaciones de tráfico, en las de fondo se aprecia la tendencia estacional del ozono al estar menos influido por el tráfico. Otro dato que se puede observar es las diferencias de contaminantes medidos entre estaciones.
* **Análisis detallado**:
    * **Funcionalidad**: permite un estudio personalizado de contaminantes en una estación específica, con filtros ajustables de fecha y la visualización de medias diarias o mensuales.
    * **Insight**: revela patrones estacionales (como los picos de NO<sub>2</sub> en invierno o de O<sub>3</sub> en verano) y la presencia de eventos anómalos o de alta contaminación, como los picos de partículas en suspensión (PM<sub>10</sub>). Además permite obervar los efectos sobre la contaminación del confinamiento de 2020 o de las medidas anti polución.
 * **Análisis anual**:
    * **Funcionalidad**:  analiza la variabilidad de los niveles de contaminación a lo largo de los años, incluyendo tendencias y máximos en diferentes tipos de estaciones: tráfico, fondo y zonas verdes. Se divide en dos secciones: 
        - Evolución anual por estación: el usuario elige una estación de cada tipo para ver la evolución de las medias anuales y poder comparar entre estaciones de tráfico, fondo y grandes zonas verdes.
        - Máximos anuales por estación: compara los máximos anuales de las estaciones elegidas.
    * **Insight**: se observa una clara tendencia descencente en el período de análisis, tanto en las medias anuales como en los máximos. También permite ver las diferencias entre las estaciones de tráfico, de fondo y las de grandes zonas verdes, comprobando que la presencia de vegetación reduce los niveles de contaminación.

---

## Conexión con el Problema de Negocio

Los resultados del análisis tienen una **conexión directa con el problema** planteado por la Comunidad de Madrid:

* **Identificación de áreas y períodos críticos**: El análisis de patrones estacionales y la comparación entre estaciones nos permiten identificar claramente **qué contaminantes son problemáticos en qué épocas del año y en qué zonas geográficas**. Por ejemplo, se sabe que el NO<sub>2</sub> es un problema invernal en zonas de tráfico, mientras que el O<sub>3</sub> es un desafío veraniego. Esto proporciona a la Comunidad de Madrid información para dirigir sus esfuerzos.
* **Evaluación de la eficacia de medidas previas**: La drástica reducción de contaminantes durante el confinamiento de 2020 demuestra el impacto directo de la reducción del tráfico en la calidad del aire. El descenso general de los valores medios anuales refuerza que las políticas restrictivas de tráfico, el fomento del transporte público y las mejoras en la eficiencia energética (ej., calderas) son **medidas efectivas** y están funcionando.
* **Base para la toma de decisiones**: El dashboard y los análisis subyacentes proporcionan a la Comunidad de Madrid una **herramienta basada en datos** para monitorear continuamente la calidad del aire, evaluar el éxito de futuras intervenciones y justificar la necesidad de nuevas regulaciones o inversiones en infraestructuras verdes. La capacidad de comparar estaciones y visualizar tendencias permite una gestión más proactiva y precisa.

---

## Propuestas de recomendaciones

Basándonos en el análisis de los datos, proponemos las siguientes recomendaciones para la Comunidad de Madrid:

1.  **Intensificar las medidas de restricción al tráfico en los meses fríos**: Dado el patrón estacional de NO<sub>2</sub> y la evidente relación con el tráfico mostrada durante el confinamiento, se recomienda reforzar las zonas de bajas emisiones (ZBE) y otras medidas de restricción de vehículos (ej., Madrid Central) durante los meses de **octubre a marzo**. Esto podría incluir campañas de concienciación sobre el uso del transporte público o modos de transporte alternativos en estos periodos críticos.
2.  **Fomentar la ampliación y la creación de zonas verdes**: La diferencia significativa en los niveles de contaminación observados en la estación del Parque del Retiro subraya el papel crucial de la vegetación. Se recomienda invertir en la **creación de nuevos parques, jardines y corredores verdes**, especialmente en áreas densamente pobladas y con alto tráfico, para actuar como filtros naturales de contaminantes.
3.  **Campañas de concienciación**: Dada la tendencia del ozono, se sugiere implementar **campañas informativas y de alerta temprana** dirigidas a la población, especialmente a grupos vulnerables, durante los meses cálidos (marzo a septiembre). Estas campañas podrían incluir recomendaciones para limitar la exposición en las horas de mayor concentración de O<sub>3</sub>.

---

## Next Steps

Para seguir avanzando en el proyecto y proporcionar aún más valor a la Comunidad de Madrid, los próximos pasos incluyen:

1.  **Análisis de patrones horarios**:
    * **Objetivo**: Aprovechar la disponibilidad de medidas horarias para identificar patrones diarios de contaminación en cada estación.
    * **Beneficio**: Determinar las **horas críticas** y las **zonas más problemáticas** dentro de cada día, permitiendo la implementación de medidas preventivas y regulaciones más específicas y temporales (ej., restricciones de carga y descarga en horarios de pico, gestión de semáforos).
2.  **Optimización del pipeline de actualización de la base de datos**:
    * **Objetivo**: Implementar funciones para la actualización eficiente de la tabla `medidas` en PostgreSQL.
    * **Beneficio**: Asegurar que el dashboard siempre opere con los datos más recientes sin comprometer la integridad o el rendimiento de la base de datos. 
3. **Elaboración de un dashboard en PowerBI:**
    - **Objetivo**: Desarrollar una versión complementaria del dashboard en Power BI.
    - **Beneficio** : Power BI es una herramienta ampliamente reconocida en entornos empresariales por su facilidad de uso para usuarios no técnicos, por eso, proporcionar un dashboard en Power BI ampliaría la accesibilidad del análisis a un público más amplio dentro de la Comunidad de Madrid facilitando su integración en flujos de trabajo existentes para la toma de decisiones basada en datos.
3.  **Expansión de métricas**:
    * **Objetivo**: Desarrollar e integrar métricas más avanzadas (ej., índice de calidad del aire según normativa europea/nacional).
    * **Beneficio**: Proporcionar a los usuarios una comprensión más profunda y estandarizada de la calidad del aire, así como notificaciones proactivas cuando los niveles de contaminantes superen umbrales peligrosos.
4.  **Integración de datos meteorológicos**:
    * **Objetivo**: Incorporar datos meteorológicos (temperatura, humedad, viento, precipitaciones).
    * **Beneficio**: Realizar un análisis de correlación entre las condiciones meteorológicas y los niveles de contaminantes, lo que podría ayudar a predecir episodios de alta contaminación y a comprender mejor la dispersión atmosférica.

