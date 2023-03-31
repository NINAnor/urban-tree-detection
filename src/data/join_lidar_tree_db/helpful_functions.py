"""
NAME:    Useful functions

AUTHOR(S): Zofie Cimburova < zofie.cimburova AT nina.no>
"""

"""
To Dos:
"""

import arcpy
import math  
import itertools  
import datetime  
 
# =========================== #
# Check if field exists
# =========================== #
def FieldExist(featureclass, fieldname):
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
 
    if (fieldCount == 1):
        return True
    else:
        return False
 
         
# =========================== #
# Add field if not already exists
# =========================== #
def AddFieldIfNotexists(featureclass, fieldname, type):
    if (not FieldExist(featureclass, fieldname)):
        arcpy.AddField_management(featureclass, fieldname, type)
          
          
# =========================== #
# Join table 2 to table 1 and copy source field from table 2 to destination field of table 1
# =========================== #
def join_and_copy(target_table, key_target, join_table, key_join, field_list_join, field_list_target):
     
    name1 = arcpy.Describe(target_table).name
    name2 = arcpy.Describe(join_table).name
     
    # 1. create layer from target_table
    layer1 = "table1_lyr"
    arcpy.MakeFeatureLayer_management(target_table, layer1)
     
    # 2. create Join
    arcpy.AddJoin_management(layer1, key_target, join_table, key_join)
            
    i = 0
    for source_field in field_list_join:
        arcpy.AddMessage("Copying values from " + name2 +  "." + field_list_join[i] + " to " + name1 + "." + field_list_target[i])
        arcpy.CalculateField_management(layer1, name1 + "." + field_list_target[i], "[" + name2 + "." + field_list_join[i] + "]")
        i = i+1
        