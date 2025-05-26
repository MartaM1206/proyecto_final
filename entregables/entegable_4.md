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

**Desafíos en el Proceso ETL**

Durante el proceso ETL, se abordaron varios desafíos clave:

- Integración de Múltiples Fuentes: Los datos de las APIs del Ayuntamiento y la Comunidad de Madrid presentaban diferencias en los formatos y nombres de columnas, lo que requirió una normalización y unificación exhaustiva para lograr una combinación coherente de la información.
- Extracción de Datos de PDFs: La obtención de la lista de contaminantes desde documentos PDF requirió el uso de herramientas específicas (camelot) para su extracción y estructuración.
- Presencia de valores nulos y/o extraños: debido a la progesiva implantación de estaciones en diversos municipios y zonas, se han encontrado numerosos valores nulos debido y extraños, posiblemente debidos a que se han rellenado datos de estaciones que aún no estaban implantadas. Para evitar errores en la carga y reducir el peso del archivo, esos valores nulos y extraños se han eliminado.
- Lentitud extrema de proceso de carga: intentar insertar fila por fila los aproximadamente 50 millones de registros de medidas horarias a través de sentencias INSERT individuales era inviable, ya que el proceso se proyectaba para durar hasta 18 horas. Para superar este cuello de botella, se optó por utilizar el comando COPY de PostgreSQL.
---
## Enfoque del Análisis y Marco Temporal (2018-2024)
* **Enfoque del Análisis: Madrid Capital**

Aunque la API de la Comunidad de Madrid ofrece datos de calidad del aire de diversas estaciones distribuidas por toda la región, para este proyecto, el análisis se ha centrado específicamente en las estaciones de la ciudad de Madrid (Madrid capital).

La razón principal de esta decisión estratégica es la mayor densidad y cantidad de estaciones de monitoreo ubicadas dentro de la capital. Al concentrarnos en Madrid ciudad, hemos podido realizar comparaciones entre diferentes tipos de estaciones (tráfico, fondo urbano) que están geográficamente cercanas y, por lo tanto, sujetas a dinámicas atmosféricas y fuentes de emisión similares pero con influencias locales distintas, lo que facilita la identificación de áreas problemáticas específicas y la evaluación del impacto de medidas localizadas, como las restricciones de tráfico o las zonas de bajas emisiones, que son más prevalentes en la capital.

* **Período de Análisis: 2018-2024**

El análisis de la calidad del aire se ha centrado en el período comprendido entre 2018 y 2024. Los motivos principales para elegir este rango temporal son:

- Impacto de la Pandemia de COVID-19 (2020): El año 2020 fue un punto de inflexión debido a las restricciones de movilidad y los confinamientos derivados de la pandemia de COVID-19. Este periodo ofreció una oportunidad única para observar una reducción drástica y atípica de las emisiones de fuentes como el tráfico, permitiendo aislar el impacto de estas en la calidad del aire y entender qué contaminantes están directamente relacionados con la actividad humana convencional.
- Evaluación de Medidas Antipolución: Desde 2018, la ciudad de Madrid ha implementado diversas políticas y medidas para combatir la contaminación, como la Zona de Bajas Emisiones (anteriormente Madrid Central), restricciones al tráfico de vehículos más contaminantes, y programas de fomento del transporte público o la renovación de calderas. Al incluir los años anteriores y posteriores a la implementación de estas medidas, el análisis permite evaluar su efectividad a lo largo del tiempo y observar si han contribuido a una mejora sostenida de la calidad del aire.
---
## Análisis de los Insights Obtenidos
El Análisis Exploratorio de Datos (EDA) ha revelado varios insights críticos sobre la contaminación en Madrid:

* **Cobertura y Evolución de la Medición de Contaminantes**
Un aspecto identificado durante el EDA es la variabilidad en la medición de contaminantes a través de las estaciones y a lo largo del tiempo. Aunque la red de estaciones mide hasta 14 contaminantes distintos, es importante destacar que no todos estos contaminantes se miden en todas las estaciones. Esta heterogeneidad significa que, para ciertas comparaciones (especialmente a nivel de toda la ciudad o entre un gran número de estaciones), solo un subconjunto de contaminantes es apto para un análisis robusto. Los óxidos de nitrógeno (NO, NO<sub>2</sub>, NO<sub>x</sub>) son los que se encuentran en todas las estaciones, convirtiéndose en los indicadores principales para análisis transversales.

