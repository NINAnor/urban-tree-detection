"""util functions for working with arcpy."""
import arcpy
import os

# --------------------------------------------------------------------------- #
# LOOKUP AND RECLASSIY/RENAME FUNCTIONS
# --------------------------------------------------------------------------- #

def df_to_lookupDict(df, key, value):
    lookup_dict = {}
    for index, row in df.iterrows():
        lookup_dict[row[key]] = row[value]
    return lookup_dict

def reclassify_row(fc, field_to_check, field_to_modify, lookup_dict):
    """Reclassifies values in a specified field based on a lookup table.

    Args:
        fc (str): The path to the feature class.
        field_to_check (str): The name of the field to check against the lookup table.
        field_to_modify (str): The name of the field to modify based on the lookup table.
        lookup_dict (dict): A dictionary object containing lookup values as keys and their corresponding new values as values.
    """
    # Create a case-insensitive dictionary for the lookup values
    lookup_dict_case_insensitive = {k.lower(): v for k, v in lookup_dict.items()}

    # Create an update cursor to modify the values in the field
    fields = [field_to_check, field_to_modify]
    #sql_clause = f"{field_to_check} IS NOT NULL"
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            lookup_value = lookup_dict_case_insensitive.get(str(row[0]).lower())
            if lookup_value is not None:
                row[1] = lookup_value
                cursor.updateRow(row)
                #print(f"Reclassified value <{row[0]}> to value <{lookup_value}>") 

    # Print a message indicating the update is complete
    print(f"The rows in <{field_to_modify}> are reclassified.")
    
# --------------------------------------------------------------------------- #
# JOIN/MERGE/EXTRACT FUNCTIONS
# --------------------------------------------------------------------------- #

def join_and_copy(t_dest:str, join_a_dest:str, t_src:str, join_a_src:str, a_src:list, a_dest:list):
    """ 
    Join "source_table" to "destination table" and copy attributes from "source table" 
    to attributes in "destination table".

    Args:
        t_dest (str): destinatation table, table view to wich the join will be added.  
        join_a_dest (str): destination field, the field in the dst table on which the join will be based. 
        t_src (str): source table (join table), the table view to be joined to the destination table.
        join_a_src (str): source field (join field), the field in the source table on which the join will be based.
        a_src (list): source list of fields (join field list), the list of fields to be copied from the source table to the destination table.
        a_dest (str): destination list of fields, the name of the source fields to where the copied values will be stored in the destination table.
    """
     
    name_dest = arcpy.Describe(t_dest).name
    name_src = arcpy.Describe(t_src).name
     
    # Create layer from "destination table"
    l_dest = "dest_lyr"
    arcpy.MakeFeatureLayer_management(t_dest, l_dest)
     
    # Join
    arcpy.AddJoin_management(l_dest, join_a_dest, t_src, join_a_src)
    

    
    # Copy attributes   
    for src_field, dest_field in zip(a_src, a_dest):
        arcpy.AddMessage(
            "\tCopying values from " + name_src +  "." + src_field + " to " + name_dest + "." + dest_field
        )
        arcpy.CalculateField_management(
            l_dest, 
            name_dest + "." + dest_field, 
            "!" + name_src + "." + src_field + "!"
        )
        

def extractFeatures_byID(target_feature:str, id_feature:str, output_feature:str, id_field:str):
    """
    This function extracts features from a feature lyr based on a list 
    of unique IDs derived from another feature lyr.

    Args:
        target_feature (str): Target feature layer path
        id_feature (str): Path to the layer that contains the selecting ids
        output_feature (str): Output feature layer path 
    """    
    # Get unique IDs from the id_feature layer
    ids = set(row[0] for row in arcpy.da.SearchCursor(id_feature, id_field))
    sorted_ids = sorted(list(ids))
    print("number of ids:", len(sorted_ids))

    # Select the features in the target layer if the ID is in the ID_list  
    where_clause = f"{id_field} IN ({','.join(map(str, sorted_ids))})"
    selected_layer = arcpy.management.MakeFeatureLayer(target_feature, "selected_layer", where_clause)
    
    # Copy the selected features to the output feature layer
    arcpy.management.CopyFeatures(selected_layer, output_feature)

# --------------------------------------------------------------------------- #
# ifNotExists or ifEmpty FUNCTIONS
# --------------------------------------------------------------------------- #

def createGDB_ifNotExists(filegdb_path:str):
    """
    Checks if a fileGDB exists and if not creates this fileGDB
    
    Args:
        filegdb_path (str): path to the fileGDB
    """
    filegdb_name = os.path.basename(filegdb_path)
    if arcpy.Exists(filegdb_path):
        arcpy.AddMessage("\tFileGDB {} already exists. Continue...".format(filegdb_name))
    else:
        dir_path = os.path.dirname(filegdb_path)
        arcpy.management.CreateFileGDB(dir_path, filegdb_name)
        
