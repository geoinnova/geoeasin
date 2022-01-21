# -*- coding: utf-8 -*-
"""

"""

import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QPixmap

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'about_dialog.ui'))

UPPATH = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
CURR_PATH = UPPATH(__file__, 2)


class AboutDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        self.logo = QPixmap(os.path.join(CURR_PATH, 'img/geoeasinicon.png'))
        self.logo = self.logo.scaledToWidth(30)
        self.lblLogo.setPixmap(self.logo)
        self.tbInfo.setHtml(self.get_about_text())
        self.tbLicense.setPlainText(self.get_license_text())

    def get_about_text(self):
        return self.tr(
            '<p>Web services downloader and tools to analyze the European Alien Species Information Network data (EASIN).'
            '<a href="https://easin.jrc.ec.europa.eu/easin/Services/RestfulWebService">+Info</a></p>'
            '<p><strong>Developers:</strong> <a href="https://geoinnova.org/">Patricio Soriano (Geoinnova.org)</a>, <a href="http://www.gisandbeers.com/roberto-aspectos-profesionales-en-sig/">Roberto Matellanes</a></p>'
            '<p><strong>Homepage:</strong> <a href="https://geoinnova.org/plugin/geoeasin">Homepage</a></p>'
            '<p><strong>Issue tracker:</strong> <a href="https://github.com/geoinnova/geoeasin/issues">GitHub</a></p>'
            '<p><strong>Source code:</strong> <a href="https://github.com/geoinnova/geoeasin">GitHub</a></p>')

    def get_license_text(self):
        with open(os.path.join(CURR_PATH, 'LICENSE')) as f:
            return f.read()
