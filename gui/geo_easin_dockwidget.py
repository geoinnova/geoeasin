# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoEASINDockWidget
                                 A QGIS plugin
 Data downloader from EASIN Geospatial Web Service
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-12-26
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Patricio Soriano. Geoinnova
        email                : patricio.soriano@geoinnova.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import os
from urllib import request

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QColor, QFont
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import Qgis, QgsMessageLog, QgsRasterLayer, QgsVectorLayer, QgsGeometry, QgsFeature, QgsProject

from ..tools.tools import replaceSpaces

import re
from functools import partial

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_easin_dockwidget_base.ui'))

PATH_ICON_ZOOM = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons') + '\zoom.png')


class GeoEASINDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(GeoEASINDockWidget, self).__init__(parent)
        self.setupUi(self)

        # Search Button
        self.btnSearch.setEnabled(False)
        self.btnSearch.clicked.connect(self.searchAPI)

        # Clean treeData
        self.btnCleanResults.clicked.connect(self.clean_results)

        # Search text
        self.lineSpecieText.textChanged.connect(self.enable_button)

        # TreeData
        self.treeWidgetData.setColumnCount(2)
        self.treeWidgetData.setHeaderItem(QTreeWidgetItem(["Specie", ""]))
        self.treeWidgetData.setColumnWidth(0, 300)
        # self.treeWidgetData.itemDoubleClicked.connect(self.create_layer)
        self.treeWidgetData.itemDoubleClicked.connect(partial(self.printItem))

        # Tools
        self.btnBaseMapOSM.clicked.connect(self.addTileLayer)
        self.btnBaseMapCountries.clicked.connect(self.addVectorLayer)

        # Tab

        self.tabWidget.setCurrentIndex(0)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def enable_button(self):
        textLength = len(self.lineSpecieText.text())
        if textLength > 3:
            self.btnSearch.setEnabled(True)
        else:
            self.btnSearch.setEnabled(False)

    def fetch_term(self, term):
        """

        @param term: the species scientific name or part of it
        @return:
        """
        try:

            url = f'https://easin.jrc.ec.europa.eu/api/cat/term/{term}'
            req = request.Request(url)

            with request.urlopen(req) as f:
                QgsMessageLog.logMessage("oK", level=Qgis.Info)
                return json.loads(f.read().decode('utf-8'))

        except Exception as error:
            print(f'Error: {error}')
            self.requestInfo.setText("Error. Fallo de conexión")
            # 2 - QgsMessageLog
            # QgsMessageLog.logMessage(error, level=Qgis.Critical)
            QgsMessageLog.logMessage(
                f'Error: {error}', level=Qgis.Critical)

    def searchAPI(self):
        """

        @return:
        """

        term = self.lineSpecieText.text()
        term2 = 'Procambarus  acutus '
        term3 = re.sub('\\s+', ' ', term)
        term_list = []
        # print(replaceSpaces(term3))
        resp = self.fetch_term(replaceSpaces(term3))
        data = resp['results']
        self.requestInfo.setText(f'{len(data)} results for {term3}')
        # print(data)
        # print(type(data))
        try:
            for dataLevel0 in data:
                speciesName = dataLevel0['SpeciesName']
                speciesCatalogueId = dataLevel0['SpeciesCatalogueId']

                item_level0 = QTreeWidgetItem(self.treeWidgetData, [speciesName, 'Add grid: ' + speciesCatalogueId, ''])

                item_level0.setForeground(0, QColor("blue"))

                self.treeWidgetData.addTopLevelItem(item_level0)

                for dataLevel1 in dataLevel0.items():

                    key_level_1 = dataLevel1[0]
                    value_level_1 = dataLevel1[1]

                    if type(value_level_1) is list:

                        item_level_1 = QTreeWidgetItem(item_level0, [key_level_1])
                        self.treeWidgetData.addTopLevelItem(item_level_1)

                        for dataLevel2 in value_level_1:

                            for datalevel3 in dataLevel2.items():
                                key_level_3 = datalevel3[0]
                                value_level_3 = str(datalevel3[1])

                                item_level2 = QTreeWidgetItem(item_level_1, [key_level_3, value_level_3])
                                self.treeWidgetData.addTopLevelItem(item_level2)

                    elif type(value_level_1) is dict:

                        item_level_1 = QTreeWidgetItem(item_level0, [key_level_1])
                        self.treeWidgetData.addTopLevelItem(item_level_1)

                        for datalevel3 in value_level_1.items():
                            key_level_3 = datalevel3[0]
                            value_level_3 = str(datalevel3[1])

                            item_level2 = QTreeWidgetItem(item_level_1, [key_level_3, value_level_3])
                            self.treeWidgetData.addTopLevelItem(item_level2)

                    else:

                        item_level_1 = QTreeWidgetItem(item_level0, [key_level_1, str(value_level_1)])
                        self.treeWidgetData.addTopLevelItem(item_level_1)


        except:
            print('error')

    def clean_results(self, value):
        self.treeWidgetData.clear()
        self.requestInfo.setText(f'Info')

    def create_layer1(self, name_layer, gridID):
        print('Crea capa')
        layer_name = f"{name_layer}_{gridID}"

    def create_layer(self,speciesCatalogueId, speciesName=''):

        speciesid = speciesCatalogueId
        speciesname = speciesName
        skip = 0
        len_results = 1
        data = {}

        layer_name = f"{speciesid}_{speciesname}"

        def fetch_data(speciesid, skip):

            URL = f'https://easin.jrc.ec.europa.eu/api/geo/speciesid/{speciesid}/layertype/grid/take/50/skip/{skip}'
            req = request.Request(URL)  # URL de solicitud (solicitud GET)

            with request.urlopen(req) as f:  # Solicitud de URL abierta (como si abriera un archivo local)
                return json.loads(f.read().decode(
                    'utf-8'))  # Lea datos y codifique mientras usa json.loads para convertir datos en formato json en objetos python

        # URL + speciesid/{speciesid}/layertype/{layertype}/take/{num records to take}/skip/{num records teso skip}
        ## cntr o grid

        temp = QgsVectorLayer(
            "Polygon?crs=epsg:3035"
            "&field=LayerRecordId:string&index=yes"
            "&field=SpeciesId:string"
            "&field=SpeciesName:string"
            "&field=YearMin:int"
            "&field=YearMax:int"
            "&field=Reference:string:string(400)"
            "&field=Native:boolean"
            "&field=DataPartner:string",
            layer_name, "memory")

        def addGrid(temp, resultados):

            temp.startEditing()

            for feature in resultados:
                wkt = feature['Wkt']
                geom = QgsGeometry()
                geom = QgsGeometry.fromWkt(feature['Wkt'])
                feat = QgsFeature()
                feat.setGeometry(geom)

                yearMin = feature['YearMin'].replace("    ", "0")
                yearMax = feature['YearMax'].replace("    ", "0")

                feat.setAttributes([
                    feature['LayerRecordId'],
                    feature['SpeciesId'],
                    feature['SpeciesName'],
                    int(yearMin),
                    int(yearMax),
                    feature['Reference'],
                    feature['Native'],
                    feature['DataPartner'],
                ])
                temp.dataProvider().addFeatures([feat])

            temp.commitChanges()

        while len_results > 0:
            new_data = fetch_data(speciesid, skip)
            print(type(new_data))
            print(new_data)
            skip += 50
            resultados = new_data['results']
            len_results = len(resultados)
            print(len_results)

            #######
            addGrid(temp, resultados)

        if temp.featureCount() > 0:
            ## temp.renderer().symbol().setColor(QColor("red"))
            ## temp.triggerRepaint()
            QgsProject.instance().addMapLayer(temp)
            ## qgis.utils.iface.setActiveLayer(temp)
            ## qgis.utils.iface.zoomToActiveLayer()
        else:
            print('Sin resultados')


    def item_icon(self, key, value_id, QTW):
        icon_item = QTreeWidgetItem(QTW, 1)
        icon_item.setText(1, key + "(" + str(value_id) + ")")
        icon_item.setText(0, "ZOOM")
        icon_item.setIcon(0, QtGui.QIcon(QtGui.QPixmap(path_icon_zoom)))

    def printItem(self, treeitem, item):
        print(treeitem)
        print(item)
        getSelected = self.treeWidgetData.selectedItems()

        if getSelected:
            baseNode = getSelected[0]
            getChildNode = baseNode.text(item)

            if "Add grid" in getChildNode:
                name_layer = baseNode.text(0)
                id = baseNode.text(1).split(":")[1].strip()
                self.create_layer( id, name_layer)

    def addTileLayer(self):
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

