
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
        t0 = time.time()

        self.shape = shape
        self.shp = fiona.open(shape)
        self.csr = self.shp.crs
        self.perp = perp
        self.path = os.path.split(shape)[0]
        self.shape_name = os.path.split(shape)[1][:-4]
        self.npath = os.path.join(self.path, 'lines')
        print(self.npath)
        os.makedirs(self.npath, exist_ok=True)

        self.din = {}       # líneas interiores más largas
        self.dout = {}      # líneas exteriores más largas
        self.dperp = {}     # perpendiculares en el punto medio
        self.ext = ext
        self.max_perp = {}  # perpendicular máxima
        self.perp_max = perp_max

        self.d = {i['properties']['id']: [] for i in self.shp}    # vértices por polígono
        self.dpg = {i['properties']['id']: [] for i in self.shp}  # polígonos Shapely

        nshape = 0
        nvertex = 0

        self.outdin = os.path.join(self.npath, self.shape_name + '_int.shp')
        self.outout = os.path.join(self.npath, self.shape_name + '_out.shp')
        self.outperp = os.path.join(self.npath, self.shape_name + '_perpendicular.shp')
        self.outmaxperp = os.path.join(self.npath, self.shape_name + '_max_perpendicular.shp')

        print(self.outdin, "\n", self.outmaxperp)

        for e in self.shp:
            nshape += 1
            id_ = e['properties']['id']
            coords = e['geometry']['coordinates'][0]
            self.dpg[id_] = Polygon(e['geometry']['coordinates'][0])
            for pt in coords:
                nvertex += 1
                self.d[id_].append(Point(pt))

        print('Se han importado', nshape, 'poligonos y', nvertex - nshape, 'vertices en', time.time() - t0, 'segundos')

    def get_lines(self):
        """Calcula la línea más larga interior y exterior para cada polígono."""

        t0 = time.time()
        counter = 0

        for k, v in self.d.items():

            m_in = 0
            m_out = 0

            print('\n########################################Haciendo el ID:', k, '\n')

            for n, e in enumerate(v):
                for nn, ee in enumerate(v):
                    if nn > n:
                        counter += 1
                        l = e.distance(ee)

                        if l > m_in:
                            # *** EJERCICIO 1 ***
                            # Crea una LineString conectando los dos puntos e y ee
                            line = # TU CÓDIGO AQUÍ

                            # *** EJERCICIO 2 ***
                            # Comprueba si la línea está completamente dentro del polígono
                            if # TU CÓDIGO AQUÍ:
                                self.din[k] = line
                                m_in = l

                            elif line.intersects(self.dpg[k]):
                                if l > m_out:
                                    self.dout[k] = line
                                    m_out = l

        print('Se han recorrido', counter, 'vertices en', time.time() - t0, 'segundos\n')

    def write_lines(self):
        """Escribe las líneas interiores y exteriores a shapefiles."""

        schema = {
            'geometry': 'LineString',
            'crs': self.shp.crs,
            'properties': {'id': 'int', 'length': 'float'}
        }

        with fiona.open(self.outdin, 'w', crs=self.csr, driver='ESRI Shapefile', schema=schema) as c:
            for k, v in self.din.items():
                c.write({
                    'geometry': mapping(v),
                    'properties': {'id': k, 'length': v.length}})

        if self.ext == True:
            with fiona.open(self.outout, 'w', crs=self.csr, driver='ESRI Shapefile', schema=schema) as c:
                for k, v in self.dout.items():
                    c.write({
                        'geometry': mapping(v),
                        'properties': {'id': k, 'length': v.length}})

    def get_perpendicular(self):
        """Calcula la perpendicular en el punto medio de la línea interior más larga."""

        for k, v in self.din.items():
            mid_point = v.interpolate(0.5, normalized=True)

            pt1 = list(v.coords)[0]
            pt2 = list(v.coords)[1]

            x_diff = pt2[0] - pt1[0]
            y_diff = pt2[1] - pt1[1]
            bearing = math.degrees(math.atan2(y_diff, x_diff))

            nangle = bearing - 90
            nbearing = math.radians(nangle)
            x = list(mid_point.coords)[0][0] + v.length * math.cos(nbearing)
            y = list(mid_point.coords)[0][1] + v.length * math.sin(nbearing)

            bearing = math.radians(bearing + 90)
            nx = list(mid_point.coords)[0][0] + v.length * math.cos(bearing)
            ny = list(mid_point.coords)[0][1] + v.length * math.sin(bearing)

            p1 = Point(x, y)
            p2 = Point(nx, ny)
            perpline = LineString((p1, p2))

            # *** EJERCICIO 3 ***
            # Calcula la intersección de perpline con el polígono self.dpg[k]
            intersection = # TU CÓDIGO AQUÍ
            self.dperp[k] = intersection

            if self.perp_max == True:
                md = 0
                dist = v.length / 100
                for i in range(-50, 51):
                    mperp = perpline.parallel_offset(dist * i)
                    mintersection = mperp.intersection(self.dpg[k])
                    if mintersection.length > md:
                        self.max_perp[k] = mintersection
                        md = mintersection.length

    def write_perp_lines(self, dict_, out):
        """Escribe líneas perpendiculares a un shapefile."""

        schema = {
            'geometry': 'LineString',
            'crs': self.csr,
            'properties': {'id': 'int', 'length': 'float'}
        }

        print(out)
        with fiona.open(out, 'w', crs=self.csr, driver='ESRI Shapefile', schema=schema) as c:
            for k, v in dict_.items():
                c.write({
                    'geometry': mapping(v),
                    'properties': {'id': k, 'length': v.length}})

    def run(self):
        """Ejecuta todos los pasos en orden."""

        self.get_lines()
        self.write_lines()
        if self.perp == True:
            self.get_perpendicular()
            self.write_perp_lines(self.dperp, self.outperp)
            if self.perp_max == True:
                self.write_perp_lines(self.max_perp, self.outmaxperp)
