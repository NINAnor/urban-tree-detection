"""util functions for working with arcpy."""
import arcpy

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
    
    
# Join "source_table" to "destination table" and copy attributes from "source table" to attributes in "destination table"
def join_and_copy(t_dest:str, join_a_dest:str, t_src:str, join_a_src:str, a_src:list, a_dest:list):
    """_summary_

    Args:
        t_dest (str): destinatation table (in_table)
        join_a_dest (str): destination field (in_field)
        t_src (str): source table (join_table)
        join_a_src (str): source field (join_field)
        a_src (list): source list of fields (join_field_list)
        a_dest (str): destination list of fields (in_field_list)
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

# --------------------------------------------------------------------------- #
# Join table 2 to table 1 and copy src field from table 2 to dest. field in table 1
# TODO check this function and remove 
# --------------------------------------------------------------------------- #

def join_and_copy2(target_table, key_target, join_table, key_join, field_list_join, field_list_target):
     
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