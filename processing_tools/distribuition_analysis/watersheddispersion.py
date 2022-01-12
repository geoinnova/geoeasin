"""
Model exported as python.
Name : Watershed dispersion
Group : Distribution analysis
With QGIS : 31609
"""

import processing
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterPoint
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterRasterLayer


class WatershedDispersion(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterPoint('Citadelaespecie', 'Specie ocurrence', defaultValue='0.000000,0.000000'))
        self.addParameter(QgsProcessingParameterRasterLayer('DEM', 'Digital Elevation Model (DEM)', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(
            QgsProcessingParameterRasterDestination('WatershedDispersion', 'Watershed dispersion', createByDefault=True,
                                                    defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Direccion de drenaje
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
            'elevation': parameters['DEM'],
            'flow': None,
            'max_slope_length': None,
            'memory': 300,
            'threshold': None,
            'drainage': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DireccionDeDrenaje'] = processing.run('grass7:r.watershed', alg_params, context=context,
                                                       feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Cuenca de invasion
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'coordinates': parameters['Citadelaespecie'],
            'input': outputs['DireccionDeDrenaje']['drainage'],
            'output': parameters['WatershedDispersion']
        }
        outputs['CuencaDeInvasion'] = processing.run('grass7:r.water.outlet', alg_params, context=context,
                                                     feedback=feedback, is_child_algorithm=True)
        results['WatershedDispersion'] = outputs['CuencaDeInvasion']['output']
        return results

    def name(self):
        return 'Watershed dispersion'

    def displayName(self):
        return 'Watershed dispersion'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculate an upstream distribution using a DEM layer.</p>
<h2>Input parameters</h2>
<h3>Specie ocurrence</h3>
<p>An specie ocurrence (along the river).</p>
<h3>Digital Elevation Model (DEM)</h3>
<p>Digital Elevation Model (DEM).</p>
<h2>Outputs</h2>
<h3>Watershed dispersion</h3>
<p>Watershed dispersion</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return WatershedDispersion()
