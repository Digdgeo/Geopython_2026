# GeoPython 2026

Repositorio para el contenido del curso de **Análisis Espacial con Python** (GeoPython 2026).

## Descripción

Curso de 30 horas centrado en el ecosistema de librerías Python para análisis espacial. Una de las ideas centrales del curso es entender cómo se construyen las librerías unas sobre otras: desde GDAL/OGR y Shapely hasta GeoPandas y Rasterio, pasando por Google Earth Engine con Geemap y análisis de redes con OSMnx.

Los notebooks están disponibles en dos versiones:
- `*_complete.ipynb` — notebook completo con todo el código
- `*_exercises.ipynb` — notebook con ejercicios para resolver durante el curso

## Entorno de trabajo

El curso es **mixto**: algunos módulos se ejecutan en local y otros en Google Colab. Cada notebook indica al inicio qué entorno se recomienda.

### Entorno local (conda)

```bash
conda env create -f environment.yml
conda activate geopython2026
```

### Google Colab

Los notebooks de Colab incluyen una celda inicial con las instalaciones necesarias (`!pip install ...`).

## Temario

### Módulo 1 — Introducción a Python
`notebooks/01_intro_python/`

Entorno Jupyter, tipos de datos, estructuras de control, funciones, clases y módulos. Ejercicio final: Rock, Paper, Scissors, Lizard, Spock.

### Módulo 2 — Shapely: geometrías vectoriales
`notebooks/02_shapely_geometrias/`

La base del análisis vectorial en Python. Puntos, líneas y polígonos. Operaciones espaciales (buffer, intersect, union, difference). Relaciones topológicas.

### Módulo 3 — Fiona y GeoPandas
`notebooks/03_fiona_geopandas/`

De Fiona (I/O vectorial sobre GDAL/OGR) a GeoPandas (análisis vectorial de alto nivel). Lectura/escritura de shapefiles y GeoPackage, proyecciones, operaciones espaciales, joins atributales y espaciales.

### Módulo 4 — GDAL y Rasterio
`notebooks/04_gdal_rasterio/`

De GDAL (la base) a Rasterio (API Pythónica sobre GDAL). Lectura/escritura de rasters, metadatos, reproyección, formatos.

### Módulo 5 — Análisis raster aplicado
`notebooks/05_analisis_raster/`

NumPy para operaciones matriciales. Clips, enmascarado, álgebra de mapas, point sampling, estadísticas zonales. Clase Landsat. Librería ndvi2gif.

### Módulo 6 — Google Earth Engine y Geemap
`notebooks/06_gee_geemap_ndvi2gif/`

Introducción a GEE desde Python. Geemap como interfaz interactiva. Casos de uso: series temporales NDVI, visualización en mapas.

### Módulo 7 — Análisis de redes con OSMnx
`notebooks/07_osmx_redes/`

Descarga de grafos viales desde OpenStreetMap. Análisis de redes: rutas óptimas, isocronas, estadísticas de red.

## Datos

Los datos de ejemplo están en `data/` e incluyen capas vectoriales de Canarias y Tenerife (shapefiles, GeoPackage, GeoJSON).

## Librerías principales

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| geopandas | 1.0 | Análisis vectorial |
| shapely | 2.0 | Geometrías |
| fiona | 1.9 | I/O vectorial |
| rasterio | 1.3 | Análisis raster |
| numpy | 1.26 | Arrays |
| matplotlib | 3.8 | Visualización |
| geemap | 0.30 | Google Earth Engine |
| osmnx | 1.9 | Redes viales |
| ndvi2gif | — | Series temporales NDVI |
| jupyter | — | Entorno de trabajo |
