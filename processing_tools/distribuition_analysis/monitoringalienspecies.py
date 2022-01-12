"""
Model exported as python.
Name : Alien species hydro network monitoring
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterVectorLayer


class AlienSpeciesHydroNetworkMonitoring(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Hydronetworkaffected', 'Hydro network affected ',
                                                            types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Watershedsoradministrativemanagementlimits',
                                                            'Watersheds or administrative management limits',
                                                            types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('MonitoringPoints', 'Monitoring points',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, supportsAppend=True,
                                                            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Polígonos a líneas
        alg_params = {
            'INPUT': parameters['Watershedsoradministrativemanagementlimits'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolgonosALneas'] = processing.run('native:polygonstolines', alg_params, context=context,
                                                   feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Vigilancia EEI
        alg_params = {
            'INPUT': parameters['Hydronetworkaffected'],
            'INPUT_FIELDS': [''],
            'INTERSECT': outputs['PolgonosALneas']['OUTPUT'],
            'INTERSECT_FIELDS': [''],
            'INTERSECT_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VigilanciaEei'] = processing.run('native:lineintersections', alg_params, context=context,
                                                  feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Coordenadas X e Y
        alg_params = {
            'CRS': 'ProjectCrs',
            'INPUT': outputs['VigilanciaEei']['OUTPUT'],
            'PREFIX': 'Coord_',
            'OUTPUT': parameters['MonitoringPoints']
        }
        outputs['CoordenadasXEY'] = processing.run('native:addxyfields', alg_params, context=context, feedback=feedback,
                                                   is_child_algorithm=True)
        results['MonitoringPoints'] = outputs['CoordenadasXEY']['OUTPUT']
        return results

    def name(self):
        return 'Alien species hydro network monitoring'

    def displayName(self):
        return 'Alien species hydro network monitoring'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Location of administrative boundaries to monitoring alien species.</p>
<h2>Input parameters</h2>
<h3>Hydro network affected </h3>
<p>The hydro network affected.</p>
<h3>Watersheds or administrative management limits</h3>
<p>Watersheds or administrative management limits.</p>
<h2>Outputs</h2>
<h3>Monitoring points</h3>
<p>Points location to monitoring alien species.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return AlienSpeciesHydroNetworkMonitoring()
