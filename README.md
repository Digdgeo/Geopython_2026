# GeoPython 2026

> **Análisis Espacial con Python** · Gabinete de Formación del CSIC  
> Estación Biológica de Doñana, Sevilla · 6–10 abril 2026

[![Ver presentación del curso](https://i.imgur.com/mmIjQjA.png)](https://slides.com/diegogarciadiaz/aepython/fullscreen)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Conda](https://img.shields.io/badge/Conda-Anaconda-44A833?logo=anaconda&logoColor=white)](https://docs.conda.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Grabaciones de las sesiones

| Día | Contenido | Enlace |
|-----|-----------|--------|
| Día 1 | Intro Google Colab + Introducción a Python | [Ver grabación](https://balanbbb.corp.csic.es/playback/presentation/2.3/49d59d607ccc44671d0e0ada701426dd6a2dcfd4-1775458392383) |
| Día 2 | Clases en Python · Pandas · Stack vectorial | [Ver grabación](https://balanbbb.corp.csic.es/playback/presentation/2.3/49d59d607ccc44671d0e0ada701426dd6a2dcfd4-1775545152074) |
| Día 3 | Entorno Anaconda · Stack vectorial | [Ver grabación](https://balanbbb.corp.csic.es/playback/presentation/2.3/49d59d607ccc44671d0e0ada701426dd6a2dcfd4-1775631555977) |
| Día 4 | Nubes de puntos LiDAR (laspy) · Stack raster: NumPy y Rasterio | [Ver grabación](https://balanbbb.corp.csic.es/playback/presentation/2.3/49d59d607ccc44671d0e0ada701426dd6a2dcfd4-1775717939412) |
| Día 5 | Clase Landsat · Geemap · ndvi2gif | [Ver grabación](https://balanbbb.corp.csic.es/playback/presentation/2.3/49d59d607ccc44671d0e0ada701426dd6a2dcfd4-1775804390520) |

---

## Entorno de trabajo

El curso es **mixto**: los dos primeros días trabajamos en Google Colab; a partir del Día 3 pasamos al entorno local con Anaconda.

### Días 1–2 — Google Colab

Accede en [colab.research.google.com](https://colab.research.google.com). Los notebooks incluyen una celda inicial con las instalaciones necesarias (`!pip install ...`).

### Días 3–5 — Entorno local (conda)

```bash
conda env create -f environment.yml
conda activate geopython2026
```

---

## Temario

### Día 1 — Introducción a Python

[![Notebook completo](https://img.shields.io/badge/Notebook-completo-blue?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_1/notebooks/01_intro_python_complete.ipynb)
[![Ejercicios](https://img.shields.io/badge/Notebook-ejercicios-orange?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_1/notebooks/01_intro_python_exercises.ipynb)

Primer contacto con Jupyter en Google Colab. Introducción a Python: tipos de datos, estructuras de control y funciones. Como ejercicio de cierre, el clásico **Rock, Paper, Scissors, Lizard, Spock** popularizado por The Big Bang Theory.

- Google Colab: entorno, atajos, integración con Drive
- Variables, strings, numbers, booleans
- Listas, tuplas, sets, diccionarios
- Bucles `for` / `while` y condicionales
- Manejo de errores (`try` / `except`)
- Funciones y módulos

![](dia_1/grafico_RSCPS.png)

---

### Día 2 — Clases en Python y Pandas

[![Clases Python](https://img.shields.io/badge/Notebook-clases-blue?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_1/notebooks/01b_python_classes.ipynb)
[![Pandas](https://img.shields.io/badge/Notebook-pandas-blue?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_1/notebooks/01c_pandas_dataframes.ipynb)

Terminamos los temas pendientes de Python y damos el salto a **Pandas**, la librería de referencia para datos tabulares. Introducción a la Programación Orientada a Objetos con herencia.

- Clases en Python: `__init__`, métodos, atributos
- Herencia y polimorfismo
- Pandas: Series y DataFrames
- Lectura de CSV/Excel, indexado y filtrado
- Operaciones, agrupaciones y visualización básica

![](https://i.imgur.com/mcWcZYY.png)

---

### Día 3 — Entorno Anaconda y análisis vectorial

[![Anaconda](https://img.shields.io/badge/Guía-Anaconda-44A833?logo=anaconda)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_2/introduccion_anaconda.md)
[![Vectorial completo](https://img.shields.io/badge/Notebook-completo-blue?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_2/notebooks/02_shapely_fiona_geopandas_complete.ipynb)
[![Ejercicios](https://img.shields.io/badge/Notebook-ejercicios-orange?logo=jupyter)](https://github.com/Digdgeo/Geopython_2026/blob/main/dia_2/notebooks/02_shapely_fiona_geopandas_exercises.ipynb)

Pasamos al entorno local con Anaconda y arrancamos con el análisis vectorial. La clave del día es entender cómo se construyen las librerías unas sobre otras:

```
GDAL/OGR  →  Fiona · Shapely  →  GeoPandas
```

- Anaconda: conda vs pip, entornos virtuales, `environment.yml`
- **Shapely**: geometrías, predicados y operaciones espaciales en memoria
- **Fiona**: I/O vectorial sobre GDAL/OGR, control fino del schema
- **GeoPandas**: análisis vectorial de alto nivel, CRS, spatial joins, overlay y visualización

![](img/fincas__.png)

---

### Día 4 — Nubes de puntos LiDAR y stack raster

> **Datos de la sesión:** [Descargar datos LiDAR](https://saco.csic.es/s/7fwsC5oXLtRwtMe)

Trabajamos con nubes de puntos LAZ del PNOA y con los rasters derivados de Canopy Height. El mismo esquema de capas aplicado al mundo raster:

```
GDAL  →  NumPy  →  Rasterio
```

- **LiDAR / LAZ**: lectura de nubes de puntos del PNOA con `laspy`, visualización y filtrado por clase de retorno
- **Canopy Height**: generación de modelos de altura de vegetación a partir de MDS y MDT
- **GDAL** desde Python: drivers, metadatos, reproyección
- **NumPy**: arrays multidimensionales y álgebra de mapas
- **Rasterio**: lectura/escritura de rasters, clips, enmascarado, estadísticas zonales y reclasificación

![](img/las_img.png)

---

### Día 5 — Clase Landsat, Geemap y ndvi2gif

*Viernes 10 de abril*

> **Datos de la sesión:** [Descargar imagen Landsat](https://saco.csic.es/s/tmKZqPiDdiSYyxe)

Cerramos el curso con acceso a imágenes de satélite desde Python. Creamos una clase `Landsat` para encapsular la lógica de descarga y procesado, y exploramos Geemap como interfaz interactiva para análisis espacial en la nube.

- **Clase Landsat**: POO aplicada al procesado de imágenes de satélite
- **Geemap**: mapas interactivos, composites estacionales, exportación
- **ndvi2gif**: compuestos estacionales basados en estadísticas sobre índices de teledetección, clasificación y análisis fenológico

![](https://i.imgur.com/Vwt3r1r.png)

---

## Librerías principales

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| geopandas | 1.0 | Análisis vectorial |
| shapely | 2.0 | Geometrías y operaciones espaciales |
| fiona | 1.9 | I/O vectorial (sobre GDAL/OGR) |
| rasterio | 1.3 | Análisis raster |
| numpy | 1.26 | Arrays y álgebra de mapas |
| pandas | 2.0 | Datos tabulares |
| matplotlib | 3.8 | Visualización |
| geemap | 0.30 | Google Earth Engine interactivo |
| osmnx | 1.9 | Redes viales |
| ndvi2gif | 1.1.0 | Compuestos estacionales, clasificación y análisis fenológico |
| jupyter | — | Entorno de trabajo |

---

## Datos

Los datos de ejemplo están en `data/` e incluyen capas vectoriales de Canarias, Tenerife y el entorno de Doñana (shapefiles, GeoPackage, GeoJSON).

---

*GeoPython 2026 · CSIC / Estación Biológica de Doñana*
