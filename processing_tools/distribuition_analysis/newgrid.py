"""
Model exported as python.
Name : Create a new grid
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer


class CreateANewGrid(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer('Speciesgriddistribution', 'Occurences or species distribution grid',
                                              types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Horizontaldistance', 'Horizontal distance',
                                                       type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Verticaldistance', 'Vertical distance',
                                                       type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterFeatureSink('OutputGrid', 'Output grid', type=QgsProcessing.TypeVectorPolygon,
                                              createByDefault=True, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Create grid
        alg_params = {
            'CRS': 'ProjectCrs',
            'EXTENT': parameters['Speciesgriddistribution'],
            'HOVERLAY': 0,
            'HSPACING': parameters['Horizontaldistance'],
            'TYPE': 2,
            'VOVERLAY': 0,
            'VSPACING': parameters['Verticaldistance'],
            'OUTPUT': parameters['OutputGrid']
        }
        outputs['CreateGrid'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback,
                                               is_child_algorithm=True)
        results['OutputGrid'] = outputs['CreateGrid']['OUTPUT']
        return results

    def name(self):
        return 'Create a new grid'

    def displayName(self):
        return 'Create a new grid'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Create a new grid mesh using a maximum extent of species distribution and a new grid dimension.</p>
<h2>Input parameters</h2>
<h3>Occurences or species distribution grid</h3>
<p>The species distribution from EASIN or other occurences distribution.</p>
<h3>Horizontal distance</h3>
<p>Width grid.</p>
<h3>Vertical distance</h3>
<p>Height grid.</p>
<h3>Output grid</h3>
<p>The new output grid.</p>
<h2>Outputs</h2>
<h3>Output grid</h3>
<p>The new output grid.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return CreateANewGrid()
