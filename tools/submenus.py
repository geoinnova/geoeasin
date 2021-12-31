from PyQt5.QtWidgets import QMenu


def sayHello():
    print(item, 'Hello')


def sayHello2():
    print('Hello2')


## Crea objeto menu
menuGeoEASIN = QMenu("&GeoEASIN", iface.mainWindow().menuBar())

## Añade el menu al menú de Complementos
iface.pluginMenu().addMenu(menuGeoEASIN)

iconFolder = "E:\\DESARROLLOS\\plugins_qgis\\geoeasin\img\\"

icon_search = self.plugin_dir + '/img/icon.png'

action01_search = menuGeoEASIN.addAction("&Search by Specie", sayHello)
action01_search.setWhatsThis("Configuration for test plugin")
action01_search.setStatusTip("This is status tip")
action01_search.setIcon(QIcon(iconFolder + 'icon.png'))

subMenu1 = menuGeoEASIN.addMenu('&Add &maps')
action11_addOSM = subMenu1.addAction("OSM...", sayHello)
action12_addOSM = subMenu1.addAction("WMS Copernicus rivers", sayHello)

action02_about = menuGeoEASIN.addAction("&About", sayHello)
