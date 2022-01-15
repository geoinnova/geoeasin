"""
Model exported as python.
Name : Environment statistics
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBand
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer


class EnvironmentStatistics(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('speciedistribution', 'Species distribution',
                                                            types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterLayer('Environmentlayer', 'Environment raster variable (band or multi band)',
                                              defaultValue=None))
        self.addParameter(QgsProcessingParameterBand('envband', 'Band', parentLayerParameterName='Environmentlayer',
                                                     allowMultiple=False, defaultValue=[0]))
        self.addParameter(
            QgsProcessingParameterExpression('fieldname', 'Field statistic name', parentLayerParameterName='',
                                             defaultValue='STA_'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Zonal statistics
        alg_params = {
            'COLUMN_PREFIX': parameters['fieldname'],
            'INPUT_RASTER': parameters['Environmentlayer'],
            'INPUT_VECTOR': parameters['speciedistribution'],
            'RASTER_BAND': parameters['envband'],
            'STATISTICS': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        }
        outputs['ZonalStatistics'] = processing.run('native:zonalstatistics', alg_params, context=context,
                                                    feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'Environment statistics'

    def displayName(self):
        return 'Environment statistics'

    def group(self):
        return 'Analysis'

    def groupId(self):
        return 'Analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculates environmental statistics related to species distribution using a raster file as the analysis surface.</p>
<h2>Input parameters</h2>
<h3>Species distribution</h3>
<p>Select the species distribution from EASIN or other resource. </p>
<h3>Environment raster variable (band or multi band)</h3>
<p>Use a environmental raster to obtain its statistical values ​​(temperature, altitude, precipitation ...)</p>
<h3>Band</h3>
<p>For multiband raster, select the specific analysis band.</p>
<h3>Field statistic name</h3>
<p>Variable name as prefix in input fields from species distribution layer.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return EnvironmentStatistics()
