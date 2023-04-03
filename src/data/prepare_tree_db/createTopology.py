# create filegdb 
# create featureset
# create topology
# make sure XML database all in utm33n
# make XML database for utm32

# set topology rules 
# Must Be Properly Inside Polygons
# Delete Feature Delete removes point features that are not properly within polygon features.


arcpy.management.CreateTopology(
    in_dataset=r"P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\treeDetection\data\municipality_urban_trees.gdb\urban_trees",
    out_name="tree_topology",
    in_cluster_tolerance=None
)


import arcpy
from arcpy import env

# Set the workspace to the FileGDB containing the topology
env.workspace = r"path\to\filegdb.gdb"

# Open the topology and export the errors to a feature class
topology_name = "my_topology"
topology = arcpy.Describe(topology_name).topology
error_fc = r"in_memory\topology_errors"
arcpy.ExportTopologyErrors_management(topology, error_fc, "ERROR")

# Create a dictionary to hold the fix types for each topology rule
fixes = {
    "Must Be Properly Inside Polygons": "snap",
    "Must Contain": "add"
}



env.workspace = "path/to/FileGDB"
topology_name = "topology_name"
topology = arcpy.Describe(topology_name).topology

error_fc = "path/to/error_fc"
arcpy.ExportTopologyErrors_management(topology, error_fc, "ERROR")


# Iterate over the topology errors and apply fixes as needed
with arcpy.da.UpdateCursor(error_fc, ["RuleDescription", "FeatureClass1", "FeatureClass2", "OriginObjectID", "DestinationObjectID"]) as cursor:
    for row in cursor:
        rule = row[0]
        fc1 = row[1]
        fc2 = row[2]
        origin_id = row[3]
        dest_id = row[4]
        fix_type = fixes.get(rule, None)
        if fix_type == "snap":
            
            # Snap the point to the nearest edge of the polygon
            polygon_fc = fc1 if arcpy.Describe(fc1).shapeType == "Polygon" else fc2
            point_fc = fc2 if fc1 == polygon_fc else fc1
            polygon_desc = arcpy.Describe(polygon_fc)
            point_desc = arcpy.Describe(point_fc)
            polygon_spatial_ref = polygon_desc.spatialReference
            point_spatial_ref = point_desc.spatialReference
            
            if not polygon_spatial_ref.equals(point_spatial_ref):
                # If the spatial references are not equal, project the point to the polygon's coordinate system
                point_geom = arcpy.PointGeometry(point_desc.shape, point_spatial_ref).projectAs(polygon_spatial_ref)
            else:
                point_geom = arcpy.PointGeometry(point_desc.shape)
            snapped_point = point_geom.snapToBoundary(polygon_desc.shape)[0]
            # Update the point feature with the new geometry
            arcpy.da.UpdateCursor(point_fc, ["SHAPE@"], f"OBJECTID = {origin_id}")[0][0] = snapped_point
        elif fix_type == "add":
            # Add a new point to the polygon's interior
            polygon_fc = fc1 if arcpy.Describe(fc1).shapeType == "Polygon" else fc2
            point_fc = fc2 if fc1 == polygon_fc else fc1
            polygon_desc = arcpy.Describe(polygon_fc)
            point_desc = arcpy.Describe(point_fc)
            polygon_spatial_ref = polygon_desc.spatialReference
            point_spatial_ref = point_desc.spatialReference
            if not polygon_spatial_ref.equals(point_spatial_ref):
                # If the spatial references are not equal, project the point to the polygon's coordinate system
                point_geom = arcpy.PointGeometry(point_desc.shape, point_spatial_ref).projectAs(polygon_spatial_ref)
            else:
                point_geom = arcpy.PointGeometry(point_desc.shape)
            # Add the point to the polygon's interior
            arcpy.AddField_management(polygon_fc, "ORIG_FID", "LONG")
            arcpy.CalculateField_management(polygon_fc, "ORIG_FID", f"{point_fc}.OBJECTID", "PYTHON")
            arcpy.FeatureToPoint_management(polygon_fc, r"in_memory\temp_point", "INSIDE")
            arcpy.JoinField_management(r"in
