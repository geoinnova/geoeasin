"""
Model exported as python.
Name : Range (using ineffective areas)
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer


class RangeUsingIneffectiveAreas(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('speciedistribution', 'Species distribution',
                                                            types=[QgsProcessing.TypeVectorAnyGeometry],
                                                            defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('dispersaldistance', 'Dispersal distance',
                                                       type=QgsProcessingParameterNumber.Double, defaultValue=0))
        self.addParameter(
            QgsProcessingParameterVectorLayer('referencegrid', 'Reference grid or administrative boundaries',
                                              types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        param = QgsProcessingParameterVectorLayer('Inefectiveareasuchasbarriersorinefectiveecosistems',
                                                  'Inefective area (such as barriers or inefective ecosystems)',
                                                  types=[QgsProcessing.TypeVector], defaultValue=None)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterNumber('inefectivedistance', 'Inefective distance o presure distance',
                                             type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308,
                                             maxValue=1.79769e+308, defaultValue=0)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterFeatureSink('Range', 'Range', type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
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
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractRangeGrids'] = processing.run('native:extractbylocation', alg_params, context=context,
                                                      feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Intersection
        alg_params = {
            'INPUT': outputs['BufferArea']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': parameters['Inefectiveareasuchasbarriersorinefectiveecosistems'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback,
                                                 is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Buffer inefective area
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': parameters['inefectivedistance'],
            'END_CAP_STYLE': 0,
            'INPUT': outputs['Intersection']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferInefectiveArea'] = processing.run('native:buffer', alg_params, context=context,
                                                         feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract inefective grids
        alg_params = {
            'INPUT': parameters['referencegrid'],
            'INTERSECT': outputs['BufferInefectiveArea']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractInefectiveGrids'] = processing.run('native:extractbylocation', alg_params, context=context,
                                                           feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'INPUT': outputs['ExtractRangeGrids']['OUTPUT'],
            'OVERLAY': outputs['ExtractInefectiveGrids']['OUTPUT'],
            'OUTPUT': parameters['Range']
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback,
                                               is_child_algorithm=True)
        results['Range'] = outputs['Difference']['OUTPUT']
        return results

    def name(self):
        return 'Range (using ineffective areas)'

    def displayName(self):
        return 'Range (using ineffective areas)'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculates the potential distribution area based on the dispersal capacity of the species and the exclusion of ineffective distribution areas.</p>
<h2>Input parameters</h2>
<h3>Species distribution</h3>
<p>The species distribution from EASIN or other resource. </p>
<h3>Dispersal distance</h3>
<p>Use a prudent maximum distance to which the species can disperse. </p>
<h3>Reference grid or administrative boundaries</h3>
<p>Use a grid or any administrative boundaries.</p>
<h3>Inefective area (such as barriers or inefective ecosystems)</h3>
<p>For ineffective areas (water bodies, islands, roads, urban areas) use the limits of the ineffective vector entities.</p>
<h3>Inefective distance o presure distance</h3>
<p>Ineffective buffer or radius of influence around the ineffective areas.</p>
<h2>Outputs</h2>
<h3>Range</h3>
<p>The output range distribution.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return RangeUsingIneffectiveAreas()
