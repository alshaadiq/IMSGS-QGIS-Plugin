# -*- coding: utf-8 -*-

"""
/***************************************************************************
 IMSGS
                                 A QGIS plugin
 This plugin generates grid based on IMSGS standart.
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

from qgis.PyQt.QtCore import (QCoreApplication,QVariant)
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsCoordinateReferenceSystem,
                       QgsFields,QgsField,QgsWkbTypes,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsFeature
                       )
from qgis.PyQt.QtCore import *
import processing


#--------------------- Calculate Energy -------------------------
class calcneedAlgorithm(QgsProcessingAlgorithm):

    POPUL_GRID = 'POPUL_GRID'
    POPUL_FIELD = 'POPUL_FIELD'
    STD_WATER = 'STD_WATER'
    COR_FCT = 'COR_FCT'
    VEG = 'VEG'
    VEG_INT = 'VEG_INT'
    STD_VEG = 'STD_VEG'
    NEED = 'NEED'

    def name(self):
        return '1. Generate Water Needs Distribution'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Environmental Carrying Capacity (Water)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return calcneedAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        # Population grid
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POPUL_GRID,
                self.tr('Input grid layer containing population values ​​per grid'),
                [QgsProcessing.TypeVectorPolygon],
                optional=False,
            )
        )

        #input population values per grid
        self.addParameter(
            QgsProcessingParameterField(
                self.POPUL_FIELD,
                self.tr('Select Fields that Contains Population Values per Grid'),
                parentLayerParameterName = self.POPUL_GRID, # parent grid layer
                type=QgsProcessingParameterField.Any
            )
        )  

        #input standard household water requirements per year
        self.addParameter(
            QgsProcessingParameterNumber(
                self.STD_WATER,
                self.tr("Input standard household water requirements per year "),
                type=QgsProcessingParameterNumber.Double,
                minValue=1,
                defaultValue=43.2,
                optional = False
            )
        )

        # input correction Factor for water requirements per year
        self.addParameter(
            QgsProcessingParameterNumber(
                self.COR_FCT,
                self.tr("Input Correction Factor for household water requirements per year"),
                type = QgsProcessingParameterNumber.Double,
                minValue=1,
                defaultValue=2,
                optional = False
            )
        )

        # Input Vegetation layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VEG,
                self.tr('Input Vegetation layer containing Crop intensity in percent (%) of seasons per year'),
                [QgsProcessing.TypeVectorPolygon],
                optional=False,
            )
        )

        #input vegetation field that contain intensity
        self.addParameter(
            QgsProcessingParameterField(
                self.VEG_INT,
                self.tr('Select Fields that Contain crop intensity in percent (%) of seasons per year'),
                parentLayerParameterName = self.VEG, # parent grid layer
                type=QgsProcessingParameterField.Any
            )
        )

        #Input water usage standard
        self.addParameter(
            QgsProcessingParameterNumber(
                self.STD_VEG,
                self.tr("Input Water Usage Standard for vegetation"),
                type = QgsProcessingParameterNumber.Double,
                minValue=1,
                defaultValue = 10368,
                optional = False
            )
        )

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.NEED,
                self.tr('Output layer'),
            )
        )


    def processAlgorithm(self, parameters, context, model_feedback):

# ==================== Define Parameter =====================================   

        #input population field
        popul = self.parameterAsString(parameters, self.POPUL_FIELD, context)

        #input standard for adequate living water requirements per year 
        KHL = self.parameterAsDouble(parameters, self.STD_WATER, context)

        #input factor correction for water requirements
        Fc = self.parameterAsDouble(parameters, self.COR_FCT, context)

        # input field contain vegetation intensity
        int_veg = self.parameterAsString(parameters, self.VEG_INT, context)

        #input water usage standard for vegetation
        w_veg = self.parameterAsDouble(parameters, self.STD_VEG, context)

        # initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(8,model_feedback)    

 # ==================== algoritm =====================================  
       
       # transform coordinate to epsg 4326
        feedback.setProgressText('Reproject All Layer to EPSG 4326')

        grid_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['POPUL_GRID'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        veg_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['VEG'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  
        
        veg_fix =  processing.run("native:reprojectlayer",
                                {'INPUT':veg_rep['OUTPUT'],
                                'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})


        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return{}
        
        # calculate population water need per grid

        feedback.setProgressText('Calculate household water requirements per grid')

        D_grid =  processing.run("native:fieldcalculator", 
                                {'INPUT':grid_rep['OUTPUT'],
                                'FIELD_NAME': "Dgrid",
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'{popul}*{KHL}*{Fc}',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 2
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Intersect land cover
        feedback.setProgressText('Intersect Vegetation with Grid Layer...')

        intr_veg = processing.run("native:intersection", 
                                  {'INPUT':veg_fix['OUTPUT'], 
                                   'OVERLAY': grid_rep['OUTPUT'],
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})

        #progress set to 3
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
        # calculate area for each feature in road layer
        feedback.setProgressText('Calulate Area for each feature in grid layer...')

        feat_area = processing.run("native:fieldcalculator", 
                                {'INPUT':intr_veg['OUTPUT'],
                                'FIELD_NAME':'area_feat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'$area/10000',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})      

        #progress set to 4
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}
        
        #calculate land water needs

        feedback.setProgressText('Calculate land water needs for each feature in grid layer...')

        q_feat =  processing.run("native:fieldcalculator", 
                                {'INPUT': feat_area['OUTPUT'],
                                'FIELD_NAME': "qfeat",
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'area_feat*{int_veg}*{w_veg}',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}
        
        #calculate sum by id land water needs
        feedback.setProgressText('Sum by ID Land Water Needs ...')

        sum_by_id(q_feat, 'Qgrid', 'IMGSID', 'qfeat')

        #progress set to 6
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}
        
        # join value to grid
        feedback.setProgressText('Join Value To Grid Layer...')

        join = processing.run("native:joinattributestable", {'INPUT_2':q_feat['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':D_grid['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 7
        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}
        
        # Calculate water need 

        feedback.setProgressText('Calculate water Need per Grid ...')

        T_grid =  processing.run("native:fieldcalculator", 
                                {'INPUT': join['OUTPUT'],
                                'FIELD_NAME': "Tgrid",
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'Dgrid + Qgrid',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 8
        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

# ==================== output parameter =====================================  
        
        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('Population', QVariant.Int,'', 50))
        fields.append(QgsField('Dgrid', QVariant.Double, '', 50 ,5))
        fields.append(QgsField('Qgrid', QVariant.Double, '', 50, 5))
        fields.append(QgsField('Tgrid', QVariant.Double, '', 50, 5))


        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.NEED, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in T_grid['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            popul_field = feat[f'{popul}']
            d_grid_1 = feat['Dgrid']
            q_grid_1 = feat['Qgrid']
            T_grid_1 = feat['Tgrid']

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,popul_field,d_grid_1,q_grid_1,T_grid_1])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        return {self.NEED: dest_id}
    
class distavailability2Algorithm(QgsProcessingAlgorithm):

    Grid = 'Grid'
    IJH ='IJH'
    IJH_V = 'IJH_V'
    WAS ='WAS'
    WAS_V = 'WAS_V'
    WAS_N = 'WAS_N'
    OUTPUT = 'OUTPUT'

    def name(self):
        return '2. Generate Water Availability Distribution'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Environmental Carrying Capacity (Water)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return distavailability2Algorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  
        
        #input grid 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.Grid,
                self.tr('Input Grid Layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # input environmental services performance
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.IJH,
                self.tr('Input Layer that contains environmental services performance'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # input field that contains environmental services performance
        self.addParameter(
            QgsProcessingParameterField(
                self.IJH_V,
                self.tr('Select Fields that Contains environmental services performance'),
                parentLayerParameterName = self.IJH, # parent landcover layer
                type=QgsProcessingParameterField.Any
            )
        )

        #input watershed area layer 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.WAS,
                self.tr('Input Layer that contains Watershed Area'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        #input field that contain total water availability
        self.addParameter(
            QgsProcessingParameterField(
                self.WAS_N,
                self.tr('Select Field That Contains Water shed Area Name'),
                parentLayerParameterName = self.WAS, # parent layer 
                type=QgsProcessingParameterField.Any
            )
        )

        #input field that contain total water availability
        self.addParameter(
            QgsProcessingParameterField(
                self.WAS_V,
                self.tr('Select Field That Contains Total Water Availability'),
                parentLayerParameterName = self.WAS, # parent layer 
                type=QgsProcessingParameterField.Any
            )
        )

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
            )
        )
    def processAlgorithm(self, parameters, context, model_feedback):

# ==================== Define Parameter =====================================   
        
        # enviromental services performance layer 
        IJH_Value = self.parameterAsString(parameters, self.IJH_V,context)

        # watershed area name 
        WAS_Name = self.parameterAsString(parameters,self.WAS_N,context)

        #field that contain water availability 
        WAS_Value = self.parameterAsString(parameters, self.WAS_V, context)

        # initialize progress bar
        feedback =  QgsProcessingMultiStepFeedback(9, model_feedback)

 # ==================== algoritm =====================================  
        
        # transform coordinates to epsg 4326
        feedback.setProgressText('Reproject All layer to EPSG 4326...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")


        grid_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['Grid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

 
        IJH_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['IJH'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        IJH_FIX = processing.run("native:fixgeometries", 
                                {'INPUT':IJH_rep['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})    

        WAS_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['WAS'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  

        WAS_FIX = processing.run("native:fixgeometries", 
                                {'INPUT':WAS_rep['OUTPUT'],
                                 'METHOD':0,
                                 'OUTPUT':'TEMPORARY_OUTPUT'})   


        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return{}
        
        # Intersect All Layer

        feedback.setProgressText('Intersect all layer ....')

        intr = processing.run("native:multiintersection", 
                       {'INPUT':IJH_FIX['OUTPUT'],
                        'OVERLAYS':[grid_rep['OUTPUT'],
                                    WAS_FIX['OUTPUT']],
                        'OVERLAY_FIELDS_PREFIX':'',
                        'OUTPUT':'TEMPORARY_OUTPUT'})
        
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        # calculate polygon area

        feedback.setProgressText('Calculate Area for each Feature...')

        feat_area = processing.run("native:fieldcalculator", 
                                {'INPUT':intr['OUTPUT'],
                                'FIELD_NAME':'area_feat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'$area',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return{}
        
        #calculate grid area

        feedback.setProgressText('Calculate Area for each Grid...')

        sum_by_id(feat_area, 'Grid_area', 'IMGSID', 'area_feat')

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return{}
        
        # calculate environmental services performance for each feature in grid

        feedback.setProgressText('Environmental services performance for each feature in grid...')

        IJH_layer = processing.run("native:fieldcalculator", 
                        {'INPUT':feat_area['OUTPUT'],
                        'FIELD_NAME':'IJH_feat',
                        'FIELD_TYPE':0,
                        'FIELD_LENGTH':30,
                        'FIELD_PRECISION':20,
                        'FORMULA':f'(area_feat/Grid_area)*{IJH_Value}',
                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return{}
        
        # Calculate enviromental services performances for each water shed

        feedback.setProgressText('Calculate enviromental services performance for each water shed...')

        sum_by_id(IJH_layer, 'WAS_IJH', WAS_Name, 'IJH_feat')

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return{}
        
        # calculate water availability for each polygon

        feedback.setProgressText('Calculate water availability for each polygon ... ')

        water_avl = processing.run("native:fieldcalculator", 
                        {'INPUT':IJH_layer['OUTPUT'],
                        'FIELD_NAME':'K_feat',
                        'FIELD_TYPE':0,
                        'FIELD_LENGTH':30,
                        'FIELD_PRECISION':20,
                        'FORMULA':f'(IJH_feat/WAS_IJH)*{WAS_Value}',
                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return{}
        
        #calcualte water availability for each grid 

        feedback.setProgressText('Calculate water availability for each grid ... ')

        sum_by_id(water_avl, 'K_Grid', 'IMGSID', 'K_feat')

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return{}
        
        # join attributes to grid layer 

        feedback.setProgressText('join attribute table to grid layer ... ')

        join = processing.run("native:joinattributestable", {'INPUT_2':water_avl['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':grid_rep['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return{}
        


# ==================== output parameter ===================================== 

        # initialization fields

        fields = QgsFields()
        fields.append(QgsField('IMGSID',QVariant.String,'',50))
        fields.append(QgsField('K_Grid', QVariant.Double, '', 50, 5))

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields,QgsWkbTypes.Polygon, epsg4326 )

        for feat in join['OUTPUT'].getFeatures():

            grid_id = feat['IMGSID']
            k = feat['K_grid']
            

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,k])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}  
class carcap2Algorithm(QgsProcessingAlgorithm):

    AVAIL = 'AVAIL'
    AVAIL_VAL= 'AVAIL_VAL'
    NEED = 'NEED'
    NEED_VAL = 'NEED_VAL'
    WN_STD = 'WN_STD'
    OUTPUT = 'OUTPUT'

    def name(self):
        return '3. Generate Water Need and Capacity Difference and Status'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Environmental Carrying Capacity (Water)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return carcap2Algorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  
        
        #input water needs layer 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.NEED,
                self.tr('Input Vector layer that contain water needs for each grid'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        #input water need value 
        self.addParameter(
            QgsProcessingParameterField(
                self.NEED_VAL,
                self.tr('Select Fields that Contains water needs for each grid'),
                parentLayerParameterName = self.NEED, # parent road layer
                type=QgsProcessingParameterField.Any
            )
        ) 

        # input water availability layer 
        
        self.addParameter(
        QgsProcessingParameterFeatureSource(
            self.AVAIL,
            self.tr('Input Vector layer that contain water availibility for each grid'),
            [QgsProcessing.TypeVectorPolygon]

            )
        )

        #input water availibility value 
        self.addParameter(
            QgsProcessingParameterField(
                self.AVAIL_VAL,
                self.tr('Select Fields that Contains water needs for each grid'),
                parentLayerParameterName = self.AVAIL, # parent road layer
                type=QgsProcessingParameterField.Any
            )
        )

        #Input water usage standard
        self.addParameter(
            QgsProcessingParameterNumber(
                self.WN_STD,
                self.tr("Input water needs for a decent life "),
                type = QgsProcessingParameterNumber.Double,
                minValue=1,
                defaultValue = 800,
                optional = False
            )
        )         

        # Output parameters
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
            )
        )


    def processAlgorithm(self, parameters, context, model_feedback):

# ==================== Define Parameter =====================================  

        #input water need value 
        wn_val = self.parameterAsString(parameters, self.NEED_VAL, context)

        #input water availability value 
        ava_val = self.parameterAsString(parameters, self.AVAIL_VAL, context)

        #input water usage standard 
        wn_stad = self.parameterAsDouble(parameters, self.WN_STD, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)    


 # ==================== algoritm ===================================== 
        
        join = processing.run("native:joinattributestable", {'INPUT_2':parameters['AVAIL'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':parameters['NEED'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        feedback.setProgressText('Calculate Difference between waterneeds and water availability...')

        diff =  processing.run("native:fieldcalculator", 
                                      {'INPUT':join['OUTPUT'],
                                       'FIELD_NAME':'diff',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':30,
                                       'FIELD_PRECISION':20,
                                       'FORMULA':f'{ava_val}-{wn_val}',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        

        stat = processing.run("native:fieldcalculator", 
                                      {'INPUT':diff['OUTPUT'],
                                       'FIELD_NAME':'Statues',
                                       'FIELD_TYPE':2,
                                       'FIELD_LENGTH':10,
                                       'FIELD_PRECISION':0,
                                       'FORMULA':"if(diff<=0, title('Not'),title('Exceed'))",
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        #progress set to 2
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        #calculate threshold person for each grid 
        feedback.setProgressText('Calculate threshold person for each grid... ')

        thres = processing.run("native:fieldcalculator", 
                                      {'INPUT':stat['OUTPUT'],
                                       'FIELD_NAME':'Threshold',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':f'(diff/{wn_stad})+Population',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 3
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
# ==================== output parameter =====================================  
        # Add all fields from the grid to the output layer
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('Population', QVariant.Int,'', 50))
        fields.append(QgsField('K_Grid', QVariant.Double, '', 50, 5))
        fields.append(QgsField('T_Grid', QVariant.Double, '', 50, 5)) 
        fields.append(QgsField("Difference", QVariant.Double, '', 50,5))
        fields.append(QgsField('Statues', QVariant.String, '', 50))
        fields.append(QgsField('Threshold', QVariant.Int,'', 50))

        # Output parameter
        output_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, output_crs)

        for feat in thres['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            popul = feat['Population']
            k = feat[f'{ava_val}']
            t = feat[f'{wn_val}']
            diff_1 = feat['diff']
            status = feat['Statues']
            threshold_1 = feat['Threshold']

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,popul,k,t,diff_1,status,threshold_1])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        
        return {self.OUTPUT: dest_id}

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