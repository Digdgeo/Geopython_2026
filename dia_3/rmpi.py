
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

        self.pointshp = pointshp
        self.marco = marco
        self.base = os.path.split(self.pointshp)[0]
        self.name = os.path.split(self.pointshp)[1][:-4]
        self.moved = os.path.join(self.base, 'moved')
        self.movedcc = os.path.join(self.moved, 'cc')
        self.movedcg = os.path.join(self.moved, 'cg')
        if not os.path.exists(self.moved):
            os.makedirs(self.moved)
        if not os.path.exists(self.movedcc):
            os.makedirs(self.movedcc)
        if not os.path.exists(self.movedcg):
            os.makedirs(self.movedcg)
        self.moves = {0: 'NW', 1: 'NE', 2: 'SW', 3: 'SE'}
        self.ccpath = os.path.join(self.base, 'cc')
        if not os.path.exists(self.ccpath):
            os.makedirs(self.ccpath)
        self.cgpath = os.path.join(self.base, 'cg')
        if not os.path.exists(self.cgpath):
            os.makedirs(self.cgpath)
        # diccionario con offset x/y, centroides y ángulo de rotación de cada individuo
        self.individuos = {}

        print('shape:', self.pointshp, '\nmarco: ', self.marco, '\nsalida:', self.moved)

    def get_extent_shapely(self, k):
        """Elige un cuadrante aleatorio y calcula el desplazamiento hacia él."""

        shp = fiona.open(self.marco)
        feature1 = next(iter(shp))
        geom1 = feature1['geometry']
        a1 = Polygon(geom1['coordinates'][0])
        Oeste, Este, Norte, Sur = a1.bounds[0], a1.bounds[2], a1.bounds[3], a1.bounds[1]

        moves = ['NW', 'NE', 'SW', 'SE']
        cuadrante = moves[random.randrange(4)]
        print('Individuo', k, 'se desplaza al', cuadrante)
        move = {'NW': (Oeste, Norte), 'NE': (Este, Norte), 'SW': (Oeste, Sur), 'SE': (Este, Sur)}
        self.individuos[k]['bounds'] = move[cuadrante]
        bounds = self.individuos[k]['bounds']
        ceg = self.individuos[k]['ceg']
        distxy = tuple(x - y for x, y in zip(bounds, ceg))

        if distxy[0] < 0:
            offx = round(random.uniform(distxy[0], 0), 2)
        else:
            offx = round(random.uniform(0, distxy[0]), 2)
        if distxy[1] < 0:
            offy = round(random.uniform(distxy[1], 0), 2)
        else:
            offy = round(random.uniform(0, distxy[1]), 2)

        print('llamando a self.check', ceg, k, offx, offy)
        self.check(ceg, k, offx, offy)

    def centroids(self):
        """Calcula centroides y centros de gravedad de cada grupo de puntos."""

        point = fiona.open(self.pointshp)
        especies = set([i['properties']['ID_progres'] for i in point.values()])
        lespecies = sorted([i for i in especies])

        d = {}
        for k in lespecies:
            d[k] = {'x': [], 'y': []}

        for i in point.values():
            d[i['properties']['ID_progres']]['x'].append(i['geometry']['coordinates'][0])
            d[i['properties']['ID_progres']]['y'].append(i['geometry']['coordinates'][1])

        for k, v in d.items():
            self.individuos[k] = {'centroide': (), 'ceg': (), 'grados': 0, 'xoff': 0, 'yoff': 0}

        for k, v in d.items():
            # *** EJERCICIO 1 ***
            # Calcula el centro de gravedad (media aritmética de x e y) con np.mean
            # y el centroide geométrico (media de máx y mín de x e y)
            self.individuos[k]['ceg'] = # TU CÓDIGO AQUÍ
            self.individuos[k]['centroide'] = (((max(d[k]['x']) + min(d[k]['x'])) / 2),
                                               ((max(d[k]['y']) + min(d[k]['y'])) / 2))

        for k in lespecies:
            grados = random.randint(0, 360)
            self.individuos[k]['grados'] = grados

        for k in lespecies:
            self.get_extent_shapely(k)

        schema = {'geometry': 'Point', 'properties': {'id': 'int'}}
        for k, v in self.individuos.items():
            shp = os.path.join(self.ccpath, str(k) + '_cc.shp')
            centroid = Point(self.individuos[k]['centroide'])
            with fiona.open(shp, 'w', crs=point.crs, driver='ESRI Shapefile', schema=schema) as cshp:
                cshp.write({'geometry': mapping(centroid), 'properties': {'id': k}})

            shpcg = os.path.join(self.cgpath, str(k) + '_cg.shp')
            centroid = Point(self.individuos[k]['ceg'])
            with fiona.open(shpcg, 'w', crs=point.crs, driver='ESRI Shapefile', schema=schema) as cshp:
                cshp.write({'geometry': mapping(centroid), 'properties': {'id': k}})

        print(self.individuos)

    def check(self, centroid, k, offx, offy):
        """Comprueba que el centroide trasladado cae dentro del marco."""

        print('comprobando geometria en self.check')
        centroid = Point(centroid)

        # *** EJERCICIO 2 ***
        # Traslada el punto centroid aplicando los offsets offx y offy con affinity.translate
        cc = # TU CÓDIGO AQUÍ

        marco = fiona.open(self.marco)
        c = 0
        for i in marco:
            mc = Polygon(i['geometry']['coordinates'][0])
            if mc.contains(cc):
                c += 1
                print('Punto dentro del marco')

        if c > 0:
            self.individuos[k]['xoff'], self.individuos[k]['yoff'] = offx, offy
        else:
            print('Punto fuera del marco')
            self.get_extent_shapely(k)

    def rotate_c(self):
        """Rota y traslada todos los puntos según los parámetros calculados."""

        with fiona.open(self.pointshp, 'r') as input:
            schema = input.schema.copy()
            coords = from_epsg(25830)

            with fiona.open(os.path.join(self.moved, self.name + '_rm.shp'), 'w',
                            'ESRI Shapefile', schema, coords) as output:
                for elem in input:
                    idp = elem['properties']['ID_progres']
                    p = Point(elem['geometry']['coordinates'])

                    # *** EJERCICIO 3 ***
                    # Primero rota p sobre el centro de gravedad del individuo (self.individuos[idp]['ceg'])
                    # usando el ángulo en grados almacenado en self.individuos[idp]['grados']
                    # Luego traslada el punto rotado con los offsets xoff e yoff del individuo
                    rp = # TU CÓDIGO AQUÍ  (affinity.rotate)
                    rpt = # TU CÓDIGO AQUÍ  (affinity.translate)

                    output.write({'properties': elem['properties'], 'geometry': mapping(rpt)})

        cglist = [os.path.join(self.cgpath, i) for i in os.listdir(self.cgpath)
                  if i.endswith('.shp') and 'rm' not in i]
        cclist = [os.path.join(self.ccpath, i) for i in os.listdir(self.ccpath)
                  if i.endswith('.shp') and 'rm' not in i]

        for cg in cglist:
            with fiona.open(cg, 'r') as input:
                schema = input.schema.copy()
                coords = from_epsg(25830)
                with fiona.open(os.path.join(self.movedcg, os.path.split(cg)[1][:-4] + '_rm.shp'), 'w',
                                'ESRI Shapefile', schema, coords) as output:
                    for elem in input:
                        idp = elem['properties']['id']
                        p = Point(elem['geometry']['coordinates'])
                        pt = affinity.translate(p, self.individuos[idp]['xoff'], self.individuos[idp]['yoff'])
                        output.write({'properties': elem['properties'], 'geometry': mapping(pt)})

        for cc in cclist:
            with fiona.open(cc, 'r') as input:
                schema = input.schema.copy()
                coords = from_epsg(25830)
                with fiona.open(os.path.join(self.movedcc, os.path.split(cc)[1][:-4] + '_rm.shp'), 'w',
                                'ESRI Shapefile', schema, coords) as output:
                    for elem in input:
                        idp = elem['properties']['id']
                        p = Point(elem['geometry']['coordinates'])
                        pt = affinity.translate(p, self.individuos[idp]['xoff'], self.individuos[idp]['yoff'])
                        output.write({'properties': elem['properties'], 'geometry': mapping(pt)})

    def run(self):
        self.centroids()
        self.rotate_c()
