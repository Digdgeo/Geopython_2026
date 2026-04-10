from pathlib import Path
import numpy as np
import rasterio


class Landsat:
    """
    Clase para trabajar con escenas Landsat procesadas.

    Parameters
    ----------
    scene_path : str or Path
        Ruta a la carpeta de la escena (nivel ori).

    Attributes
    ----------
    scene_name : str       Nombre de la escena (nombre de la carpeta)
    ori        : Path      Directorio padre donde cuelga la escena
    dat        : Path      Carpeta de datos auxiliares  (ori/dat/)
    pro        : Path      Carpeta de productos          (ori/pro/)
    pro_scene  : Path      Carpeta de salida de la escena (ori/pro/scene_name/)

    blue, green, red,      Rutas a cada banda espectral (.tif)
    nir, swir1, swir2

    fmask      : Path      Máscara de nubes Fmask
    hillshade  : Path      Hillshade
    dmtl       : dict      MTL.txt parseado como diccionario anidado
                           (vacío si no se encuentra el archivo)

    Examples
    --------
    >>> from landsat import Landsat
    >>> ls = Landsat('/ruta/a/20250327l9oli202_34')
    >>> ls.ndvi()
    >>> ls.mndwi()
    """

    def __init__(self, scene_path):

        self.scene_path = Path(scene_path)
        self.scene_name = self.scene_path.name

        # ------------------------------------------------------------------
        # Rutas de trabajo
        # ------------------------------------------------------------------
        self.ori       = self.scene_path.parent
        self.dat       = self.ori / 'dat'
        self.pro       = self.ori / 'pro'
        self.pro_scene = self.pro / self.scene_name

        for folder in [self.dat, self.pro, self.pro_scene]:
            folder.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------------
        # Bandas espectrales
        # ------------------------------------------------------------------
        self.blue  = self.scene_path / f'{self.scene_name}_grn2_blue_b2.tif'
        self.green = self.scene_path / f'{self.scene_name}_grn2_green_b3.tif'
        self.red   = self.scene_path / f'{self.scene_name}_grn2_red_b4.tif'
        self.nir   = self.scene_path / f'{self.scene_name}_grn2_nir_b5.tif'
        self.swir1 = self.scene_path / f'{self.scene_name}_grn2_swir1_b6.tif'
        self.swir2 = self.scene_path / f'{self.scene_name}_grn2_swir2_b7.tif'

        # ------------------------------------------------------------------
        # Capas auxiliares
        # ------------------------------------------------------------------
        self.fmask     = self.scene_path / f'{self.scene_name}_fmask.tif'
        self.hillshade = self.scene_path / 'hillshade.tif'

        # ------------------------------------------------------------------
        # MTL como diccionario
        # ------------------------------------------------------------------
        self.dmtl = self._load_mtl()

    # ----------------------------------------------------------------------
    # MTL
    # ----------------------------------------------------------------------

    def _load_mtl(self):
        """Busca y parsea el MTL.txt de la escena."""
        candidates = (
            list(self.scene_path.glob('*MTL.txt')) +
            list(self.scene_path.glob('*mtl.txt'))
        )
        if not candidates:
            print(f"[INFO] MTL.txt no encontrado en {self.scene_path}")
            return {}
        return self._parse_mtl(candidates[0])

    def _parse_mtl(self, mtl_path):
        """Parsea un MTL.txt estándar de Landsat en un diccionario anidado."""
        result = {}
        stack  = [result]

        with open(mtl_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('GROUP'):
                    name      = line.split('=', 1)[1].strip()
                    new_group = {}
                    stack[-1][name] = new_group
                    stack.append(new_group)
                elif line.startswith('END_GROUP'):
                    stack.pop()
                elif '=' in line and not line.startswith('END'):
                    key, val    = line.split('=', 1)
                    stack[-1][key.strip()] = val.strip().strip('"')

        return result

    # ----------------------------------------------------------------------
    # Utilidades internas
    # ----------------------------------------------------------------------

    def _read_band(self, band_path):
        """Lee una banda raster y devuelve (array float32, profile).
        Los píxeles con valor 0 se convierten a NaN."""
        with rasterio.open(band_path) as src:
            data    = src.read(1).astype('float32')
            profile = src.profile.copy()
        data[data == 0] = np.nan
        return data, profile

    def _save_index(self, array, profile, filename):
        """Guarda un array como GeoTIFF float32 en pro/scene_name/."""
        out_path = self.pro_scene / filename
        profile.update(dtype='float32', count=1, nodata=np.nan)
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(array, 1)
        print(f"  -> Guardado: {out_path}")
        return out_path

    # ----------------------------------------------------------------------
    # Índices espectrales
    # ----------------------------------------------------------------------

    def ndvi(self):
        """
        Calcula el NDVI: (NIR - Red) / (NIR + Red)
        y guarda el resultado en pro/scene_name/{scene}_ndvi.tif

        Returns
        -------
        Path  Ruta al archivo generado
        """
        print(f"Calculando NDVI para {self.scene_name}...")
        nir, profile = self._read_band(self.nir)
        red, _       = self._read_band(self.red)

        with np.errstate(invalid='ignore', divide='ignore'):
            index = (nir - red) / (nir + red)

        return self._save_index(index, profile, f'{self.scene_name}_ndvi.tif')

    def mndwi(self):
        """
        Calcula el MNDWI: (Green - SWIR1) / (Green + SWIR1)
        y guarda el resultado en pro/scene_name/{scene}_mndwi.tif

        Returns
        -------
        Path  Ruta al archivo generado
        """
        print(f"Calculando MNDWI para {self.scene_name}...")
        green, profile = self._read_band(self.green)
        swir1, _       = self._read_band(self.swir1)

        with np.errstate(invalid='ignore', divide='ignore'):
            index = (green - swir1) / (green + swir1)

        return self._save_index(index, profile, f'{self.scene_name}_mndwi.tif')

    # ----------------------------------------------------------------------
    # Representación
    # ----------------------------------------------------------------------

    def __repr__(self):
        bands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
        band_status = {b: '✓' if getattr(self, b).exists() else '✗' for b in bands}
        bands_str   = '  '.join(f"{b}:{s}" for b, s in band_status.items())

        return (
            f"Landsat('{self.scene_name}')\n"
            f"  ori:       {self.ori}\n"
            f"  dat:       {self.dat}\n"
            f"  pro:       {self.pro}\n"
            f"  pro_scene: {self.pro_scene}\n"
            f"  bandas:    {bands_str}\n"
            f"  fmask:     {'✓' if self.fmask.exists() else '✗'}  "
            f"hillshade: {'✓' if self.hillshade.exists() else '✗'}\n"
            f"  dmtl:      {'cargado (' + str(len(self.dmtl)) + ' grupos)' if self.dmtl else 'no disponible'}"
        )
