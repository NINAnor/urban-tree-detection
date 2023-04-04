import arcpy

# Join "source_table" to "destination table" and copy attributes from "source table" to attributes in "destination table"
def join_and_copy(t_dest, join_a_dest, t_src, join_a_src, a_src, a_dest):
     
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
              

# =========================== #
# Join table 2 to table 1 and copy source field from table 2 to destination field of table 1
# =========================== #
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