
# =============================================================================
# rmpi.py  —  Random Move Points Inside (a bounding frame)
# =============================================================================
# Toma un shapefile de puntos donde cada punto pertenece a un grupo (campo
# ID_progres) y mueve aleatoriamente cada grupo dentro de un marco envolvente.
#
# El proceso para cada grupo es:
#   1. Calcular el centro de gravedad (media de coordenadas) del grupo.
#   2. Elegir aleatoriamente uno de los 4 cuadrantes del marco (NW/NE/SW/SE).
#   3. Calcular un desplazamiento aleatorio que lleve el centro hacia ese cuadrante,
#      verificando que el punto resultante cae dentro del marco.
#   4. Rotar todos los puntos del grupo un ángulo aleatorio (0-360°) alrededor
#      del centro de gravedad usando shapely.affinity.
#   5. Trasladar los puntos rotados con el desplazamiento calculado.
#   6. Escribir el resultado a un nuevo shapefile.
#
# Uso:
#   a = alessandro('puntos.shp', 'marco.shp')
#   a.run()
# =============================================================================

import os, fiona, random
import numpy as np
from shapely import affinity
from shapely.geometry import mapping, shape, Point, Polygon
from fiona.crs import from_epsg


class alessandro:
    """
    Mueve grupos de puntos de forma aleatoria dentro de un marco envolvente.

    Para cada grupo de puntos (identificados por ID_progres):
    1. Calcula el centroide y el centro de gravedad del grupo
    2. Elige aleatoriamente un cuadrante del marco (NW, NE, SW, SE)
    3. Calcula un desplazamiento aleatorio hacia ese cuadrante
    4. Rota el grupo sobre su centro de gravedad con un ángulo aleatorio
    5. Aplica la traslación y escribe el resultado a shapefile

    Uso:
        a = alessandro('puntos.shp', 'marco.shp')
        a.run()
    """

    def __init__(self, pointshp, marco):
        """
        Inicializa la clase creando las carpetas de salida necesarias y
        preparando el diccionario principal donde se almacenarán los parámetros
        de movimiento de cada individuo (grupo de puntos).

        Parámetros
        ----------
        pointshp : ruta al shapefile de puntos (debe tener campo 'ID_progres')
        marco    : ruta al shapefile con el polígono que define el área de movimiento
        """
        self.pointshp = pointshp
        self.marco    = marco

        # Extraemos el directorio y nombre base del shapefile de puntos
        self.base = os.path.split(self.pointshp)[0]
        self.name = os.path.split(self.pointshp)[1][:-4]

        # Carpetas de salida:
        #   moved/     → puntos movidos y rotados
        #   moved/cc/  → centroides movidos
        #   moved/cg/  → centros de gravedad movidos
        self.moved   = os.path.join(self.base, 'moved')
        self.movedcc = os.path.join(self.moved, 'cc')
        self.movedcg = os.path.join(self.moved, 'cg')
        if not os.path.exists(self.moved):    os.makedirs(self.moved)
        if not os.path.exists(self.movedcc):  os.makedirs(self.movedcc)
        if not os.path.exists(self.movedcg):  os.makedirs(self.movedcg)

        # Carpetas para los centroides y centros de gravedad originales
        self.ccpath = os.path.join(self.base, 'cc')
        self.cgpath = os.path.join(self.base, 'cg')
        if not os.path.exists(self.ccpath):  os.makedirs(self.ccpath)
        if not os.path.exists(self.cgpath):  os.makedirs(self.cgpath)

        # Diccionario principal: una entrada por individuo (grupo de puntos)
        # Estructura de cada entrada:
        #   {'centroide': (x, y),   ← centro geométrico (media de máx y mín)
        #    'ceg':       (x, y),   ← centro de gravedad (media aritmética)
        #    'grados':    int,      ← ángulo de rotación aleatorio
        #    'xoff':      float,    ← desplazamiento en X
        #    'yoff':      float}    ← desplazamiento en Y
        self.individuos = {}

        print('shape:', self.pointshp, '\nmarco: ', self.marco, '\nsalida:', self.moved)

    # -------------------------------------------------------------------------
    def get_extent_shapely(self, k):
        """
        Elige aleatoriamente un cuadrante del marco (NW, NE, SW, SE) y calcula
        un desplazamiento aleatorio que lleve el centro de gravedad del individuo
        hacia ese cuadrante, sin salirse del marco.

        El desplazamiento se elige al azar entre 0 y la distancia máxima posible
        en cada eje hacia la esquina del cuadrante elegido.

        Llama a self.check() para verificar que el punto desplazado cae dentro
        del marco; si no, vuelve a llamarse a sí mismo recursivamente.
        """
        # Abrimos el marco y extraemos sus límites (bounding box)
        shp      = fiona.open(self.marco)
        feature1 = next(iter(shp))
        a1       = Polygon(feature1['geometry']['coordinates'][0])
        Oeste, Este, Norte, Sur = a1.bounds[0], a1.bounds[2], a1.bounds[3], a1.bounds[1]

        # Elegimos un cuadrante al azar y obtenemos la esquina correspondiente
        cuadrante = random.choice(['NW', 'NE', 'SW', 'SE'])
        print('Individuo', k, 'se desplaza al', cuadrante)
        esquinas = {'NW': (Oeste, Norte), 'NE': (Este, Norte),
                    'SW': (Oeste, Sur),   'SE': (Este, Sur)}
        self.individuos[k]['bounds'] = esquinas[cuadrante]

        # Calculamos la diferencia entre la esquina y el centro de gravedad
        # distxy[0] → diferencia en X,  distxy[1] → diferencia en Y
        bounds = self.individuos[k]['bounds']
        ceg    = self.individuos[k]['ceg']
        distxy = tuple(x - y for x, y in zip(bounds, ceg))

        # El desplazamiento aleatorio debe ir en la dirección correcta:
        # si la diferencia es negativa, el offset va de distxy a 0 (hacia la izquierda/abajo)
        # si es positiva, va de 0 a distxy (hacia la derecha/arriba)
        offx = round(random.uniform(distxy[0], 0) if distxy[0] < 0
                     else random.uniform(0, distxy[0]), 2)
        offy = round(random.uniform(distxy[1], 0) if distxy[1] < 0
                     else random.uniform(0, distxy[1]), 2)

        print('llamando a self.check', ceg, k, offx, offy)
        self.check(ceg, k, offx, offy)

    # -------------------------------------------------------------------------
    def centroids(self):
        """
        Lee todos los puntos del shapefile y calcula para cada grupo (individuo):
          - Centro de gravedad (ceg): media aritmética de todas las coordenadas
          - Centroide geométrico: media del máximo y mínimo de x e y

        Luego asigna a cada individuo:
          - Un ángulo de rotación aleatorio entre 0 y 360°
          - Un desplazamiento (offx, offy) calculado por get_extent_shapely()

        Finalmente escribe los centroides y centros de gravedad originales
        a shapefiles en las carpetas cc/ y cg/.
        """
        point = fiona.open(self.pointshp)

        # Obtenemos el conjunto de IDs únicos de los grupos de puntos
        especies  = set([i['properties']['ID_progres'] for i in point.values()])
        lespecies = sorted(especies)

        # Creamos un diccionario para acumular las coordenadas x e y de cada grupo
        # Estructura: {id: {'x': [x1, x2, ...], 'y': [y1, y2, ...]}}
        d = {k: {'x': [], 'y': []} for k in lespecies}

        # Recorremos todos los puntos y agrupamos sus coordenadas por ID
        for i in point.values():
            id_grupo = i['properties']['ID_progres']
            d[id_grupo]['x'].append(i['geometry']['coordinates'][0])
            d[id_grupo]['y'].append(i['geometry']['coordinates'][1])

        # Inicializamos el diccionario de individuos con valores vacíos
        for k in d:
            self.individuos[k] = {'centroide': (), 'ceg': (), 'grados': 0,
                                  'xoff': 0, 'yoff': 0}

        # Calculamos el centro de gravedad y el centroide geométrico de cada grupo
        for k, v in d.items():
            # *** EJERCICIO 1 ***
            # El centro de gravedad (ceg) es la media aritmética de todas las
            # coordenadas x e y del grupo → usa np.mean sobre las listas d[k]['x'] y d[k]['y']
            self.individuos[k]['ceg'] = # TU CÓDIGO AQUÍ

            # El centroide geométrico es la media del máximo y el mínimo de x e y
            # (equivale al centro del bounding box del grupo)
            self.individuos[k]['centroide'] = (
                (max(d[k]['x']) + min(d[k]['x'])) / 2,
                (max(d[k]['y']) + min(d[k]['y'])) / 2
            )

        # Asignamos un ángulo de rotación aleatorio a cada individuo
        for k in lespecies:
            self.individuos[k]['grados'] = random.randint(0, 360)

        # Calculamos el desplazamiento para cada individuo (llama a get_extent_shapely)
        for k in lespecies:
            self.get_extent_shapely(k)

        # Escribimos los centroides y centros de gravedad originales a shapefile
        schema = {'geometry': 'Point', 'properties': {'id': 'int'}}
        for k in self.individuos:
            # Centroide geométrico (cc)
            shp_cc = os.path.join(self.ccpath, str(k) + '_cc.shp')
            with fiona.open(shp_cc, 'w', crs=point.crs,
                            driver='ESRI Shapefile', schema=schema) as cshp:
                cshp.write({'geometry':   mapping(Point(self.individuos[k]['centroide'])),
                            'properties': {'id': k}})

            # Centro de gravedad (cg)
            shp_cg = os.path.join(self.cgpath, str(k) + '_cg.shp')
            with fiona.open(shp_cg, 'w', crs=point.crs,
                            driver='ESRI Shapefile', schema=schema) as cshp:
                cshp.write({'geometry':   mapping(Point(self.individuos[k]['ceg'])),
                            'properties': {'id': k}})

        print(self.individuos)

    # -------------------------------------------------------------------------
    def check(self, centroid, k, offx, offy):
        """
        Comprueba que el centro de gravedad del individuo, una vez trasladado
        con (offx, offy), cae dentro del polígono marco.

        Si el punto cae dentro  → guarda offx y offy en self.individuos[k].
        Si el punto cae fuera   → vuelve a llamar a get_extent_shapely() para
                                  elegir un nuevo desplazamiento.
        """
        print('comprobando geometria en self.check')
        centroid = Point(centroid)

        # *** EJERCICIO 2 ***
        # Traslada el punto centroid (offx metros en X, offy metros en Y)
        # usando shapely.affinity.translate
        cc = # TU CÓDIGO AQUÍ

        # Comprobamos si el punto trasladado cae dentro del marco
        marco = fiona.open(self.marco)
        c = 0
        for feature in marco:
            mc = Polygon(feature['geometry']['coordinates'][0])
            if mc.contains(cc):
                c += 1
                print('Punto dentro del marco')

        if c > 0:
            # El punto está dentro → aceptamos el desplazamiento
            self.individuos[k]['xoff'] = offx
            self.individuos[k]['yoff'] = offy
        else:
            # El punto está fuera → recalculamos con un nuevo cuadrante aleatorio
            print('Punto fuera del marco')
            self.get_extent_shapely(k)

    # -------------------------------------------------------------------------
    def rotate_c(self):
        """
        Aplica la rotación y la traslación a cada punto del shapefile original
        y escribe el resultado en un nuevo shapefile.

        Para cada punto:
          1. Lo rotamos sobre el centro de gravedad de su grupo con el ángulo
             aleatorio asignado en centroids() → affinity.rotate()
          2. Lo trasladamos con el offset calculado en get_extent_shapely()
             → affinity.translate()

        También mueve los shapefiles de centroides y centros de gravedad con
        la misma traslación (sin rotación, para mantener su posición relativa).
        """
        # --- Procesamos los puntos originales ---
        with fiona.open(self.pointshp, 'r') as input:
            schema = input.schema.copy()   # mismo schema que el original
            coords = from_epsg(25830)      # CRS de salida: ETRS89 UTM 30N

            with fiona.open(os.path.join(self.moved, self.name + '_rm.shp'), 'w',
                            'ESRI Shapefile', schema, coords) as output:
                for elem in input:
                    idp = elem['properties']['ID_progres']
                    p   = Point(elem['geometry']['coordinates'])

                    # *** EJERCICIO 3 ***
                    # Paso 1: rota el punto p alrededor del centro de gravedad
                    # del individuo (self.individuos[idp]['ceg']), usando el ángulo
                    # en grados almacenado en self.individuos[idp]['grados'].
                    # Pista: affinity.rotate(geom, angle, origin, use_radians=False)
                    rp = # TU CÓDIGO AQUÍ  (affinity.rotate)

                    # Paso 2: traslada el punto rotado con los offsets xoff e yoff
                    # del individuo para llevarlo al cuadrante elegido.
                    # Pista: affinity.translate(geom, xoff, yoff)
                    rpt = # TU CÓDIGO AQUÍ  (affinity.translate)

                    output.write({'properties': elem['properties'],
                                  'geometry':   mapping(rpt)})

        # --- Movemos también los shapefiles de centros de gravedad (cg) ---
        # Solo necesitamos la traslación (ya no rotamos los centroides)
        cglist = [os.path.join(self.cgpath, f) for f in os.listdir(self.cgpath)
                  if f.endswith('.shp') and 'rm' not in f]
        for cg in cglist:
            with fiona.open(cg, 'r') as input:
                schema = input.schema.copy()
                coords = from_epsg(25830)
                out_path = os.path.join(self.movedcg,
                                        os.path.split(cg)[1][:-4] + '_rm.shp')
                with fiona.open(out_path, 'w', 'ESRI Shapefile', schema, coords) as output:
                    for elem in input:
                        idp = elem['properties']['id']
                        p   = Point(elem['geometry']['coordinates'])
                        pt  = affinity.translate(p,
                                                 self.individuos[idp]['xoff'],
                                                 self.individuos[idp]['yoff'])
                        output.write({'properties': elem['properties'],
                                      'geometry':   mapping(pt)})

        # --- Movemos también los shapefiles de centroides geométricos (cc) ---
        cclist = [os.path.join(self.ccpath, f) for f in os.listdir(self.ccpath)
                  if f.endswith('.shp') and 'rm' not in f]
        for cc in cclist:
            with fiona.open(cc, 'r') as input:
                schema = input.schema.copy()
                coords = from_epsg(25830)
                out_path = os.path.join(self.movedcc,
                                        os.path.split(cc)[1][:-4] + '_rm.shp')
                with fiona.open(out_path, 'w', 'ESRI Shapefile', schema, coords) as output:
                    for elem in input:
                        idp = elem['properties']['id']
                        p   = Point(elem['geometry']['coordinates'])
                        pt  = affinity.translate(p,
                                                 self.individuos[idp]['xoff'],
                                                 self.individuos[idp]['yoff'])
                        output.write({'properties': elem['properties'],
                                      'geometry':   mapping(pt)})

    # -------------------------------------------------------------------------
    def run(self):
        """
        Ejecuta el flujo completo:
          1. centroids() → lee los puntos, calcula centros y desplazamientos
          2. rotate_c()  → aplica rotación + traslación y escribe los resultados
        """
        self.centroids()
        self.rotate_c()
