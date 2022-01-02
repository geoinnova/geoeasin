# -*- coding: utf-8 -*-
"""

"""
import os
import os.path

from PyQt5.QtWidgets import QMenu
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsProject

from .gui.about_dialog import AboutDialog
from .gui.geo_easin_dockwidget import GeoEASINDockWidget
from .processing_tools.processing_tools_provider import ProcessingToolsProvider


class GeoEASIN:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        # Save reference to the QGIS interface

        self.iface = iface
        self.dlgAbout = AboutDialog()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoEASIN_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.pluginIsActive = False
        self.dockwidget = None
        self.provider = None
        self.first_start = None
        self.menu = self.tr(u'&GeoEASIN')  # Procesing

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoEASIN', message)

    def add_action(self, text, callback, icon_path=None, status_tip=None, whats_this=None):
        """Add a toolbar icon to the toolbar.
        """
        if status_tip is not None:
            icon = QIcon(icon_path)
            action = QAction(icon, text, self.iface.mainWindow())
        else:
            action = QAction(text, self.iface.mainWindow())

        action.triggered.connect(callback)

        # action.triggered.connect( lambda param1: callback(param1))

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        self.actions.append(action)

        return action

    def initGui(self):
        # create action that will start plugin configuration

        icon_search = self.plugin_dir + '/img/bug.svg'
        icon2 = self.plugin_dir + '/img/bola-de-disco.svg'
        icon_about = self.plugin_dir + '/img/about.svg'
        icon_map = self.plugin_dir + '/img/map.svg'
        icon5 = self.plugin_dir + '/img/anadir.svg'


        self.action_search_specie = self.add_action("&Search by specie",
                                                    self.open_dock_search,
                                                    icon_search,
                                                    "Search by specie",
                                                    "Open search by specie panel")

        self.action_about = self.add_action("&About",
                                            self.open_dlg_about,
                                            icon_about,
                                            "About",
                                            "Open About dialog")

        self.action_addOSM = self.add_action("&Add &OSM",
                                             self.addTileLayer,
                                             icon_about)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action_search_specie)
        self.iface.addToolBarIcon(self.action_about)
        # self.iface.addToolBarIcon(self.action2)

        # Add plugins menu items
        self.main_menu = None  # GeoEASIN-plugin-menyn
        self.submenu_basemaps = None  # sub-menu "Add Base Maps"

        # Check if GeoEASIN-menyn existerar och get it
        for child in self.iface.mainWindow().menuBar().children():
            if isinstance(child, QMenu):
                if child.title() == "GeoEASIN":
                    self.main_menu = child

        # If the GeoEASIN menu does not exist, create it!
        self.have_main_menu = False  # indicator that this plugin must not clean up the GeoEASIN menu

        if not self.main_menu:
            self.have_main_menu = True  # indicator that this plugin must clean up the GeoEASIN menu
            self.main_menu = QMenu("GeoEASIN", self.iface.mainWindow().menuBar())
            # menuBar = self.iface.mainWindow().menuBar()
            self.iface.pluginMenu().addMenu(self.main_menu)

        self.main_menu.addAction(self.action_search_specie)

        # check if there is a sub-menu Add Base Maps
        for childchild in self.main_menu.children():
            if isinstance(childchild, QMenu):
                if childchild.title() == "&Add base maps":  # Put here your menu name
                    self.submenu_basemaps = childchild

        # Submenu Base Maps
        if not self.submenu_basemaps:
            self.submenu_basemaps = QMenu(QCoreApplication.translate("GeoEASIN", "Add Base &Maps"))
            self.submenu_basemaps.setIcon(QIcon(icon_map))
            self.main_menu.addMenu(self.submenu_basemaps)
            # self.submenu_basemaps_separator = self.main_menu.addSeparator()

        #  Submenu BaseMaps Actions
        self.submenu_basemaps.addAction(self.action_addOSM)

        #  Action about
        self.main_menu.addAction(self.action_about)

        self.initProcessing()

        print('__initGui_')

    def unload(self):
        # remove the plugin menu item and icon
        for action in self.actions:
            self.iface.removePluginMenu("&GeoEASIN", action)
            self.iface.removeToolBarIcon(action)

        if self.have_main_menu:  # indicator that this plugin must clean up the midvatten menu
            menubar = self.main_menu.parentWidget()
            menubar.removeAction(self.main_menu.menuAction())
            self.main_menu.deleteLater()

        QgsApplication.processingRegistry().removeProvider(self.provider)

    def initProcessing(self):
        self.provider = ProcessingToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False

    def open_dock_search(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING GeoEASIN"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GeoEASINDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def open_dlg_about(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # show the dialog
        self.dlgAbout.show()
        # Run the dialog event loop
        result = self.dlgAbout.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def addTileLayer(self, text):
        urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
        rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')

        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
        else:
            print('invalid layer')

    def addVectorLayer(self):
        # get the path to the shapefile e.g. /home/project/data/ports.shp
        plugin_dir = os.path.dirname(__file__)

        layer = "data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

        path_layer = os.path.join(plugin_dir, layer)

        print(path_layer)

        vlayer = QgsVectorLayer(path_layer, "ne_10m_admin_0_countries", "ogr")
        if not vlayer.isValid():
            print("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(vlayer)