def copyFeature_ifNotExists(in_fc:str, out_fc:str):
    """
    Checks if a feature exists in a file GDB and if not copies this feature

    Args:
        in_fc (str): path to the input feature (that will be copied.) 
        out_fc (str): path to the output feature 
    """
    if arcpy.Exists(out_fc):
        arcpy.AddMessage(f"\tFeature {os.path.basename(out_fc)} already exists. Continue...")
    else:
        arcpy.management.CopyFeatures(in_fc, out_fc)

        
def fieldExist(featureclass:str, fieldname:str):
    """
    Check if an attribute field exists

    Args:
        featureclass (str): The path to the feature class.
        fieldname (str): The name of the field to check.

    Returns:
        bool: True if the field exists, False otherwise. 
    """  
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
 
    if (fieldCount == 1):
        return True
    else:
        return False   

def addField_ifNotExists(featureclass:str, fieldname:str, type:str):
    """
    Adds a field to a feature class if the field does not already exist.

    Args:
        featureclass (str): The path to the feature class.
        fieldname (str): The name of the field to add.
        type (str): The data type of the field to add.
    """    
    if (not fieldExist(featureclass, fieldname)):
        arcpy.AddField_management(featureclass, fieldname, type)
        
def calculateField_ifEmpty(in_table:str, field:str, expression:str, code_block=""):
    """
    Check if a field in a table contains any null or empty values. If so, recalculate the field using the provided
    expression and code block.

    Args:
        in_table (str): The input table.
        field (str): The field to check and calculate.
        expression (str): The expression to use for the calculation.
        code_block (str, optional): The code block to use for the calculation. Defaults to "".
    """
    # Check if column contains any null or empty values
    with arcpy.da.SearchCursor(in_table, [field]) as cursor:
        has_nulls = False
        for row in cursor:
            if row[0] is None or row[0] == "":
                has_nulls = True
                break

    # If the column contains null or empty values, recalculate it
    if has_nulls:
        arcpy.management.CalculateField(
            in_table=in_table,
            field=field,
            expression=expression,
            expression_type="PYTHON_9.3",
            code_block=code_block
        )
        arcpy.AddMessage(f"\tThe Column <{field}> has been recalculated.")
    else:
        arcpy.AddMessage(f"\tThe Column <{field}> does not contain null or empty values.")


def check_isNull(in_table:str, field:str) -> bool:
    """
    Checks if a specified field in a feature class contains any null or empty values.
    
    Args:
    fc (str): The path to the feature class to check.
    field (str): The name of the field to check for null or empty values.
    
    Returns:
    True if there are null or empty values in the field, False otherwise.
    """
    
    with arcpy.da.SearchCursor(in_table, [field]) as cursor:
        null_count = 0
        for row in cursor:
            if row[0] is None:
                null_count += 1
            if row[0] == "":
                null_count += 1
            if row[0] == "null values":
                null_count +=1
                
        arcpy.AddMessage(f"\tThe count of Null values in {field} is: {null_count}") 
        if null_count == 0:
            arcpy.AddMessage("\tThe field is already populated. Continue..")
            return False
        else:
            arcpy.AddMessage("\tThe field contains null values. Recalculate...")
            return True


def deleteFields(in_table, out_table, keep_list):
    """Deletes all fields from a table except required fields 
    and those in the keep_list.

    Args:
        in_table (str): path to the input table
        keep_list (str): list of fields to keep
    """        
    # Describe the input (need to test the dataset and data types)
    desc = arcpy.Describe(in_table)

    # Make a copy of the input (so you can maintain the original as is)
    if desc.datasetType == "FeatureClass":
        arcpy.CopyFeatures_management(in_table, out_table)
    else:
        arcpy.CopyRows_management(in_table, out_table)
    
    fieldObj_list = arcpy.ListFields(out_table)

    # Create an empty list that will be populated with field names        
    field_list = []

    for field in fieldObj_list:
        if not field.required and field.name not in keep_list:
            field_list.append(field.name)  
    
    # dBASE tables require a field other than an OID and Shape. If this is
    # the case, retain an extra field (the first one in the original list        
    if desc.dataType in ["ShapeFile", "DbaseTable"]:
        field_list = field_list[1:]

    print(f"Keep the fields: {keep_list}.")
    print(f"Delete the fields: {field_list}.")
    arcpy.DeleteField_management(out_table, field_list)

