import os
import os.path

from PyQt5.QtWidgets import QMenu
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.core import QgsApplication

from .gui.about_dialog import AboutDialog
from .gui.geo_easin_dockwidget import GeoEASINDockWidget
from .processing_tools.processing_tools_provider import ProcessingToolsProvider


class GeoEASIN:
    def __init__(self, iface):

        self.iface = iface
        self.dlgAbout = AboutDialog()
        self.plugin_dir = os.path.dirname(__file__)

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

        ## Crea objeto menu
        self.actions = []



        self.toolbar = self.iface.addToolBar(u'GeoEASIN')
        self.toolbar.setObjectName(u'GeoEASIN')

        self.pluginIsActive = False
        self.dockwidget = None
        self.provider = None
        self.first_start = None



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

    def initGui(self):
        # create action that will start plugin configuration

        ## Añade el menu al menú de Complementos

        self.menuGeoEASIN = QMenu(self.tr(u'&GeoEASIN'), self.iface.mainWindow().menuBar())
        self.iface.pluginMenu().addMenu(self.menuGeoEASIN)

        if self.menuGeoEASIN:
            self.action01_search = self.menuGeoEASIN.addAction("&Search by Specie", self.open_dock_search)
            self.actions.append(self.action01_search)

            self.subMenu1 = self.menuGeoEASIN.addMenu('&Add &maps')
            self.action11_addOSM = self.subMenu1.addAction("OSM...", self.open_dlg_about)
            self.action12_addOSM = self.subMenu1.addAction("WMS Copernicus rivers", self.open_dlg_about)

            self.actions.append(self.action12_addOSM)
            self.actions.append(self.action12_addOSM)

            self.action02_about = self.menuGeoEASIN.addAction("&About", self.open_dlg_about)
            self.actions.append(self.action02_about)



        self.initProcessing()

    # --------------------------------------------------------------------------

    def initProcessing(self):
        self.provider = ProcessingToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False

    def unload(self):

        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&GeoEASIN'), action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

        QgsApplication.processingRegistry().removeProvider(self.provider)

    # --------------------------------------------------------------------------

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
