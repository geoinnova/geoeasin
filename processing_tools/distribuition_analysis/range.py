"""
Model exported as python.
Name : Range
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


class Range(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('speciedistribution', 'Species distribution',
                                                            types=[QgsProcessing.TypeVectorAnyGeometry],
                                                            defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('dispersaldistance', 'Dispersal distance',
                                                       type=QgsProcessingParameterNumber.Double, defaultValue=0))
        self.addParameter(
            QgsProcessingParameterVectorLayer('referencegrid', 'Reference grid or administrative boundaries',
                                              types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Range', 'Range', type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Buffer area
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': parameters['dispersaldistance'],
            'END_CAP_STYLE': 0,
            'INPUT': parameters['speciedistribution'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferArea'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback,
                                               is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract range grids
        alg_params = {
            'INPUT': parameters['referencegrid'],
            'INTERSECT': outputs['BufferArea']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': parameters['Range']
        }
        outputs['ExtractRangeGrids'] = processing.run('native:extractbylocation', alg_params, context=context,
                                                      feedback=feedback, is_child_algorithm=True)
        results['Range'] = outputs['ExtractRangeGrids']['OUTPUT']
        return results

    def name(self):
        return 'Range'

    def displayName(self):
        return 'Range'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculates the potential distribution area using the dispersal capacity of the species.</p>
<h2>Input parameters</h2>
<h3>Species distribution</h3>
<p>The species distribution from EASIN or other resource. </p>
<h3>Dispersal distance</h3>
<p>Use a prudent maximum distance to which the species can disperse.</p>
<h3>Reference grid or administrative boundaries</h3>
<p>Use a new grid or any administrative boundaries.</p>
<h2>Outputs</h2>
<h3>Range</h3>
<p>The output range distribution.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return Range()
