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
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterPoint
from qgis.core import QgsProcessingParameterRasterLayer


class HydroNetworkDispersion(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterPoint('Coordenadadeinvasin', 'Specie ocurrence', defaultValue='0.000000,0.000000'))
        self.addParameter(
            QgsProcessingParameterRasterLayer('ModeloDigitaldeElevacinDEM', 'Digital Elevation Model (DEM)',
                                              defaultValue=None))
        self.addParameter(
            QgsProcessingParameterNumber('Tamaodepxel', 'Watershed size', type=QgsProcessingParameterNumber.Double,
                                         minValue=-1.79769e+308, maxValue=1.79769e+308, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('HydroNetworkAffected', 'Hydro network affected',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WatershedsAffected', 'Watersheds affected',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('TotalWatershedAffected', 'Total watershed affected',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, supportsAppend=True,
                                                            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(10, model_feedback)
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

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Vector rios
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
        outputs['VectorRios'] = processing.run('grass7:r.to.vect', alg_params, context=context, feedback=feedback,
                                               is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Vector subcuencastotal
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
        outputs['VectorSubcuencastotal'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                          feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Fix rios
        alg_params = {
            'INPUT': outputs['VectorRios']['output'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixRios'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback,
                                            is_child_algorithm=True)

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
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VectorizacionDeCuencaTotal'] = processing.run('grass7:r.to.vect', alg_params, context=context,
                                                               feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Fix subcuencas
        alg_params = {
            'INPUT': outputs['VectorSubcuencastotal']['output'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixSubcuencas'] = processing.run('native:fixgeometries', alg_params, context=context,
                                                  feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Fix cuencatotal
        alg_params = {
            'INPUT': outputs['VectorizacionDeCuencaTotal']['output'],
            'OUTPUT': parameters['TotalWatershedAffected']
        }
        outputs['FixCuencatotal'] = processing.run('native:fixgeometries', alg_params, context=context,
                                                   feedback=feedback, is_child_algorithm=True)
        results['TotalWatershedAffected'] = outputs['FixCuencatotal']['OUTPUT']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['FixSubcuencas']['OUTPUT'],
            'OVERLAY': outputs['FixCuencatotal']['OUTPUT'],
            'OUTPUT': parameters['WatershedsAffected']
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback,
                                         is_child_algorithm=True)
        results['WatershedsAffected'] = outputs['Clip']['OUTPUT']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['FixRios']['OUTPUT'],
            'OVERLAY': outputs['FixCuencatotal']['OUTPUT'],
            'OUTPUT': parameters['HydroNetworkAffected']
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback,
                                         is_child_algorithm=True)
        results['HydroNetworkAffected'] = outputs['Clip']['OUTPUT']
        return results

    def name(self):
        return 'Hydro network dispersion'

    def displayName(self):
        return 'Hydro network dispersion'

    def group(self):
        return 'Dispersion'

    def groupId(self):
        return 'Dispersion'

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>Calculate the hydro network dispersion and the watershed dispersion area using an occurrence data.</p>
<h2>Input parameters</h2>
<h3>Specie ocurrence</h3>
<p>An specie ocurrence (along the river).</p>
<h3>Digital Elevation Model (DEM)</h3>
<p>Digital Elevation Model (DEM).</p>
<h3>Watershed size</h3>
<p>Watershed size.</p>
<h2>Outputs</h2>
<h3>Hydro network affected</h3>
<p>The hydro network affected by the alien specie.</p>
<h3>Watersheds affected</h3>
<p>The watersheds affected. </p>
<h3>Total watershed affected</h3>
<p>Total watershed affected by the alien specie. </p>
<br><p align="right">Algorithm author: Roberto Matellanes</p></body></html>"""

    def createInstance(self):
        return HydroNetworkDispersion()
