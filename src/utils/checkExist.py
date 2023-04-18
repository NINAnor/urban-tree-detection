import arcpy
import os

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
