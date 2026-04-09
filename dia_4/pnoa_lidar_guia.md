# Trabajando con datos LiDAR del PNOA

## ¿Qué es LiDAR?

**LiDAR** (Light Detection And Ranging) es una tecnología de teledetección activa que mide distancias emitiendo pulsos de luz láser (normalmente infrarrojo cercano) y midiendo el tiempo que tarda cada pulso en regresar al sensor tras rebotar en un objeto. A partir de esos tiempos de vuelo y conociendo la posición y orientación exacta del sensor (mediante GPS y unidad inercial IMU), se reconstruye una densa **nube de puntos 3D** georeferenciada.

![Principio de funcionamiento del LiDAR aerotransportado](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Lidar_P1_238418.jpg/1280px-Lidar_P1_238418.jpg)
*Imagen: nube de puntos LiDAR aerotransportado — cada punto registra coordenadas XYZ e intensidad del retorno. (USGS, dominio público)*

### Múltiples retornos

Una de las propiedades más valiosas del LiDAR forestal es que un mismo pulso láser puede generar **varios retornos** al atravesar la vegetación:

- **Primer retorno** → copa del árbol o superficie más alta (→ DSM)
- **Retornos intermedios** → estratos de vegetación
- **Último retorno** → suelo desnudo (→ DTM)

Esta capacidad de "penetrar" la vegetación permite derivar simultáneamente el modelo digital del terreno (DTM), el modelo de superficie (DSM) y el modelo de altura de la vegetación (CHM = DSM − DTM), algo imposible con fotografía aérea convencional.

![DTM, DSM y CHM a partir de retornos LiDAR](https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Airborne_LIDAR.jpg/1280px-Airborne_LIDAR.jpg)
*Diagrama conceptual de primeros y últimos retornos para derivar DTM y DSM.*

### Atributos de cada punto

Cada punto de una nube LiDAR almacena, además de sus coordenadas (X, Y, Z):

| Atributo | Descripción |
|---|---|
| **Intensidad** | Potencia del retorno — útil para discriminar superficies |
| **Número de retorno** | Posición del retorno dentro del pulso (1º, 2º…) |
| **Clasificación** | Clase ASPRS: suelo, vegetación, edificio, agua… |
| **Ángulo de escaneo** | Ángulo de incidencia del pulso |
| **Tiempo GPS** | Marca temporal del pulso |

---

## ¿Qué es el PNOA LiDAR?

