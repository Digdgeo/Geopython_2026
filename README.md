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

### Día 1 — Introducción a Python
`notebooks/dia_1/`

Entorno Jupyter (local y Colab), tipos de datos, estructuras de control, funciones, manejo de errores, módulos y Programación Orientada a Objetos (clases y herencia). Ejercicio final: Rock, Paper, Scissors, Lizard, Spock.

### Día 2 — La pila vectorial: Shapely → Fiona → GeoPandas
`notebooks/dia_2/`

Cómo se construyen las librerías vectoriales unas sobre otras. Shapely para geometrías y operaciones espaciales. Fiona para I/O vectorial sobre GDAL/OGR. GeoPandas para análisis vectorial de alto nivel: proyecciones, operaciones espaciales, joins atributales y espaciales, visualización.

### Día 3 — La pila raster: GDAL → NumPy → Rasterio
`notebooks/dia_3/`

De GDAL (la base C/C++) a Rasterio (API Pythónica sobre GDAL). NumPy para operaciones matriciales. Lectura/escritura de rasters, metadatos, reproyección, clips, enmascarado, álgebra de mapas, point sampling y estadísticas zonales.

### Día 4 — Teledetección aplicada: clase Landsat y ndvi2gif
`notebooks/dia_4/`

Construcción de una clase Python para trabajar con imágenes Landsat. Composites estacionales y multíndice con ndvi2gif. Análisis de series temporales de reflectividad.

### Día 5 — Google Earth Engine, Geemap y OSMnx
`notebooks/dia_5/`

Introducción a GEE desde Python. Geemap como interfaz interactiva: composites estacionales, visualización y exportación. Análisis de redes viales con OSMnx: descarga de grafos, rutas óptimas e isocronas.

## Datos

Los datos de ejemplo están en `data/` e incluyen capas vectoriales de Canarias, Tenerife y el entorno de Doñana (shapefiles, GeoPackage, GeoJSON).

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
| ndvi2gif | 1.1.0 | Composites estacionales (múltiples índices espectrales) |
| jupyter | — | Entorno de trabajo |
