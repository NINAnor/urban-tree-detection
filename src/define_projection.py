import arcpy
from arcpy import env

from os import listdir
from os.path import isfile, join

env.workspace = r"P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Zofie\synergi_3_tree_accounts\DATA\las_3"
las_files_list = [f for f in listdir(env.workspace) if f.endswith('.las')]

for las_file in las_files_list:
    arcpy.AddMessage(las_file)
    arcpy.management.DefineProjection(
        las_file, 'PROJCS["ETRS_1989_UTM_Zone_32N",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",9.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
    )