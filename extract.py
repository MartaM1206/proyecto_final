# importamos librerías
import pandas as pd
import numpy as np
import requests
import os
import camelot
from datetime import datetime
import zipfile

# lista de urls necesarias
url_cmadrid_anual = "https://datos.comunidad.madrid/api/3/action/package_show?id=calidad_aire_datos_historico"
url_cmadrid_mes_curso = "https://datos.comunidad.madrid/api/3/action/package_show?id=calidad_aire_datos_mes"
url_cmadrid_dia_curso = "https://datos.comunidad.madrid/api/3/action/package_show?id=calidad_aire_datos_dia"
url_madrid_anual = "https://datos.madrid.es/egob/catalogo/keyword/calidad%20aire.json"