El **Plan Nacional de Ortofotografía Aérea (PNOA)** incluye campañas periódicas de captura LiDAR (Light Detection and Ranging) que cubren todo el territorio español. Los datos están disponibles gratuitamente en el [Centro de Descargas del IGN](https://centrodedescargas.cnig.es).

Actualmente coexisten dos coberturas principales:

| Cobertura | Año aprox. | Densidad | Versión LAS |
|---|---|---|---|
| PNOA LiDAR 2ª cobertura | 2015–2020 | ~1 punto/m² | LAS 1.2 |
| PNOA LiDAR 3ª cobertura | 2023–actualidad | ~5 puntos/m² | LAS 1.4 |

---

## Formatos de archivo

### `.las`
Formato estándar de nube de puntos desarrollado por la ASPRS (American Society for Photogrammetry and Remote Sensing). Almacena los puntos **sin compresión**, por lo que los archivos son grandes (varios GB por tesela).

### `.laz`
Versión **comprimida** del formato LAS. Ocupa aproximadamente un 10-20% del tamaño del `.las` equivalente, con compresión sin pérdida. Es el formato de distribución habitual del PNOA. Para trabajar con él en Python es necesario instalar el backend de descompresión `lazrs`.

### `.copc.laz`
**Cloud Optimized Point Cloud** — una variante del `.laz` que organiza los puntos en una estructura jerárquica de octree dentro del propio archivo. Esto permite acceder a subconjuntos de puntos (por área o nivel de detalle) sin descomprimir el archivo completo, lo que lo hace muy eficiente para visualización y análisis en herramientas modernas. La 3ª cobertura del PNOA se distribuye en este formato.

> **Nota:** cuando cargas un `.laz` o `.las` en QGIS, este genera automáticamente un `.copc.laz` indexado mediante Untwine antes de mostrarlo. Ese archivo se guarda junto al original y es el que QGIS usa para la visualización.

### Resumen

| Formato | Compresión | Indexado | Compatibilidad |
|---|---|---|---|
| `.las` | No | No | Universal |
| `.laz` | Sí | No | Amplia (requiere backend LAZ) |
| `.copc.laz` | Sí | Sí (octree) | Herramientas modernas |

---

## Versiones LAS y problemas de compatibilidad

El formato LAS ha evolucionado a lo largo de los años. Las versiones más relevantes son:

- **LAS 1.2** — la más compatible, soportada por prácticamente todas las herramientas.
- **LAS 1.4** — introducida en 2013, añade nuevos formatos de punto (6-10), mayor precisión y soporte para retornos múltiples extendidos. Es la versión usada por la 3ª cobertura del PNOA.

El problema es que muchas herramientas todavía no soportan bien LAS 1.4:

| Herramienta | LAS 1.2 | LAS 1.4 | COPC |
|---|---|---|---|
| QGIS (Untwine) | ✅ | ⚠️ Puede fallar (error 139) | ✅ |
| CloudCompare < 2.13 | ✅ | ❌ | ❌ |
| CloudCompare ≥ 2.13 | ✅ | ✅ | ✅ |
| laspy + lazrs (Python) | ✅ | ✅ | ✅ (solo lectura) |
| PDAL | ✅ | ✅ | ✅ |

> **Recomendación:** para trabajar con la 3ª cobertura del PNOA, actualiza a **CloudCompare 2.13 o superior** y usa los archivos `.copc.laz` directamente en QGIS. Si QGIS da error al procesar un `.laz` LAS 1.4 (error 139), conviértelo primero a LAS 1.2 — QGIS generará el `.copc.laz` correctamente a partir del archivo convertido.

---

## Clasificación de puntos

Los datos PNOA vienen con los puntos ya clasificados según el estándar ASPRS:

| Clase | Significado |
|---|---|
| 1 | Sin clasificar |
| 2 | Suelo |
| 3 | Vegetación baja |
| 4 | Vegetación media |
| 5 | Vegetación alta |
| 6 | Edificio |
| 7 | Ruido |
| 9 | Agua |
| 12 | Solapamiento entre pasadas |

Para consultar las clasificaciones disponibles en un archivo:

```python
import numpy as np

clases_unicas = np.unique(las.classification)
nombres = {0: "Nunca clasificado", 1: "Sin clasificar", 2: "Suelo",
           3: "Vegetación baja", 4: "Vegetación media", 5: "Vegetación alta",
           6: "Edificio", 7: "Ruido", 9: "Agua", 12: "Solapamiento"}

for clase in sorted(clases_unicas):
    count = np.sum(las.classification == clase)
    porcentaje = (count / len(las.points)) * 100
    nombre = nombres.get(int(clase), "Desconocida")
    print(f"  Clase {clase}: {nombre} - {count:,} puntos ({porcentaje:.1f}%)")
```

---

## Leer archivos LAZ con Python

Para leer archivos `.laz` con `laspy` es necesario instalar el backend de descompresión:

```bash
pip install lazrs
```

Lectura básica:

```python
import laspy

las = laspy.read("PNOA_2024_AND_262-4165_H30_NPC01.laz")

print(f"Versión LAS: {las.header.version}")
print(f"Formato de punto: {las.header.point_format}")
print(f"Total puntos: {len(las.points):,}")
print(f"Extensión X: {las.header.x_min:.2f} - {las.header.x_max:.2f}")
print(f"Extensión Y: {las.header.y_min:.2f} - {las.header.y_max:.2f}")
print(f"Extensión Z: {las.header.z_min:.2f} - {las.header.z_max:.2f}")
```

---

## Convertir LAS 1.4 a LAS 1.2

Si necesitas compatibilidad con herramientas que no soportan LAS 1.4. La conversión conserva los campos esenciales (coordenadas, clasificación e intensidad).

```python
import laspy
from pathlib import Path
from tqdm import tqdm

carpeta_entrada = Path("/ruta/a/tus/archivos/")
carpeta_salida = carpeta_entrada / "las12"
carpeta_salida.mkdir(exist_ok=True)

archivos = list(carpeta_entrada.glob("*.laz")) + list(carpeta_entrada.glob("*.las"))

for archivo in tqdm(archivos, desc="Convirtiendo"):
    try:
        las = laspy.read(archivo)
        nuevo = laspy.LasData(header=laspy.LasHeader(point_format=1, version="1.2"))
        nuevo.x = las.x
        nuevo.y = las.y
        nuevo.z = las.z
        nuevo.intensity = las.intensity
        salida = carpeta_salida / (archivo.stem + ".las")
        nuevo.write(salida)
    except Exception as e:
        tqdm.write(f"✗ Error en {archivo.name}: {e}")

print("Conversión completada.")
```

> **Nota:** los archivos `.las` resultantes son más grandes que los `.laz` originales al no estar comprimidos. Una vez que QGIS genera el `.copc.laz` a partir del `.las` convertido, puedes borrar el `.las` intermedio si quieres ahorrar espacio.

---

## Concatenar varios tiles en un único archivo

Para trabajar con varios tiles como si fueran uno solo:

```python
import laspy
from pathlib import Path

carpeta = Path("/ruta/a/tus/tiles/")
archivos = sorted(carpeta.glob("*.laz"))

# Leer todos los tiles
las_list = []
for archivo in archivos:
    print(f"Leyendo {archivo.name}...")
    las_list.append(laspy.read(archivo))

print(f"Total puntos: {sum(len(l.points) for l in las_list):,}")

# Guardar como un único archivo .laz conservando todos los atributos
header_nuevo = laspy.LasHeader(
    point_format=las_list[0].header.point_format,
    version=las_list[0].header.version
)
header_nuevo.offsets = las_list[0].header.offsets
header_nuevo.scales = las_list[0].header.scales

with open("merged.laz", "wb") as f:
    with laspy.LasWriter(f, header=header_nuevo) as writer:
        for i, las in enumerate(las_list):
            print(f"  Escribiendo tile {i+1}/{len(las_list)}...")
            writer.write_points(las.points)

print("Guardado.")
```

> **Nota:** `laspy` no puede escribir archivos `.copc.laz` — solo `.laz` estándar. Si necesitas el merged en formato COPC para visualizarlo en QGIS, procésalo con PDAL después.

---

## Generar DTM, DSM y CHM con Python

Con los puntos ya clasificados se pueden generar los tres productos principales directamente desde Python usando binning por píxel. La resolución máxima recomendable depende de la densidad de puntos de suelo — con ~5 puntos/m² totales y ~35% de puntos de suelo, **0.5m** es una resolución adecuada.

```python
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from scipy.ndimage import distance_transform_edt

# ---- PARÁMETROS ----
resolucion = 0.5  # metros por píxel
ruta_salida = "/ruta/de/salida/"

# ---- CARGAR PUNTOS ----
las_merged = laspy.read("merged.laz")
x_all = np.asarray(las_merged.x, dtype=np.float64)
y_all = np.asarray(las_merged.y, dtype=np.float64)
z_all = np.asarray(las_merged.z, dtype=np.float64)
clases = np.asarray(las_merged.classification)

# ---- DEFINIR GRID ----
x_min, x_max = x_all.min(), x_all.max()
y_min, y_max = y_all.min(), y_all.max()
cols = int((x_max - x_min) / resolucion) + 1
rows = int((y_max - y_min) / resolucion) + 1
transform = from_origin(x_min, y_max, resolucion, resolucion)
print(f"Grid: {rows} filas x {cols} columnas")

# ---- FUNCIONES AUXILIARES ----
def rellenar_huecos(array):
    """Rellena NaN con el valor del píxel válido más cercano."""
    mask = np.isnan(array)
    if mask.any():
        idx = distance_transform_edt(mask, return_distances=False, return_indices=True)
        return array[tuple(idx)]
    return array

def guardar_tif(array, nombre):
    ruta = ruta_salida + nombre
    with rasterio.open(ruta, "w", driver="GTiff", height=rows, width=cols,
                       count=1, dtype="float32", crs="EPSG:25830",
                       transform=transform, nodata=np.nan) as dst:
        dst.write(array.astype(np.float32), 1)
    print(f"Guardado: {ruta}  Min: {array.min():.2f}  Max: {array.max():.2f}")

def calcular_raster(x, y, z, operacion='min'):
    """Binning de puntos en píxeles, tomando el mínimo o máximo Z."""
    col_idx = np.floor((x - x_min) / resolucion).astype(np.int32).clip(0, cols - 1)
    row_idx = np.floor((y_max - y) / resolucion).astype(np.int32).clip(0, rows - 1)
    df = pd.DataFrame({'row': row_idx, 'col': col_idx, 'z': z})
    resultado = df.groupby(['row', 'col'])['z'].min() if operacion == 'min' \
                else df.groupby(['row', 'col'])['z'].max()
    raster = np.full((rows, cols), np.nan, dtype=np.float32)
    raster[resultado.index.get_level_values('row'),
           resultado.index.get_level_values('col')] = resultado.values.astype(np.float32)
    return raster

# ---- DTM — mínimo Z de puntos de suelo (clase 2) ----
print("\nGenerando DTM...")
mask_suelo = clases == 2
dtm = calcular_raster(x_all[mask_suelo], y_all[mask_suelo], z_all[mask_suelo], 'min')
print(f"Huecos: {np.isnan(dtm).sum():,} ({100*np.isnan(dtm).mean():.1f}%)")
dtm_filled = rellenar_huecos(dtm)
guardar_tif(dtm_filled, "dtm_05.tif")

# ---- DSM — máximo Z excluyendo ruido (7) y solapamiento (12) ----
print("\nGenerando DSM...")
mask_dsm = ~np.isin(clases, [7, 12])
dsm = calcular_raster(x_all[mask_dsm], y_all[mask_dsm], z_all[mask_dsm], 'max')
print(f"Huecos: {np.isnan(dsm).sum():,} ({100*np.isnan(dsm).mean():.1f}%)")
dsm_filled = rellenar_huecos(dsm)
guardar_tif(dsm_filled, "dsm_05.tif")

# ---- CHM = DSM - DTM ----
print("\nGenerando CHM...")
chm = dsm_filled - dtm_filled
chm[chm < 0] = 0  # eliminar valores negativos por errores de interpolación
guardar_tif(chm, "chm_05.tif")

print("\nProceso completado.")
```

---

## Flujo de trabajo recomendado con datos PNOA

```
Descarga del IGN (.laz / .copc.laz)
        │
        ├── Visualización
        │       ├── CloudCompare ≥ 2.13  →  abrir directamente
        │       └── QGIS
        │               ├── .copc.laz  →  cargar directamente
        │               └── .laz LAS 1.4  →  convertir a LAS 1.2 → QGIS genera .copc.laz
        │
        └── Análisis en Python
                ├── Un tile       →  laspy.read()
                ├── Varios tiles  →  laspy.read() x N + LasWriter → merged.laz
                └── Productos raster
                        ├── DTM  →  mínimo Z clase 2 + relleno huecos
                        ├── DSM  →  máximo Z (sin ruido/solapamiento) + relleno huecos
                        └── CHM  →  DSM - DTM
```
