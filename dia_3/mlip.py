
# =============================================================================
# mlip.py  —  Max Line Inside Polygon
# =============================================================================
# Calcula, para cada polígono de un shapefile, las líneas más significativas:
#
#   1. Línea interior más larga: la diagonal más larga que queda completamente
#      dentro del polígono (conecta dos de sus vértices).
#   2. Línea exterior más larga: la diagonal más larga entre vértices que, sin
#      estar completamente dentro, al menos intersecta el polígono.
#   3. Perpendicular en el punto medio: línea perpendicular a la interior más
#      larga, calculada en su punto medio y recortada al borde del polígono.
#   4. Perpendicular máxima: la paralela a la perpendicular anterior que mayor
#      longitud tiene dentro del polígono (el "ancho máximo" perpendicular).
#
# Uso:
#   a = alejandro('ruta/al/poligonos.shp')
#   a.run()
#
# Los resultados se guardan en una subcarpeta 'lines/' junto al shapefile.
# =============================================================================

import os, time, fiona, shapely, math
import numpy as np
from shapely.geometry import Polygon, Point, LineString, mapping
from fiona.crs import from_epsg


class alejandro():
    """
    Calcula las líneas más largas contenidas dentro de polígonos.

    Para cada polígono del shapefile de entrada calcula:
    - La línea más larga completamente interior (entre vértices)
    - La línea más larga que intersecta (pero no está completamente dentro)
    - La perpendicular en el punto medio de la línea interior más larga
    - La perpendicular máxima (la más larga paralela a la anterior dentro del polígono)

    Uso:
        a = alejandro('ruta/al/shapefile.shp')
        a.run()
    """

    def __init__(self, shape, ext=True, perp=True, perp_max=True):
        """
        Inicializa la clase cargando el shapefile y preparando las estructuras
        de datos que usarán el resto de métodos.

        Parámetros
        ----------
        shape    : ruta al shapefile de polígonos (debe tener campo 'id')
        ext      : si True, calcula también la línea exterior más larga
        perp     : si True, calcula la perpendicular en el punto medio
        perp_max : si True, calcula la perpendicular máxima
        """
        t0 = time.time()

        # --- Rutas y configuración general ---
        self.shape = shape
        self.shp = fiona.open(shape)          # abrimos el shapefile con Fiona
        self.csr = self.shp.crs               # guardamos el CRS para usarlo al escribir
        self.perp = perp
        self.path = os.path.split(shape)[0]           # directorio del shapefile
        self.shape_name = os.path.split(shape)[1][:-4]  # nombre sin extensión
        self.npath = os.path.join(self.path, 'lines')   # carpeta de salida
        print(self.npath)
        os.makedirs(self.npath, exist_ok=True)  # la creamos si no existe

        # --- Diccionarios de resultados ---
        self.din = {}       # línea interior más larga por polígono {id: LineString}
        self.dout = {}      # línea exterior más larga por polígono {id: LineString}
        self.dperp = {}     # perpendicular en el punto medio      {id: LineString}
        self.ext = ext
        self.max_perp = {}  # perpendicular máxima                 {id: LineString}
        self.perp_max = perp_max

        # --- Estructuras para almacenar vértices y polígonos ---
        # self.d   → {id: [Point, Point, ...]}  lista de vértices de cada polígono
        # self.dpg → {id: Polygon}              geometría Shapely de cada polígono
        self.d   = {i['properties']['id']: [] for i in self.shp}
        self.dpg = {i['properties']['id']: [] for i in self.shp}

        nshape = 0
        nvertex = 0

        # --- Rutas de los shapefiles de salida ---
        self.outdin     = os.path.join(self.npath, self.shape_name + '_int.shp')
        self.outout     = os.path.join(self.npath, self.shape_name + '_out.shp')
        self.outperp    = os.path.join(self.npath, self.shape_name + '_perpendicular.shp')
        self.outmaxperp = os.path.join(self.npath, self.shape_name + '_max_perpendicular.shp')
        print(self.outdin, "\n", self.outmaxperp)

        # --- Lectura del shapefile: extraemos vértices y polígonos ---
        for e in self.shp:
            nshape += 1
            id_    = e['properties']['id']
            coords = e['geometry']['coordinates'][0]  # anillo exterior del polígono

            # Convertimos el dict GeoJSON a un objeto Shapely Polygon
            self.dpg[id_] = Polygon(e['geometry']['coordinates'][0])

            # Guardamos cada vértice como un objeto Point de Shapely
            for pt in coords:
                nvertex += 1
                self.d[id_].append(Point(pt))

        print('Se han importado', nshape, 'poligonos y', nvertex - nshape,
              'vertices en', time.time() - t0, 'segundos')

    # -------------------------------------------------------------------------
    def get_lines(self):
        """
        Busca la línea más larga interior y exterior para cada polígono.

        Estrategia: fuerza bruta — compara todos los pares únicos de vértices
        de cada polígono (combinaciones sin repetición). Para cada par:
          - Si la línea que los une está completamente DENTRO del polígono
            y es más larga que la mejor encontrada hasta ahora → la guardamos
            como línea interior.
          - Si la línea al menos INTERSECTA el polígono (pero no está dentro)
            y es más larga que la mejor exterior → la guardamos como exterior.

        Nota: la complejidad es O(n²) por polígono, donde n = número de vértices.
        Para polígonos con muchos vértices puede ser lento.
        """
        t0 = time.time()
        counter = 0  # contador de pares comparados (para estadísticas)

        # Iteramos sobre cada polígono (k = id, v = lista de vértices)
        for k, v in self.d.items():

            m_in  = 0  # longitud máxima interior encontrada hasta ahora
            m_out = 0  # longitud máxima exterior encontrada hasta ahora

            print('\n########################################Haciendo el ID:', k, '\n')

            # Doble bucle: tomamos todos los pares (e, ee) sin repetir
            # La condición nn > n garantiza que cada par se evalúa solo una vez
            for n, e in enumerate(v):
                for nn, ee in enumerate(v):
                    if nn > n:
                        counter += 1

                        # Distancia euclidiana entre los dos vértices
                        l = e.distance(ee)

                        # Solo seguimos si esta línea podría ser la más larga interior
                        if l > m_in:

                            # *** EJERCICIO 1 ***
                            # Crea una LineString conectando los dos puntos e y ee
                            line = # TU CÓDIGO AQUÍ

                            # *** EJERCICIO 2 ***
                            # Comprueba si la línea está completamente dentro del polígono
                            # Pista: Shapely tiene un predicado .within() para esto
                            if # TU CÓDIGO AQUÍ:
                                # Es la línea interior más larga hasta ahora → la guardamos
                                self.din[k] = line
                                m_in = l

                            elif line.intersects(self.dpg[k]):
                                # No está dentro pero sí intersecta → candidata a exterior
                                if l > m_out:
                                    self.dout[k] = line
                                    m_out = l

        print('Se han recorrido', counter, 'vertices en', time.time() - t0, 'segundos\n')

    # -------------------------------------------------------------------------
    def write_lines(self):
        """
        Escribe las líneas interiores (y opcionalmente exteriores) a shapefiles.

        Ambos archivos comparten el mismo schema: geometría LineString con
        atributos 'id' (int) y 'length' (float, longitud en las unidades del CRS).
        """
        # Definimos el schema del shapefile de salida
        schema = {
            'geometry':   'LineString',
            'crs':        self.shp.crs,
            'properties': {'id': 'int', 'length': 'float'}
        }

        # Escribimos las líneas interiores
        with fiona.open(self.outdin, 'w', crs=self.csr,
                        driver='ESRI Shapefile', schema=schema) as c:
            for k, v in self.din.items():
                # mapping(v) convierte el objeto Shapely a dict GeoJSON que Fiona entiende
                c.write({
                    'geometry':   mapping(v),
                    'properties': {'id': k, 'length': v.length}
                })

        # Escribimos las líneas exteriores (solo si ext=True)
        if self.ext == True:
            with fiona.open(self.outout, 'w', crs=self.csr,
                            driver='ESRI Shapefile', schema=schema) as c:
                for k, v in self.dout.items():
                    c.write({
                        'geometry':   mapping(v),
                        'properties': {'id': k, 'length': v.length}
                    })

    # -------------------------------------------------------------------------
    def get_perpendicular(self):
        """
        Calcula la perpendicular a la línea interior más larga en su punto medio.

        Pasos para cada polígono:
          1. Encontrar el punto medio de la línea interior más larga.
          2. Calcular el ángulo (bearing) de esa línea con atan2.
          3. Girar ese ángulo 90° para obtener la dirección perpendicular.
          4. Proyectar dos puntos a ambos lados del punto medio en esa dirección,
             formando una línea perpendicular lo suficientemente larga.
          5. Recortar la perpendicular con el borde del polígono → perpendicular real.
          6. (Opcional) Desplazar la perpendicular en pasos paralelos a lo largo
             de la línea interior para encontrar la perpendicular más larga.
        """
        for k, v in self.din.items():

            # 1. Punto medio de la línea interior (interpolate con normalized=True
            #    acepta valores entre 0 y 1, siendo 0.5 exactamente la mitad)
            mid_point = v.interpolate(0.5, normalized=True)

            # 2. Extraemos los dos extremos de la línea interior
            pt1 = list(v.coords)[0]
            pt2 = list(v.coords)[1]

            # 3. Calculamos el ángulo de la línea en grados con atan2
            #    atan2(dy, dx) da el ángulo respecto al eje X en radianes
            x_diff  = pt2[0] - pt1[0]
            y_diff  = pt2[1] - pt1[1]
            bearing = math.degrees(math.atan2(y_diff, x_diff))

            # 4. La perpendicular se obtiene girando el ángulo ±90°
            #    Calculamos un punto a cada lado del punto medio
            nangle   = bearing - 90                   # dirección perpendicular (lado 1)
            nbearing = math.radians(nangle)
            x  = list(mid_point.coords)[0][0] + v.length * math.cos(nbearing)
            y  = list(mid_point.coords)[0][1] + v.length * math.sin(nbearing)

            bearing = math.radians(bearing + 90)      # dirección perpendicular (lado 2)
            nx = list(mid_point.coords)[0][0] + v.length * math.cos(bearing)
            ny = list(mid_point.coords)[0][1] + v.length * math.sin(bearing)

            # 5. Construimos la línea perpendicular larga y la recortamos al polígono
            p1       = Point(x, y)
            p2       = Point(nx, ny)
            perpline = LineString((p1, p2))

            # *** EJERCICIO 3 ***
            # Calcula la intersección de perpline con el polígono self.dpg[k]
            # Esto nos da la parte de la perpendicular que queda dentro del polígono
            intersection = # TU CÓDIGO AQUÍ
            self.dperp[k] = intersection

            # 6. (Opcional) Perpendicular máxima: desplazamos la perpendicular
            #    en pasos paralelos a lo largo de la línea interior y buscamos
            #    cuál de todas esas paralelas tiene mayor longitud dentro del polígono
            if self.perp_max == True:
                md   = 0                   # longitud máxima encontrada
                dist = v.length / 100      # tamaño de cada paso (1% de la línea)
                for i in range(-50, 51):   # 50 pasos a cada lado del punto medio
                    # parallel_offset desplaza la línea perpendicularmente a sí misma
                    mperp        = perpline.parallel_offset(dist * i)
                    mintersection = mperp.intersection(self.dpg[k])
                    if mintersection.length > md:
                        self.max_perp[k] = mintersection
                        md = mintersection.length

    # -------------------------------------------------------------------------
    def write_perp_lines(self, dict_, out):
        """
        Escribe un diccionario de líneas {id: LineString} a un shapefile.

        Este método es genérico: lo usamos tanto para las perpendiculares en el
        punto medio como para las perpendiculares máximas.
        """
        schema = {
            'geometry':   'LineString',
            'crs':        self.csr,
            'properties': {'id': 'int', 'length': 'float'}
        }

        print(out)
        with fiona.open(out, 'w', crs=self.csr,
                        driver='ESRI Shapefile', schema=schema) as c:
            for k, v in dict_.items():
                c.write({
                    'geometry':   mapping(v),
                    'properties': {'id': k, 'length': v.length}
                })

    # -------------------------------------------------------------------------
    def run(self):
        """
        Orquesta la ejecución completa en el orden correcto:
          1. get_lines()        → encuentra las líneas más largas
          2. write_lines()      → las guarda en shapefiles
          3. get_perpendicular()→ calcula perpendiculares (si perp=True)
          4. write_perp_lines() → guarda perpendiculares y perpendicular máxima
        """
        self.get_lines()
        self.write_lines()
        if self.perp == True:
            self.get_perpendicular()
            self.write_perp_lines(self.dperp, self.outperp)
            if self.perp_max == True:
                self.write_perp_lines(self.max_perp, self.outmaxperp)
