# -*- coding: utf-8 -*-

"""
/***************************************************************************
 IMSGS
                                 A QGIS plugin
 This plugin generates grid based on IMSGS standard.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-10-25
        copyright            : (C) 2023 by Irwanto, Rania Altairatri Evelina Brawijaya, Mutia Hendriani Putri, Muhammad Usman Alshaadiq
        email                : 15120068@mahasiswa.itb.ac.id
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Irwanto, Rania Altairatri Evelina Brawijaya, Mutia Hendriani Putri, Muhammad Usman Alshaadiq'
__date__ = '2023-10-25'
__copyright__ = '(C) 2023 by Irwanto, Rania Altairatri Evelina Brawijaya, Mutia Hendriani Putri, Muhammad Usman Alshaadiq'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingMultiStepFeedback,
                       QgsCoordinateReferenceSystem,
                       QgsFeature,
                       QgsProcessingParameterNumber,
                       QgsFields,QgsField,QgsWkbTypes,
                       )
from qgis.PyQt.QtCore import *
import os
from qgis.PyQt.QtGui import QIcon
import processing

#--------------------- Calculate Energy -------------------------
class calcenergyAlgorithm(QgsProcessingAlgorithm):

    OUTPUT = 'OUTPUT'
    popgrid = 'popgrid'
    popfield = 'popfield'
    AKE = 'AKE'

    def name(self):
        return '1. Generate Energy Needs Distribution'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'd. Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/enerneed.png'))
    
    def helpUrl(self):
        file = os.path.dirname(__file__) + '/en.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def createInstance(self):
        return calcenergyAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.popgrid,
                self.tr('Input IMSGS Population layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.popfield,
                self.tr('Select Field that Contains Population'),
                parentLayerParameterName=self.popgrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.AKE,
                self.tr('Input Energy Needs Value (kcal)'),
                defaultValue=2100
            )
        )

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

# ==================== Define Parameter =====================================   
        # input popfield from population layer
        pop_field = self.parameterAsString(parameters, self.popfield,context)

        # AKE number
        AKE_number = self.parameterAsString(parameters, self.AKE, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(2, feedback)
        
 # ==================== algoritm =====================================  

        # transform coordinates to epsg 4326
        feedback.setProgressText('Reproject All layer to EPSG 4326...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        pop_repp = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['popgrid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})   
        
        pop_rep = processing.run("native:fixgeometries", 
                                {'INPUT':pop_repp['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})
        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
               
        #calculate total weigth for each grid
        feedback.setProgressText('Calculate grid AKE for each year... ')

        AKE_Count = processing.run("native:fieldcalculator", 
                                      {'INPUT':pop_rep['OUTPUT'],
                                       'FIELD_NAME':'AKEGrid',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':f'365 * {pop_field} * {AKE_number} ',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 2
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

# ==================== output parameter =====================================  

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('Population', QVariant.Int,'', 50))
        fields.append(QgsField('AKEGrid', QVariant.Int,'', 50))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in AKE_Count['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            popul = feat[f'{pop_field}']
            AKEG = feat['AKEGrid']
            

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,popul,AKEG])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        

        return {self.OUTPUT: dest_id}

class distavailabilityAlgorithm(QgsProcessingAlgorithm):

    OUTPUT = 'OUTPUT'
    grid = 'grid'
    admlay = 'admlay'
    admfield = 'admfield'
    enerfield = 'enerfield'
    ESPlay = 'ESPlay'
    IJEPBPESP = 'IJEPBPESP'

    def name(self):
        return '2. Generate Energy Availability Distribution'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'd. Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/eneravai.png'))

    def helpUrl(self):
        file = os.path.dirname(__file__) + '/en.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def createInstance(self):
        return distavailabilityAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.grid,
                self.tr('Input IMSGS Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.admlay,
                self.tr('Input Administrative Boundary Layer that contains Food Energy Production (kcal)'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.admfield,
                self.tr('Select Fields that Contains Administrative Name'),
                parentLayerParameterName=self.admlay,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.enerfield,
                self.tr('Select Fields that Contains Food Energy Production (kcal)'),
                parentLayerParameterName=self.admlay,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ESPlay,
                self.tr('Input Layer that Contains Environmental Performance Index (IJE Pangan)'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.IJEPBPESP,
                self.tr('Select Fields that Contains Environmental Performance Index (IJE Pangan)'),
                parentLayerParameterName=self.ESPlay,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

# ==================== Define Parameter =====================================   
        # input IJEPBP field per grid
        IJEPBP_field = self.parameterAsString(parameters, self.IJEPBPESP,context)

        # Administration boundary name field
        adm_field = self.parameterAsString(parameters, self.admfield, context)

        # Energy Production from Administrative Boundary Layer
        ener_field = self.parameterAsString(parameters, self.enerfield, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(18, feedback)
        
 # ==================== algoritm =====================================  
        # transform coordinates to epsg 4326
        feedback.setProgressText('Preparing Data Processing...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        grid_repp = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['grid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        grid_rep = processing.run("native:fixgeometries", 
                                {'INPUT':grid_repp['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})

        adm_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['admlay'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        adm_fix =  processing.run("native:fixgeometries", 
                                {'INPUT':adm_rep['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})    
        
        ESP_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['ESPlay'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})    

        esp_fix =  processing.run("native:fixgeometries", 
                                {'INPUT':ESP_rep['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})

        grid_clip =  processing.run("native:clip", 
                                {'INPUT':grid_rep['OUTPUT'],
                                 'OVERLAY':adm_fix['OUTPUT'],
                                 'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})           

        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        feedback.setProgressText('Intersect Administrative Boundary with Grid Layer...')

        intr_admn = processing.run("native:intersection", 
                                  {'INPUT':adm_fix['OUTPUT'], 
                                   'OVERLAY':grid_clip['OUTPUT'],
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})
        
        #progress set to 2
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        feedback.setProgressText('Calculate Administrative Area For Each Grid...')
        
        admin_area =processing.run("native:fieldcalculator", 
                                      {'INPUT':intr_admn['OUTPUT'],
                                       'FIELD_NAME':'area_admint',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':'$area',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT}) 

        #progress set to 3
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
        feedback.setProgressText('Aggregate Administrative Boundary...')        

        agg_admin  = processing.run("native:aggregate", {'INPUT':admin_area['OUTPUT'],
                                                      'GROUP_BY':'"IMGSID"',
                                                      'AGGREGATES':[{'aggregate': 'concatenate_unique',
                                                                     'delimiter': ',',
                                                                     'input': '"IMGSID"',
                                                                     'length': 50,
                                                                     'name': 'IMGSID',
                                                                     'precision': 0,
                                                                     'sub_type': 0,
                                                                     'type': 10,
                                                                     'type_name': 'text'},
                                                                     
                                                                     {'aggregate': 'maximum',
                                                                      'delimiter': ',',
                                                                      'input': f'if("area_admint"=maximum("area_admint"),{adm_field},null)',
                                                                      'length': 50,
                                                                      'name': 'Admname_1',
                                                                      'precision': 0,
                                                                      'sub_type': 0,
                                                                      'type': 10,
                                                                      'type_name': 'text'},

                                                                    {'aggregate': 'maximum',
                                                                      'delimiter': ',',
                                                                      'input': f'if("area_admint"=maximum("area_admint"),{ener_field},null)',
                                                                      'length': 50,
                                                                      'name': f'{ener_field}',
                                                                      'precision': 20,
                                                                      'sub_type': 0,
                                                                      'type': 6,
                                                                      'type_name': 'double precision'}],
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 4
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}
        
        feedback.setProgressText('Join Adminstrative Boundary with Grid Layer...') 

        join = processing.run("native:joinattributestable", {'INPUT_2':agg_admin['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':grid_clip['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}       
        
        feedback.setProgressText('Split Grid by Administrative Boundary...') 

        split_grid = processing.run("native:splitvectorlayer", 
                {'INPUT':join['OUTPUT'],
                'FIELD':f'{ener_field}',
                'PREFIX_FIELD':True,
                'FILE_TYPE':0,
                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 6
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}     
        
        feedback.setProgressText('Split Enviromental Service Index...')    

        esp_split = processing.run("native:multiparttosingleparts", 
                                     {'INPUT':esp_fix['OUTPUT'],
                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 7
        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}   
        
        partial_int = []

        feedback.setProgressText('Intersect Grid with Enviromental Service Index Layer...')  

        for i in os.listdir(split_grid['OUTPUT']):
            current_file = os.path.join(split_grid['OUTPUT'],i)

            processing.run("native:selectbylocation", 
                           {'INPUT':esp_split['OUTPUT'],
                            'PREDICATE':[0],
                            'INTERSECT':current_file,
                            'METHOD':0})
            
            extract_esp =  processing.run("native:saveselectedfeatures", 
                                     {'INPUT':esp_split['OUTPUT'],
                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
            
            intr_partial = processing.run("native:intersection", 
                                  {'INPUT':extract_esp['OUTPUT'], 
                                   'OVERLAY':current_file,
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})
            
            partial_int.append(intr_partial['OUTPUT'])

        #progress set to 8
        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}
           
        feedback.setProgressText('Merging Intersect Layer ...')    

        intr = processing.run("native:mergevectorlayers", 
                                   {'LAYERS':partial_int,
                                    'CRS':None,
                                    'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 9
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}
            
        # calculate area for each feature
        feedback.setProgressText('Calulate Area for each feature...')

        feat_area = processing.run("native:fieldcalculator", 
                                {'INPUT':intr['OUTPUT'],
                                'FIELD_NAME':'area_feat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'$area',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 10
        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        #calculate sum area by id
        feedback.setProgressText('Calculate Total Area Feature for each grid ...')

        sum_by_id(feat_area, 'sum_area', 'IMGSID', 'area_feat')

        #progress set to 11
        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}
        
        # Calculate IJEPBP for each intersected feature
        feedback.setProgressText('Calculate IJEPBP for each intersected feature...')

        IJEPBP_feat = processing.run("native:fieldcalculator", 
                                {'INPUT':feat_area['OUTPUT'],
                                'FIELD_NAME':'IJEPBPfeat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'(area_feat/sum_area)*{IJEPBP_field}',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 12
        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        feedback.setProgressText('Calculate Sum IJEPBP for Each Grid ...')

        sum_by_id(IJEPBP_feat, 'IJEPBP_grid', 'IMGSID', 'IJEPBPfeat')

        #progress set to 13
        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # join value to grid
        feedback.setProgressText('Join Attribute Table between LandCover and Grid ...')

        join_2 = processing.run("native:joinattributestable", {'INPUT_2':IJEPBP_feat['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':join['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 14
        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {} 

        feedback.setProgressText('Removing Null Value ...')
        
        esp_null =processing.run("native:fieldcalculator", 
                                      {'INPUT':join_2['OUTPUT'],
                                       'FIELD_NAME':'IJEPBP_gridnull',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':'if("IJEPBP_grid" is null, 0, "IJEPBP_grid")',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT}) 
        
        #progress set to 15
        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        feedback.setProgressText('Calculate Sum by Admin Name ...') 
        
        sum_by_id(esp_null, 'IJEPBP_admin', 'Admname_1', 'IJEPBP_gridnull')

        #progress set to 16
        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Calculate Energy
        feedback.setProgressText('Calculate Energy Per Grid ...')

        EnergyCalc = processing.run("native:fieldcalculator", 
                                {'INPUT':esp_null['OUTPUT'],
                                'FIELD_NAME':'Energy_Available',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'(IJEPBP_gridnull/IJEPBP_admin)*{ener_field}',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 17
        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}           
        
        feedback.setProgressText('join attribute table to grid layer ... ')

        join_3 = processing.run("native:joinattributestable", {'INPUT_2':EnergyCalc['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':grid_rep['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return{}

# ==================== output parameter =====================================  

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('EnerAvai', QVariant.Double,'', 50,5))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in join_3['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            energy_available = feat['Energy_Available']

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,energy_available])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        
        return {self.OUTPUT: dest_id}
      
class carcapAlgorithm(QgsProcessingAlgorithm):

    OUTPUT = 'OUTPUT'
    needgrid = 'needgrid'
    needfield = 'needfield'
    avagrid = 'avagrid'
    avafield = 'avafield'
    AKE = 'AKE'

    def name(self):
        return '3. Calculate Energy Needs and Availability Difference and Status'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'd. Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/enerstatus.png'))

    def helpUrl(self):
        file = os.path.dirname(__file__) + '/en.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def createInstance(self):
        return carcapAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.needgrid,
                self.tr('Input IMSGS Energy Needs Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.needfield,
                self.tr('Select Field that Contains Energy Needs for each Grid'),
                parentLayerParameterName=self.needgrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.avagrid,
                self.tr('Input IMSGS Energy Availability Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.avafield,
                self.tr('Select Field that Contains Energy Availability for each Grid'),
                parentLayerParameterName=self.avagrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )


        self.addParameter(
            QgsProcessingParameterNumber(
                self.AKE,
                self.tr('Input Energy Sufficiency Value (kcal)'),
                defaultValue=2100
            )
        )

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

# ==================== Define Parameter =====================================   

        # input popfield from population layer
        need_field = self.parameterAsString(parameters, self.needfield,context)

        # input popfield from population layer
        ava_field = self.parameterAsString(parameters, self.avafield,context)

        # AKE number
        AKE_number = self.parameterAsString(parameters, self.AKE, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(5, feedback)
        
 # ==================== algoritm =====================================  
        

# transform coordinates to epsg 4326
        
        feedback.setProgressText('Reproject All layer to EPSG 4326...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        need_repp = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['needgrid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        need_rep = processing.run("native:fixgeometries", 
                                {'INPUT':need_repp['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})

        ava_repp = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['avagrid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  
        
        ava_rep = processing.run("native:fixgeometries", 
                                {'INPUT':ava_repp['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})
        
        
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return{}

# join attributes to grid layer 

        feedback.setProgressText('join attribute table to grid layer ... ')


        join = processing.run("native:joinattributestable", {'INPUT_2': need_rep['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':ava_rep['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':True,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return{}

#calculate difference
        feedback.setProgressText('Calculate Needs and Availability Difference ... ')

        difference = processing.run("native:fieldcalculator", 
                                      {'INPUT':join['OUTPUT'],
                                       'FIELD_NAME':'Diff',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':f'{ava_field} - {need_field} ',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 3
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

#calculate difference
        feedback.setProgressText('Calculate carrying capacity threshold ... ')

        threshold = processing.run("native:fieldcalculator", 
                                      {'INPUT':difference['OUTPUT'],
                                       'FIELD_NAME':'Thres',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':f'({ava_field}/({AKE_number}*365))',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 4
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

# Status string
        stat = processing.run("native:fieldcalculator", 
                                      {'INPUT':threshold['OUTPUT'],
                                       'FIELD_NAME':'Stats',
                                       'FIELD_TYPE':2,
                                       'FIELD_LENGTH':10,
                                       'FIELD_PRECISION':0,
                                       'FORMULA':"if(diff<=0, title('Not'),title('Exceed'))",
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

# ==================== output parameter =====================================  

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('Population', QVariant.Int,'', 50))
        fields.append(QgsField('AgridF', QVariant.Double, '', 50,5))
        fields.append(QgsField('NgridF', QVariant.Double, '', 50,5))
        fields.append(QgsField('Difference', QVariant.Double, '', 50,5))
        fields.append(QgsField('Status', QVariant.String,'', 50))
        fields.append(QgsField('Threshold', QVariant.Int, '', 50))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in stat['OUTPUT'].getFeatures():
            IMGSID = feat['IMGSID']
            popul = feat['Population']
            Agridf = feat[f'{ava_field}']
            Ngridf = feat[f'{need_field}']
            Diff = feat['Diff']
            Stat = feat['Stats']
            Thres = feat['Thres']
            

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([IMGSID,popul,Agridf,Ngridf,Diff,Stat,Thres])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        

        return {self.OUTPUT: dest_id}

# ==================== function =====================================       
                
def sum_by_id(input, field_name, ids, cal_field):
    layer = input['OUTPUT']   
    # Create a new field for storing the total values
    total_field = QgsField(field_name, QVariant.Double, len=20, prec=5)
    layer.dataProvider().addAttributes([total_field])
    layer.updateFields()

    # Get field indices
    id_index = layer.fields().indexFromName(ids)
    cal_index = layer.fields().indexFromName(cal_field)
    total_index = layer.fields().indexFromName(field_name)

    # Dictionary to store total values for each unique ID
    total_values = {}

    # Calculate total values for each unique ID
    for feature in layer.getFeatures():
        unique_id = feature.attributes()[id_index]
        cal_value = feature.attributes()[cal_index]

        # Check if cal_value is not None
        if cal_value is not None:
            # Update total_values dictionary
            if unique_id not in total_values:
                total_values[unique_id] = cal_value
            else:
                total_values[unique_id] += cal_value

    # Update the 'field_name' field with the total values
    attribute_map = {}
    for feature in layer.getFeatures():
        unique_id = feature.attributes()[id_index]
        total_value = total_values.get(unique_id, 0)  # Use 0 if unique_id not found

        # Update the attribute_map
        attribute_map[feature.id()] = {total_index: total_value}

    layer.dataProvider().changeAttributeValues(attribute_map)