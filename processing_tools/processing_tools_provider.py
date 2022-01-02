from qgis.core import QgsProcessingProvider

from PyQt5.QtGui import QIcon
from os import path

from .union import UnirInformacionPas


class ProcessingToolsProvider(QgsProcessingProvider):

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(UnirInformacionPas())

    def id(self, *args, **kwargs):
        """The ID of your plugin, used for identifying the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return 'GeoEASIN'

    def name(self, *args, **kwargs):
        """The human friendly name of your plugin in Processing.
        """
        return self.tr('GeoEASIN')

    def icon(self):
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(path.dirname(__file__) + '/img/bug.svg')
