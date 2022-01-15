"""
Model exported as python.
Name : Dissolve distribution area
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterVectorLayer


class DissolveDistributionArea(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer('distributionarea', 'Distribution species area from EASIN data',
                                              types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(
            QgsProcessingParameterField('biodiversityfield', 'Biodiversity field', type=QgsProcessingParameterField.Any,
                                        parentLayerParameterName='distributionarea', allowMultiple=True,
                                        defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('DissolvedDistributionArea', 'Dissolved distribution area',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Dissolve
        alg_params = {
            'FIELD': parameters['biodiversityfield'],
            'INPUT': parameters['distributionarea'],
            'OUTPUT': parameters['DissolvedDistributionArea']
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback,
                                             is_child_algorithm=True)
        results['DissolvedDistributionArea'] = outputs['Dissolve']['OUTPUT']
        return results

    def name(self):
        return 'Dissolve distribution area'

    def displayName(self):
        return 'Dissolve distribution area'

    def group(self):
        return 'Analysis'

    def groupId(self):
        return 'Analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Dissolve distribution zones based on strategic ecological or geographic fields.</p>
<h2>Input parameters</h2>
<h3>Distribution species area from EASIN data</h3>
<p>The EASIN distribution area.</p>
<h3>Biodiversity field</h3>
<p>The dissolve key field such a "specie", "country", "provider"...</p>
<h2>Outputs</h2>
<h3>Dissolved distribution area</h3>
<p>The output dissolved distribution area.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return DissolveDistributionArea()
