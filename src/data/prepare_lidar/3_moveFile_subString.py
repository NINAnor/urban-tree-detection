import os
import shutil
import dotenv
from dotenv import dotenv_values

kommune="kristiansand"

# search for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, '.env')

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)

# project data path variables 
DATA_PATH = os.getenv('DATA_PATH')
source_dir = os.path.join(DATA_PATH, kommune, "raw", "las_inside_BuildUpZone")
target_dir = os.path.join(DATA_PATH, kommune, "interim","lidar")

print(source_dir)
print(target_dir)

#"raw_data\baerum\lidar\las_inside_BuildUpZone

# Loop through the file list
for file_name in os.listdir(source_dir):
    # Extract the substring we're interested in
    substring = file_name.split('-')[2] + '-' + file_name.split('-')[3]
    print(substring)
    f_substring = substring[:3] + '_' + substring[4:]

    # Define the folder path using the substring
    folder_path = os.path.join(target_dir, f_substring)
    
    # Check if the folder already exists, if not create it
    if not os.path.exists(folder_path):
        print(f"Make directory {f_substring}")
        os.makedirs(folder_path)

    # Move the file to the appropriate folder
    print(f"copy the file '{file_name}'to the folder '{folder_path}'")
    shutil.copy(os.path.join(source_dir, file_name), folder_path)
    
    #break