Además de esta disparidad espacial, el conjunto de contaminantes medidos en las diferentes estaciones ha evolucionado a lo largo de los años. Se ha observado que algunas estaciones han dejado de medir ciertos contaminantes (como el monóxido de carbono, CO, en varias ubicaciones), mientras que otras han incorporado la medición de nuevos contaminantes, como el aumento en el número de estaciones que ahora registran partículas en suspensión (PM). Esto influye en la disponibilidad de datos históricos para análisis de tendencias a largo plazo de contaminantes específicos en ciertas estaciones, por lo que se debe tener en cuenta a la hora de realziar análisis temporales o comparaciones entre estaciones.

* **Patrones Estacionales Dominantes**:
    * Los **óxidos de nitrógeno (NO, NO<sub>2</sub>, NO<sub>x</sub>)** muestran un patrón anual consistente: caen de enero a marzo, se mantienen bajos hasta octubre y vuelven a subir hacia finales de año. Este comportamiento está fuertemente ligado al aumento de emisiones por calefacción y tráfico en invierno, agravado por las situaciones de inversión térmica que se dan por la topografía de Madrid.
    * El **ozono (O<sub>3</sub>)** exhibe un patrón opuesto, alcanzando sus máximos en los meses cálidos (marzo a septiembre). Esto se debe a que el ozono es un contaminante secundario que se forma por la reacción de otros contaminantes (principalmente óxidos de nitrógeno) en presencia de luz solar, por lo que en verano aumentan sus niveles.
    * Las **partículas en suspensión (PM<sub>10</sub>)** no muestran un patrón estacional tan definido, con niveles generalmente bajos y picos esporádicos que pueden estar relacionados con eventos como la calima (polvo africano) o actividades específicas locales.
* **Impacto del Tráfico y Confinamiento**:
    * El análisis de las medias diarias durante el **confinamiento de 2020** (febrero-junio) reveló una caída drástica, incluso a cero, en la mayoría de los contaminantes. Esto confirma que una parte sustancial de la contaminación atmosférica, especialmente NO<sub>2</sub> y NO, tiene su origen principal en las **emisiones del tráfico rodado**. Los contaminantes "de base" (ej., calefacciones o centrales térmicas) mostraron una menor variación.
* **Diferencias Geográficas**:
    * La comparación entre estaciones ha demostrado que las estaciones de **tráfico** consistentemente registran valores más altos de contaminantes primarios (como NO<sub>2</sub>) en comparación con las estaciones de **fondo** o las ubicadas en **zonas verdes**. La estación del Parque del Retiro, en particular, presenta valores significativamente menores. Esto resalta el efecto positivo de las áreas verdes como "pulmones" urbanos y la influencia directa de la proximidad a vías con alto volumen de tráfico.
* **Evolución General de la Contaminación**:
    * En general, se observa un **descenso en los valores medios anuales** de los principales contaminantes entre 2018 y 2024. Este es un hallazgo alentador que sugiere que las medidas implementadas a nivel municipal y regional están teniendo un efecto positivo en la mejora de la calidad del aire.

---
## Dashboard Funcional e Interactivo

Para la visualización y presentación interactiva de los resultados del análisis de la calidad del aire, se ha decidido desarrollar el dashboard utilizando Streamlit. Esta herramienta de código abierto se seleccionó por varias razones clave que se alinean perfectamente con los objetivos y el flujo de trabajo del proyecto:

