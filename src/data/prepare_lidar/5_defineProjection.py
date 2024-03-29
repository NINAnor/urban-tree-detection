import os
from os import listdir

import arcpy
import dotenv
from arcpy import env
from dotenv import dotenv_values

# filepath
# bodo (utm33); baerum (utm32); kristiansand (utm32)

kommune = "kristiansand"

# search for .env file in USER directory
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, "trekroner.env")

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)

# project data path variables
DATA_PATH = os.getenv("DATA_PATH")
las_dir = os.path.join(DATA_PATH, kommune, "interim", "lidar")

print(las_dir)
env.workspace = las_dir


# TODO walk through subdir as well.

# list files with extension ".las"
files_list = [f for f in listdir(env.workspace) if f.endswith(".las")]

print(files_list)
utm32 = [
    "UTM zone 32N",
    'PROJCS["ETRS_1989_UTM_Zone_32N",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",9.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
]
utm33 = [
    "UTM zone 33N",
    'PROJCS["ETRS89 / UTM zone 33N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25833"]]',
]

# define projection
projection = utm32[1]
# print(projection)

for file in files_list:
    arcpy.AddMessage("reproject <" + file + "> to " + utm32[0])
    arcpy.management.DefineProjection(file, projection)

arcpy.AddMessage("Reprojection is finished.")
