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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsCoordinateTransform,
                       QgsProcessingMultiStepFeedback,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
                       QgsFeature,
                       QgsProcessingParameterNumber,
                       QgsFields,QgsField,QgsWkbTypes,
                       )
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import (QCoreApplication,QVariant)
import processing
import math

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
        return 'Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return calcenergyAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.popgrid,
                self.tr('Population per Grid Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.popfield,
                self.tr('Select Fields that Contains Population Count'),
                parentLayerParameterName=self.popgrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.AKE,
                self.tr('Insert Energy Sufficiency Number'),
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
        # input population layer 
        pop_layer = self.parameterAsSource(parameters, self.popgrid,context)

        # input popfield from population layer
        pop_field = self.parameterAsString(parameters, self.popfield,context)

        # AKE number
        AKE_number = self.parameterAsString(parameters, self.AKE, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(22, feedback)
        
 # ==================== algoritm =====================================  
        # transform coordinates to epsg 4326
        feedback.setProgressText('Reproject All layer to EPSG 4326...')
        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        reproject = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['popgrid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        

        
        #calculate total weigth for each grid
        feedback.setProgressText('Calculate grid AKE for each year... ')

        AKE_Count = processing.run("native:fieldcalculator", 
                                      {'INPUT':reproject['OUTPUT'],
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
        return 'Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return distavailabilityAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.grid,
                self.tr('Grid Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.admlay,
                self.tr('Administration Boundary Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.admfield,
                self.tr('Select Fields that Contains Administrative Name from Administrative Boundary Layer'),
                parentLayerParameterName=self.admlay,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.enerfield,
                self.tr('Select Fields that Contains Energy Production from Administrative Boundary Layer'),
                parentLayerParameterName=self.admlay,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ESPlay,
                self.tr('Environment Service Performance Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.IJEPBPESP,
                self.tr('Select Fields that Contains IJEPBP Value'),
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
        # input population layer 
        grid_layer = self.parameterAsSource(parameters, self.grid,context)

        # input IJEPBP field per grid
        IJEPBP_field = self.parameterAsString(parameters, self.IJEPBPESP,context)

        # Administration Boundary
        adm_layer = self.parameterAsSource(parameters, self.admlay, context)

        # Administration boundary name field
        adm_field = self.parameterAsString(parameters, self.admfield, context)

        # Energy Production from Administrative Boundary Layer
        ener_field = self.parameterAsString(parameters, self.enerfield, context)

        # input ecoregion layer 
        ESP_layer = self.parameterAsSource(parameters, self.ESPlay,context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(10, feedback)
        
 # ==================== algoritm =====================================  
        # transform coordinates to epsg 4326
        feedback.setProgressText('Reproject All layer to EPSG 4326...')

        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

        grid_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['grid'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

 
        adm_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['admlay'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})  
        
        ESP_rep = processing.run("native:reprojectlayer",
                                        {'INPUT':parameters['ESPlay'],
                                        'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:4326'),
                                        'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})              

        #progress set to 1
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
    #INTERSECTION
        feedback.setProgressText('Intersections')

        intr = processing.run("native:multiintersection", 
                       {'INPUT':ESP_rep['OUTPUT'],
                        'OVERLAYS':[grid_rep['OUTPUT'],
                                    adm_rep['OUTPUT']],
                        'OVERLAY_FIELDS_PREFIX':'',
                        'OUTPUT':'TEMPORARY_OUTPUT'})
        
        #progress set to 2
        feedback.setCurrentStep(2)
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
        
        #progress set to 3
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

#calculate sum area by id
        feedback.setProgressText('Calculate Total Area Feature for each grid ...')

        sum_by_id(feat_area, 'sum_area', 'IMGSID', 'area_feat')

        #progress set to 4
        feedback.setCurrentStep(4)
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
        
        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

#calculate sum IJEPBP by administrative boundary
        feedback.setProgressText('Calculate sum IJEPBP by administrative boundary ...')

        sum_by_id(IJEPBP_feat, 'IJEPBP_adm', adm_field, 'IJEPBPfeat')

        #progress set to 6
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

# Calculate 1IJEPBP
        feedback.setProgressText('Calculate 1IJEPBP ...')

        SATUIJEPBP = processing.run("native:fieldcalculator", 
                                {'INPUT':IJEPBP_feat['OUTPUT'],
                                'FIELD_NAME':'satIJEPBP',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'{ener_field}/IJEPBP_adm',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 7
        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

# Calculate Energy
        feedback.setProgressText('Calculate Energy Per Feature ...')

        EnergyCalc = processing.run("native:fieldcalculator", 
                                {'INPUT':SATUIJEPBP['OUTPUT'],
                                'FIELD_NAME':'Energy_Available',
                                'FIELD_TYPE':0,
                                'FIELD_LENGTH':30,
                                'FIELD_PRECISION':20,
                                'FORMULA':f'IJEPBPfeat*satIJEPBP',
                                'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 8
        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

#calculate sum area by id
        feedback.setProgressText('Calculate Total Energy Available for each grid ...')

        sum_by_id(EnergyCalc, 'EnerAvai', 'IMGSID', 'Energy_Available')

        #progress set to 9
        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

# join attributes to grid layer 

        feedback.setProgressText('join attribute table to grid layer ... ')

        join = processing.run("native:joinattributestable", {'INPUT_2':EnergyCalc['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':parameters['grid'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':False,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return{}

# ==================== output parameter =====================================  

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('EnerAvai', QVariant.Int,'', 50))
        fields.append(QgsField('IJEPBP_Adm', QVariant.Int,'', 50))
        fields.append(QgsField('IJEPBPfeat', QVariant.Int,'', 50))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in join['OUTPUT'].getFeatures():
            grid_id = feat['IMGSID']
            energy_available = feat['EnerAvai']
            IJEPBPADM = feat['IJEPBP_Adm']
            IJEPBPFEATURE = feat['IJEPBPfeat']

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([grid_id,energy_available,IJEPBPADM,IJEPBPFEATURE])
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
        

        return {self.OUTPUT: dest_id}
      
class carcapAlgorithm(QgsProcessingAlgorithm):

    OUTPUT = 'OUTPUT'
    needgrid = 'needgrid'
    needfield = 'needfield'
    avagrid = 'avagrid'
    avafield = 'avafield'
    populgrid = 'populgrid'
    populfield = 'populfield'
    AKE = 'AKE'

    def name(self):
        return '3. Calculate Energy Needs and Availability Difference and Status'

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return 'Environmental Carrying Capacity (Food)'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return carcapAlgorithm()


    def initAlgorithm(self, config):
# ====================  Parameter =====================================  

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.needgrid,
                self.tr('Energy Needs Grid Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.needfield,
                self.tr('Select Fields that Contains Energy Needs per Grid'),
                parentLayerParameterName=self.needgrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.avagrid,
                self.tr('Energy Availability Grid Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.avafield,
                self.tr('Select Fields that Contains Energy Availability per Grid'),
                parentLayerParameterName=self.avagrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.populgrid,
                self.tr('Population Grid Layer'),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.populfield,
                self.tr('Select Fields that Contains Population per Grid'),
                parentLayerParameterName=self.populgrid,  # Set the parent layer parameter
                type=QgsProcessingParameterField.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.AKE,
                self.tr('Insert Energy Sufficiency Number'),
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
        # input population layer 
        need_layer = self.parameterAsSource(parameters, self.needgrid,context)

        # input popfield from population layer
        need_field = self.parameterAsString(parameters, self.needfield,context)

        # input population layer 
        ava_layer = self.parameterAsSource(parameters, self.avagrid,context)

        # input popfield from population layer
        ava_field = self.parameterAsString(parameters, self.avafield,context)

        # input population layer 
        popul_layer = self.parameterAsSource(parameters, self.populgrid,context)

        # input popfield from population layer
        popul_field = self.parameterAsString(parameters, self.populfield,context)

        # AKE number
        AKE_number = self.parameterAsString(parameters, self.AKE, context)

        #initialize progress bar
        feedback = QgsProcessingMultiStepFeedback(22, feedback)
        
 # ==================== algoritm =====================================  
        
        epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")

# join attributes to grid layer 

        feedback.setProgressText('join attribute table to grid layer ... ')


        joinn = processing.run("native:joinattributestable", {'INPUT_2': parameters['needgrid'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':parameters['avagrid'],
                                                      'FIELD':'IMGSID',
                                                      'FIELDS_TO_COPY':[],
                                                      'METHOD':1,
                                                      'DISCARD_NONMATCHING':True,
                                                      'PREFIX':'',
                                                      'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})

        join = processing.run("native:joinattributestable", {'INPUT_2': joinn['OUTPUT'],
                                                      'FIELD_2':'IMGSID',
                                                      'INPUT':parameters['populgrid'],
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
                                       'FORMULA':f'{ava_field} / (365 * {AKE_number}) ',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 4
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

#calculate difference
        feedback.setProgressText('Calculate carrying capacity status ... ')

        status = processing.run("native:fieldcalculator", 
                                      {'INPUT':threshold['OUTPUT'],
                                       'FIELD_NAME':'Status',
                                       'FIELD_TYPE':0,
                                       'FIELD_LENGTH':20,
                                       'FIELD_PRECISION':15,
                                       'FORMULA':f'Thres - {popul_field}',
                                       'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT})
        
        #progress set to 5
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}





# ==================== output parameter =====================================  

        # initialization fields
        fields = QgsFields()
        fields.append(QgsField('IMGSID', QVariant.String, '', 50))
        fields.append(QgsField('Diff', QVariant.Double, '', 50))
        fields.append(QgsField('Thres', QVariant.Double,'', 50))
        fields.append(QgsField('Status', QVariant.Double,'', 50))

        # Output parameter
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, QgsWkbTypes.Polygon, epsg4326)

        for feat in status['OUTPUT'].getFeatures():
            IMGSID = feat['IMGSID']
            Diff = feat['Diff']
            Thres = feat['Thres']
            Status = feat['Status']
            

            new_feat = QgsFeature(feat)
            new_feat.setAttributes([IMGSID,Diff,Thres,Status])
            
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