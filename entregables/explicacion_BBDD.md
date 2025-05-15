# Base de Datos de Estaciones de Calidad del Aire

Este proyecto define una base de datos en **PostgreSQL** para almacenar información sobre estaciones de calidad del aire, mediciones y zonas geográficas.

## 📌 Estructura de la Base de Datos

La base de datos está compuesta por las siguientes tablas:

### 🏛 **provincias**

Almacena información sobre las provincias.

- `codigo_provincia` (`VARCHAR(10)`) – Clave primaria, identifica cada provincia.
- `nombre_provincia` (`TEXT`) – Nombre de la provincia.

### 🏙 **municipios**

Registra los municipios y su relación con provincias.

- `codigo_municipio` (`VARCHAR(10)`) – Clave primaria, identifica cada municipio.
- `nombre_municipio` (`TEXT`) – Nombre del municipio.
- `codigo_provincia` (`VARCHAR(10)`) – Clave foránea, referencia a `provincias`.

### 🌫 **contaminantes**

Define los distintos contaminantes medidos en las estaciones.

- `codigo_magnitud` (`VARCHAR(10)`) – Clave primaria, código del contaminante.
- `descripcion_magnitud` (`TEXT`) – Nombre del contaminante.
- `unidad` (`TEXT`) – Unidad de medición.
- `descripcion_unidad` (`TEXT`) – Explicación sobre la unidad.

### 🔬 **tecnicas_medida**

Registra las técnicas de medición utilizadas en el análisis de la calidad del aire.

- `codigo_tecnica_de_medida` (`VARCHAR(10)`) – Clave primaria, identifica la técnica de medición.
- `descripcion_tecnica_de_medida` (`TEXT`) – Explicación de la técnica utilizada.

### 📍 **zonas**

Agrupa las diferentes zonas de calidad del aire en las que se ubican las estaciones de medición.

- `codigo_zona` (`VARCHAR(10)`) – Clave primaria, identifica la zona.
- `descripcion` (`TEXT`) – Explicación de la zona.

### 🌎 **estaciones**

Guarda información sobre cada estación de medición de calidad del aire.

- `codigo_estacion` (`VARCHAR(20)`) – Clave primaria, identifica cada estación.
- `fecha_alta` (`DATE`) – Fecha de alta de la estación.
- `tipo_area` (`VARCHAR(50)`) – Define si la estación está en un área urbana o rural.
- `tipo_estacion` (`VARCHAR(50)`) – Categoría de la estación.
- `subarea_rural` (`VARCHAR(50)`) – Subcategoría dentro de áreas rurales.
- `direccion` (`TEXT`) – Dirección de la estación.
- `coord_latitud` (`DECIMAL(9, 6)`) – Latitud de la ubicación.
- `coord_longitud` (`DECIMAL(9, 6)`) – Longitud de la ubicación.
- `altitud` (`INT`) – Altitud sobre el nivel del mar.
- `analizador_*` (`BOOL`) – Indica si la estación analiza distintos contaminantes (`NO`, `NO2`, `PM10`, `O3`, `CO`, etc.).
- `codigo_zona` (`VARCHAR(10)`) – Clave foránea, referencia a `zonas`.
- `codigo_municipio` (`VARCHAR(10)`) – Clave foránea, referencia a `municipios`.
- `nombre_estacion` (`TEXT`) – Nombre de la estación.

### 📊 **medidas**

Registra las mediciones realizadas en las estaciones.

- `provincia` (`VARCHAR(10)`) – Clave foránea, referencia a `provincias`.
- `municipio` (`VARCHAR(10)`) – Clave foránea, referencia a `municipios`.
- `estacion` (`VARCHAR(10)`) – Código de la estación en el municipio.
- `magnitud` (`VARCHAR(10)`) – Clave foránea, referencia a `contaminantes`.
- `punto_muestreo` (`TEXT`) – Código que indica la estación, la técnica y el contaminante.
- `fecha` (`TEXT`) – Fecha de la medición.
- `hora` (`TEXT`) – Hora de la medición.
- `valor` (`DECIMAL(5,3)`) – Valor de la medición.
- `fecha_hora_f` (`TIMESTAMP`) – Fecha y hora en formato completo.
- `validacion` (`TEXT`) – Estado de validación de la medición.
- `id_medida` (`VARCHAR(75)`) – Clave primaria, identifica cada medición.
- `codigo_estacion` (`VARCHAR(20)`) – Clave foránea, referencia a `estaciones`.
- `codigo_tecnica` (`VARCHAR(10)`) – Clave foránea, referencia a `tecnicas_medida`.

## 🔗 Relaciones en la Base de Datos
- `municipios` está vinculado a `provincias` por `codigo_provincia`.
- `estaciones` está vinculado a `zonas` y `municipios`.
- `medidas` está vinculada a `provincias`, `municipios`, `contaminantes`, `tecnicas_medida` y `estaciones`.