- Rapidez de desarrollo y prototipado: Streamlit permite construir aplicaciones web de datos y dashboards interactivos con una rapidez excepcional, utilizando únicamente código Python. Esto facilita el desarrollo ágil y el prototipado rápido de visualizaciones y funcionalidades, permitiendo iterar y obtener feedback de manera eficiente.
- Integración con Python: Dado que todo el análisis de datos, desde el ETL hasta el EDA, se ha realizado en Python (utilizando librerías como Polars, Pandas y Matplotlib), Streamlit ofrece una integración nativa y sin fricciones. Esto significa que las funciones de análisis y los objetos de visualización ya creados en Python pueden incorporarse directamente al dashboard.
- Interactividad: Streamlit proporciona una manera sencilla de añadir widgets interactivos como selectores, deslizadores y botones, que se conectan de forma intuitiva a los datos. Esto permite a los usuarios filtrar y explorar la información de manera dinámica sin necesidad de conocimientos técnicos avanzados.

El dashboard incluye las siguientes **visualizaciones clave** y funcionalidades:

* **Tendencias Temporales de Contaminantes por Estación**:
    * **Funcionalidad**: Permite seleccionar un contaminante y una estación específica para observar su evolución diaria o mensual a lo largo del tiempo.
    * **Insight**: Revela patrones estacionales (como los picos de NO<sub>2</sub> en invierno o de O<sub>3</sub> en verano) y la presencia de eventos anómalos o de alta contaminación.
* **Comparación de Medias Mensuales entre Estaciones**:
    * **Funcionalidad**: Ofrece la posibilidad de seleccionar dos estaciones diferentes y un contaminante común para comparar sus medias mensuales a lo largo de un año específico.
    * **Insight**: Ayuda a identificar diferencias geográficas en los niveles de contaminación, por ejemplo, contrastando estaciones de tráfico con estaciones de fondo o zonas verdes, lo que subraya la influencia del tipo de ubicación.
* **Distribución Geográfica de Contaminantes (Mapa)**:
    * **Funcionalidad**: Visualiza la ubicación de las estaciones y, opcionalmente, codifica por color los niveles de un contaminante seleccionado en un momento dado, mostrando las áreas más afectadas.
    * **Insight**: Proporciona una perspectiva espacial inmediata de la contaminación, ayudando a localizar zonas "calientes" en la ciudad.

El dashboard está diseñado con **filtros personalizables** (año, mes, tipo de contaminante, estación) que permiten a los usuarios explorar los datos según sus intereses. Además, se presentan **métricas clave (KPIs)** que ofrecen una visión rápida del estado general de la calidad del aire.

---

## Conexión con el Problema de Negocio

Los insights obtenidos del análisis tienen una **conexión directa y tangible con el problema de negocio** planteado por la Comunidad de Madrid:

* **Identificación de Áreas y Periodos Críticos**: El análisis de patrones estacionales y la comparación entre estaciones nos permiten identificar claramente **qué contaminantes son problemáticos en qué épocas del año y en qué zonas geográficas**. Por ejemplo, se sabe que el NO<sub>2</sub> es un problema invernal en zonas de tráfico, mientras que el O<sub>3</sub> es un desafío veraniego. Esto proporciona a la Comunidad de Madrid información granular para focalizar sus esfuerzos.
* **Evaluación de la Eficacia de Medidas Previas**: La drástica reducción de contaminantes durante el confinamiento de 2020 sirve como una "prueba de concepto" a gran escala. Demuestra el impacto directo de la reducción del tráfico en la calidad del aire. El descenso general de los valores medios anuales refuerza que las políticas restrictivas de tráfico, el fomento del transporte público y las mejoras en la eficiencia energética (ej., calderas) son **medidas efectivas** y están funcionando.
* **Base para la Toma de Decisiones Informadas**: El dashboard y los análisis subyacentes proporcionan a la Comunidad de Madrid una **herramienta basada en datos** para monitorear continuamente la situación, evaluar el éxito de futuras intervenciones y justificar la necesidad de nuevas regulaciones o inversiones en infraestructuras verdes. La capacidad de comparar estaciones y visualizar tendencias permite una gestión más proactiva y precisa de la calidad del aire.

---

## Propuestas de Recomendaciones Basadas en los Hallazgos

Basándonos en el análisis de los datos, proponemos las siguientes recomendaciones para la Comunidad de Madrid:

