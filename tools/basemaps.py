import os

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject

UPPATH = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
CURR_PATH = UPPATH(__file__, 2)


def addTileLayer():
    urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
    raster_layer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print('invalid layer')


def addWMSCopernicusRiver():
    """Def"""
    layer_name = 'Copernicus River Basine'
    url = 'https://image.discomap.eea.europa.eu/arcgis/services/EUHydro/RiverBasine/MapServer/WMSServer'
    layers = 'STRAHLE_Levels_of_River38734'
    styles = 'default'
    format = 'image/png'
    crs = 'EPSG:4326'
    urlWithParams = f'url={url}&layers={layers}&styles={styles}&format={format}&crs={crs}'
    raster_layer = QgsRasterLayer(urlWithParams, layer_name, 'wms')
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print('invalid layer')


def addWMSCopernicusCLC2018():
    """Def"""
    layer_name = 'CLC2018'
    url = 'https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC2018_WM/MapServer/WMSServer'
    layers = '12&layers=13'
    styles = '&styles'
    format = 'image/png'
    crs = 'EPSG:4326'
    urlWithParams = f'url={url}&layers={layers}&styles={styles}&format={format}&crs={crs}'
    raster_layer = QgsRasterLayer(urlWithParams, layer_name, 'wms')
    print(urlWithParams)
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print('invalid layer')


def addWMSCopernicusNatura2000N2k2018():
    """Def"""
    layer_name = 'Natura2000_2018 '
    url = 'https://image.discomap.eea.europa.eu/arcgis/services/Natura2000/N2K_2018/MapServer/WMSServer'
    layers = '0&layers=1'
    styles = '&styles'
    format = 'image/png'
    crs = 'EPSG:4326'
    urlWithParams = f'url={url}&layers={layers}&styles={styles}&format={format}&crs={crs}'
    raster_layer = QgsRasterLayer(urlWithParams, layer_name, 'wms')
    print(urlWithParams)
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print('invalid layer')


def addCountriesLayer():
    # get the path to the shapefile e.g. /home/project/data/ports.shp
    plugin_dir = os.path.dirname(__file__)

    layer = "data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

    path_layer = os.path.join(CURR_PATH, layer)

    virtual_layer = QgsVectorLayer(path_layer, "ne_10m_admin_0_countries", "ogr")
    if not virtual_layer.isValid():
        print("Layer failed to load!")
    else:
        QgsProject.instance().addMapLayer(virtual_layer)
