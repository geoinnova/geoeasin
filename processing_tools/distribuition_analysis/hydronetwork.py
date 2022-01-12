"""
Model exported as python.
Name : Hydro network
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorDestination


class HydroNetwork(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterRasterLayer('DigitalElevationModelDEM', 'Digital Elevation Model (DEM)',
                                                            defaultValue=None))
        self.addParameter(
            QgsProcessingParameterNumber('Watershedsize', 'Watershed size', type=QgsProcessingParameterNumber.Double,
                                         defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorDestination('Hydronetwork', 'Hydronetwork',
                                                                  type=QgsProcessing.TypeVectorAnyGeometry,
                                                                  createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Elementos totales de red
        alg_params = {
            '-4': False,
            '-a': False,
            '-b': False,
            '-m': False,
            '-s': False,
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'blocking': None,
            'convergence': 5,
            'depression': None,
            'disturbed_land': None,
            'elevation': parameters['DigitalElevationModelDEM'],
            'flow': None,
            'max_slope_length': None,
            'memory': 300,
            'threshold': parameters['Watershedsize'],
            'stream': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ElementosTotalesDeRed'] = processing.run('grass7:r.watershed', alg_params, context=context,
                                                          feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Vectorizacion de rios
        alg_params = {
            '-b': True,
            '-s': False,
            '-t': False,
            '-v': False,
            '-z': False,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'column': 'value',
            'input': outputs['ElementosTotalesDeRed']['stream'],
            'type': 0,
            'output': parameters['Hydronetwork']
        }
        outputs['VectorizacionDeRios'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                        feedback=feedback, is_child_algorithm=True)
        results['Hydronetwork'] = outputs['VectorizacionDeRios']['output']
        return results

    def name(self):
        return 'Hydro network'

    def displayName(self):
        return 'Hydro network'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Create a hydrological network.</p>
<h2>Input parameters</h2>
<h3>Digital Elevation Model (DEM)</h3>
<p>Digital Elevation Model (DEM).</p>
<h3>Watershed size</h3>
<p>Watershed size.</p>
<h2>Outputs</h2>
<h3>Hydronetwork</h3>
<p>The hydro network output.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return HydroNetwork()
