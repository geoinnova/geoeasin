"""
Model exported as python.
Name : Hydro network dispersion
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
from qgis.core import QgsProcessingParameterPoint
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorDestination


class HydroNetworkDispersion(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(
            QgsProcessingParameterRasterLayer('ModeloDigitaldeElevacinDEM', 'Digital Elevation Model (DEM)',
                                              defaultValue=None))
        self.addParameter(
            QgsProcessingParameterNumber('Tamaodepxel', 'Watershed size', type=QgsProcessingParameterNumber.Double,
                                         minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterPoint('Coordenadadeinvasin', 'Specie ocurrence', defaultValue='0.000000,0.000000'))
        self.addParameter(QgsProcessingParameterVectorDestination('TotalWatershedAffected', 'Total watershed affected',
                                                                  type=QgsProcessing.TypeVectorAnyGeometry,
                                                                  createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('HydroNetworkAffected', 'Hydro network affected',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WatershedsAffected', 'Watersheds affected',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
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
            'elevation': parameters['ModeloDigitaldeElevacinDEM'],
            'flow': None,
            'max_slope_length': None,
            'memory': 300,
            'threshold': parameters['Tamaodepxel'],
            'basin': QgsProcessing.TEMPORARY_OUTPUT,
            'drainage': QgsProcessing.TEMPORARY_OUTPUT,
            'stream': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ElementosTotalesDeRed'] = processing.run('grass7:r.watershed', alg_params, context=context,
                                                          feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Vectorizacion de cuencas
        alg_params = {
            '-b': False,
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
            'input': outputs['ElementosTotalesDeRed']['basin'],
            'type': 2,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VectorizacionDeCuencas'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                           feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Vectorizcion de rios
        alg_params = {
            '-b': False,
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
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VectorizcionDeRios'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                       feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Analisis de cuenca afectada
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'coordinates': parameters['Coordenadadeinvasin'],
            'input': outputs['ElementosTotalesDeRed']['drainage'],
            'output': 'TEMPORARY_OUTPUT',
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AnalisisDeCuencaAfectada'] = processing.run('grass7:r.water.outlet', alg_params, context=context,
                                                             feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Vectorizacion cuenca
        alg_params = {
            '-b': False,
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
            'input': outputs['AnalisisDeCuencaAfectada']['output'],
            'output': 'TEMPORARY_OUTPUT',
            'type': 2,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VectorizacionCuenca'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                        feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Vectorizacion de cuenca total
        alg_params = {
            '-b': False,
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
            'input': outputs['AnalisisDeCuencaAfectada']['output'],
            'type': 2,
            'output': parameters['TotalWatershedAffected']
        }
        outputs['VectorizacionDeCuencaTotal'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                               feedback=feedback, is_child_algorithm=True)
        results['TotalWatershedAffected'] = outputs['VectorizacionDeCuencaTotal']['output']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Clipear rios
        alg_params = {
            'INPUT': outputs['VectorizcionDeRios']['output'],
            'OVERLAY': outputs['VectorizacionCuenca']['output'],
            'OUTPUT': parameters['HydroNetworkAffected']
        }
        outputs['ClipearRios'] = processing.run('native:clip', alg_params, context=context, feedback=feedback,
                                                is_child_algorithm=True)
        results['HydroNetworkAffected'] = outputs['ClipearRios']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extraer por ubicacion 
        alg_params = {
            'INPUT': outputs['VectorizacionDeCuencas']['output'],
            'INTERSECT': outputs['ClipearRios']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': parameters['WatershedsAffected']
        }
        outputs['ExtraerPorUbicacion'] = processing.run('native:extractbylocation', alg_params, context=context,
                                                        feedback=feedback, is_child_algorithm=True)
        results['WatershedsAffected'] = outputs['ExtraerPorUbicacion']['OUTPUT']
        return results

    def name(self):
        return 'Hydro network dispersion'

    def displayName(self):
        return 'Hydro network dispersion'

    def group(self):
        return 'Distribution analysis'

    def groupId(self):
        return 'Distribution analysis'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculate the hydro network dispersion and the watershed dispersion area using an occurrence data.</p>
<h2>Input parameters</h2>
<h3>Digital Elevation Model (DEM)</h3>
<p>Digital Elevation Model (DEM).</p>
<h3>Watershed size</h3>
<p>Watershed size.</p>
<h3>Specie ocurrence</h3>
<p>An specie ocurrence (along the river).</p>
<h2>Outputs</h2>
<h3>Total watershed affected</h3>
<p>Total watershed affected by the alien specie.</p>
<h3>Hydro network affected</h3>
<p>The hydro network affected by the alien specie.</p>
<h3>Watersheds affected</h3>
<p>The watersheds affected.</p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return HydroNetworkDispersion()
