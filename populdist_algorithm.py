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

from qgis.core import (QgsProcessingAlgorithm, 
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessing,
                        QgsProcessingParameterField,
                        QgsProcessingMultiStepFeedback,
                        QgsFields,
                        QgsField,
                        QgsCoordinateReferenceSystem,
                        QgsCoordinateTransform,
                        QgsProject,
                        QgsWkbTypes,
                        QgsFeatureSink,
                        QgsFeature,
                        QgsFeatureRequest
                        )

from qgis.PyQt.QtCore import QUrl
import os
from qgis.PyQt.QtGui import QIcon
import processing
import geopandas as gpd

class PopulDistAlgorithm(QgsProcessingAlgorithm):



    INPUT = 'INPUT' #grid input
    lc_layer = 'LC_LAYER' # landcover layer
    TableWeightLC ='TableWeightLC' # landcover weights table
    rt_layer = 'RT_LAYER' # road layer
    TableWeightRT ='TableWeightRT' # road weights table
    INPUTA ='INPUTA' # admin boundary layer
    INPUTAT ='INPUTAT' # admin boundart field
    INPUTPOP ='INPUTPOP' # population field 
    OUTPUT = 'OUTPUT' # output population grid


    def __init__(self):
        super().__init__()

    def name(self):
        return 'Distribute Populations to Grid'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Population'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/populdist.png'))

    def createInstance(self):
        return PopulDistAlgorithm()
    
    def initAlgorithm(self, config=None):
 # ====================  Parameter =====================================  
        
        #input grid 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Grid Layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # input landcover layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.lc_layer,
                self.tr('Input Landcover Layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        #input weight landcover layer
        self.addParameter(
            QgsProcessingParameterField(
                self.TableWeightLC,
                self.tr('Select Fields that Contains Weight for landcover'),
                parentLayerParameterName = self.lc_layer, # parent landcover layer
                type=QgsProcessingParameterField.Any
            )
        )

        # input road layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.rt_layer,
                self.tr('Input Road Layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        #input weight Road layer
        self.addParameter(
            QgsProcessingParameterField(
                self.TableWeightRT,
                self.tr('Select Fields that Contains Weight for road'),
                parentLayerParameterName = self.rt_layer, # parent road layer
                type=QgsProcessingParameterField.Any
            )
        )      

        # Administrative Boundaries Input Parameters
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUTA,
                self.tr('Input Administrative Boundaries Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        # Input administrative boundary field
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUTAT,
                self.tr('Select Fields that Contains Administrative Boundaries Name'),
                parentLayerParameterName=self.INPUTA,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        # Input population on administrative boundary
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUTPOP,
                self.tr('Select Fields that Contains Population from Administrative Boundaries Layer'),
                parentLayerParameterName=self.INPUTA,  # Set the parent layer parameter
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
        # input grid layer 
        grid_layer = self.parameterAsSource(parameters, self.INPUT,context)

        # landcover layer    
        lc = self.parameterAsSource(parameters,self.lc_layer, context)

        #input field that contain landcover weight 
        lc_weight = self.parameterAsString(parameters, self.TableWeightLC,context)

        # road layer    
        rt = self.parameterAsSource(parameters,self.rt_layer, context)

        #input field that contain road weight 
        rt_weight = self.parameterAsString(parameters, self.TableWeightRT,context)

        # input admin boundary
        admin_layer = self.parameterAsSource(parameters, self.INPUTA, context)

        #input admin field that contain admin boudary
        admin_field = self.parameterAsString(parameters, self.INPUTAT,context)

        #input admin field that contain population
        popul_field = self.parameterAsString(parameters, self.INPUTPOP,context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(22, feedback) 

# ==================== algoritm =====================================  

        # transform coordinates to epsg 4326
        feedback.setProgressText('Reproject All layer to EPSG 4326...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")
        grid_crs = grid_layer.sourceCrs()
        lc_crs = lc.sourceCrs()
        rt_crs = rt.sourceCrs()
        admin_crs = admin_layer.sourceCrs() 


        grid_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['INPUT'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  

        lc_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['lc_layer'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  
        
        rt_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['rt_layer'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  

        admin_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['INPUTA'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  


        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return{}
        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        # Intersect road
        feedback.setProgressText('Intersect Road with Grid Layer...')

        intr_road = processing.run("native:intersection", 
                                  {'INPUT':rt_rep['OUTPUT'], 
                                   'OVERLAY':grid_rep['OUTPUT'],
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})
        
        #progress set to 2
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        # calculate length for each feature in road layer
        feedback.setProgressText('Calulate Length for each feature in road layer...')

        feat_length = processing.run("native:fieldcalculator", 
                                {'INPUT':intr_road['OUTPUT'],
                                'FIELD_NAME':'length_feat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'$length',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 3
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
        #calculate sum length by id
        feedback.setProgressText('Calculate Total Length Feature for each grid ...')

        sum_by_id(feat_length, 'Grid_length', 'IMGSID', 'length_feat' )
    
        # Set progress to 4
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return{}
        
        # calculate feature weight for each grid
        feedback.setProgressText('Calculate Feature Weight for each grid ...')

        w_rt_f =  processing.run("native:fieldcalculator", 
                                      {'INPUT':feat_length['OUTPUT'],
                                       'FIELD_NAME':'Wrt_f',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':30,
                                       'FIELD_PRECISION':20,
                                       'FORMULA':f'(length_feat/Grid_length) * {rt_weight} ',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}
        
        #calculate sum by id road
        feedback.setProgressText('Sum by ID Road Layer ...')

        sum_by_id(w_rt_f, 'WRT', 'IMGSID', 'Wrt_f')

        #progress set to 6
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}
        
        # join value to grid
        feedback.setProgressText('Join Value by Field Road Layer...')

        join = processing.run("native:joinattributestable", {'INPUT_2':w_rt_f['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':grid_rep['OUTPUT'],
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
        
        # Intersect land cover
        feedback.setProgressText('Intersect Land Cover with Grid Layer...')

        intr_Lc = processing.run("native:intersection", 
                                  {'INPUT':lc_rep['OUTPUT'], 
                                   'OVERLAY':grid_rep['OUTPUT'],
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})
        
        #progress set to 8
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}
        
        # calculate area for each feature in road layer
        feedback.setProgressText('Calulate Area for each feature in road layer...')

        feat_area = processing.run("native:fieldcalculator", 
                                {'INPUT':intr_Lc['OUTPUT'],
                                'FIELD_NAME':'area_feat',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':'$area',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 9
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}
        
        #calculate sum area by id
        feedback.setProgressText('Calculate Total Area Feature for each grid ...')

        sum_by_id(feat_area, 'Grid_area', 'IMGSID', 'area_feat')

        #progress set to 10
        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}
        
        # calculate feature weight for each grid
        feedback.setProgressText('Calculate Feature Weight for each grid ...')

        w_lc_f =  processing.run("native:fieldcalculator", 
                                      {'INPUT':feat_area['OUTPUT'],
                                       'FIELD_NAME':'Wlc_f',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':30,
                                       'FIELD_PRECISION':20,
                                       'FORMULA':f'(area_feat/Grid_area) * {lc_weight} ',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        #progress set to 11
        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}
        
        #calculate sum by id road
        feedback.setProgressText('Sum by ID Landcover Layer ...')

        sum_by_id(w_lc_f, 'WLC', 'IMGSID', 'Wlc_f')

        #progress set to 12
        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}
        
        # join value to grid
        feedback.setProgressText('Join Value by Field LandCover Layer...')

        join_2 = processing.run("native:joinattributestable", {'INPUT_2':w_lc_f['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':join['OUTPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 13
        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}
        
        # intersect admin boundary
        feedback.setProgressText('Intersect Grid Layer with Admin Boundary ... ')

        intr_Ad = processing.run("native:intersection", 
                                  {'INPUT':admin_rep['OUTPUT'], 
                                   'OVERLAY':join_2['OUTPUT'],
                                   'INPUT_FIELDS':[],
                                   'OVERLAY_FIELDS':[],
                                   'OVERLAY_FIELDS_PREFIX':'',
                                   'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT,
                                   'GRID_SIZE':None})
        
        #progress set to 14
        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}
        
        #calculate area admin
        feedback.setProgressText('Calculate area for each feature in grid... ')

        area_admin = processing.run("native:fieldcalculator", 
                                      {'INPUT':intr_Ad['OUTPUT'],
                                       'FIELD_NAME':'a_admin',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':'$area',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 15
        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}
                
        #calculate sum area by id
        feedback.setProgressText('Calculate total area for each feature in grid... ')

        sum_by_id(area_admin, 'tot_area', 'IMGSID', 'a_admin')

        #progress set to 16
        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}
        
        #calculate total weigth for each grid
        feedback.setProgressText('Calculate total weight for each grid... ')

        W_grid = processing.run("native:fieldcalculator", 
                                      {'INPUT':area_admin['OUTPUT'],
                                       'FIELD_NAME':'weight_grid',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':'(WLC+WRT)*(a_admin/tot_area)',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 17
        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}
        
        #calculate total weigth for each admin boundary
        feedback.setProgressText('Calculate Total Weight for each admin boundary... ')

        sum_by_id(W_grid, 'W_admin', admin_field, 'weight_grid')

        #progress set to 18
        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}
        
        #calculate population for each grid
        feedback.setProgressText('Calculate Population For Each Grid... ')

        popul_grid = processing.run("native:fieldcalculator", 
                                {'INPUT':W_grid['OUTPUT'],
                                'FIELD_NAME':'popul_grid',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':20,
                                'FIELD_PRECISION':15,
                                'FORMULA':f'(weight_grid/W_admin)*{popul_field}',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 19
        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}
        
        #Sum by id population
        feedback.setProgressText('Calculate Sum population by IMGSID... ')

        sum_by_id(popul_grid, 'popul', 'IMGSID', 'popul_grid')

        #progress set to 20
        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}
        
        # join value to grid
        feedback.setProgressText('Join Value by Field (population)...')
        
        join_3 = processing.run("native:joinattributestable", {'INPUT_2':popul_grid['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':parameters['INPUT'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 21
        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # remove null from population
        feedback.setProgressText('Remove Null From Population Field ...')

        popul_null =processing.run("native:fieldcalculator", 
                                      {'INPUT':join_3['OUTPUT'],
                                       'FIELD_NAME':'Population',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':'if("popul" is null, 0, "popul")',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 22
        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {} 

        # ==================== output parameter =====================================

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('WRT', QVariant.Double, '', 50, 4))
        fields.append(QgsField('WLC', QVariant.Double, '', 50, 5))
        fields.append(QgsField('Population', QVariant.Double,'', 50, 5))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in popul_null['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            length = feat['WRT']
            area = feat['WLC']
            popul = feat['Population']
            

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,length,area,popul])
            
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