1.  **Intensificar las Medidas de Restricción del Tráfico en Meses Fríos**: Dado el patrón estacional de NO<sub>2</sub> y la evidente relación con el tráfico mostrada durante el confinamiento, se recomienda reforzar las zonas de bajas emisiones (ZBE) y otras medidas de restricción de vehículos (ej., Madrid Central) durante los meses de **octubre a marzo**. Esto podría incluir campañas de concienciación sobre el uso del transporte público o modos de transporte alternativos en estos periodos críticos.
2.  **Fomentar la Creación y Expansión de Zonas Verdes Urbanas**: La diferencia significativa en los niveles de contaminación observados en la estación del Parque del Retiro subraya el papel crucial de la vegetación. Se recomienda invertir en la **creación de nuevos parques, jardines y corredores verdes**, especialmente en áreas densamente pobladas y con alto tráfico, para actuar como filtros naturales de contaminantes.
3.  **Campañas de Concienciación sobre Ozono en Verano**: Dada la tendencia del ozono, se sugiere implementar **campañas informativas y de alerta temprana** dirigidas a la población, especialmente a grupos vulnerables, durante los meses cálidos (marzo a septiembre). Estas campañas podrían incluir recomendaciones para limitar la exposición en las horas de mayor concentración de O<sub>3</sub>.

---

## Next Steps

Para seguir avanzando en el proyecto y proporcionar aún más valor a la Comunidad de Madrid, los próximos pasos incluyen:

1.  **Análisis de Patrones Horarios Detallados**:
    * **Objetivo**: Aprovechar la disponibilidad de medidas horarias para identificar patrones diarios de contaminación en cada estación.
    * **Beneficio**: Determinar las **horas críticas** y las **zonas más problemáticas** dentro de cada día, permitiendo la implementación de medidas preventivas y regulaciones más específicas y temporales (ej., restricciones de carga y descarga en horarios de pico, gestión de semáforos).
2.  **Optimización del Pipeline de Actualización de Datos**:
    * **Objetivo**: Implementar una estrategia robusta para la actualización eficiente de la tabla `medidas` en PostgreSQL.
    * **Beneficio**: Asegurar que el dashboard siempre opere con los datos más recientes sin comprometer la integridad o el rendimiento de la base de datos. Esto es crucial para un monitoreo continuo y en tiempo real.
3. Elaboración de un Dashboard en Power BI:

    - **Objetivo**: Desarrollar una versión complementaria del dashboard en Power BI.
    - **Beneficio** : Aunque Streamlit ofrece gran flexibilidad y capacidades de desarrollo rápido con Python, Power BI es una herramienta ampliamente reconocida en entornos empresariales por su facilidad de uso para usuarios no técnicos. Proporcionar un dashboard en Power BI ampliaría la accesibilidad del análisis a un público más amplio dentro de la Comunidad de Madrid y facilitaría su integración en flujos de trabajo existentes para la toma de decisiones basada en datos.
3.  **Expansión de Métricas y Alertas en el Dashboard**:
    * **Objetivo**: Desarrollar e integrar métricas más avanzadas (ej., índice de calidad del aire según normativa europea/nacional) y un sistema de alertas visuales en el dashboard.
    * **Beneficio**: Proporcionar a los usuarios una comprensión más profunda y estandarizada de la calidad del aire, así como notificaciones proactivas cuando los niveles de contaminantes superen umbrales peligrosos.
4.  **Integración de Datos Meteorológicos**:
    * **Objetivo**: Incorporar datos meteorológicos (temperatura, humedad, viento, precipitaciones) de fuentes externas.
    * **Beneficio**: Realizar un análisis de correlación entre las condiciones meteorológicas y los niveles de contaminantes, lo que podría ayudar a predecir episodios de alta contaminación y a comprender mejor la dispersión atmosférica.
5.  **Despliegue y Mantenimiento Continuo**:
    * **Objetivo**: Implementar el dashboard de Streamlit en un entorno de producción accesible y establecer un plan de mantenimiento continuo.
    * **Beneficio**: Garantizar la disponibilidad y el buen funcionamiento de la herramienta para la Comunidad de Madrid a largo plazo, facilitando el monitoreo constante y la toma de decisiones.
