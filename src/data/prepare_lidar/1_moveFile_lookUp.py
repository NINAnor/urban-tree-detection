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

input_folder = os.path.join(DATA_PATH , kommune, "raw", "lidar\laz", "all")
output_folder_1 = os.path.join(DATA_PATH , kommune, "raw", "lidar\laz", "inside_BuildUpZone")
output_folder_2 = os.path.join(DATA_PATH , kommune, "raw", "lidar\laz", "outside_BuildUpZone")
lookup_file = os.path.join(DATA_PATH , kommune, "raw", "lidar", kommune+"_LUT.csv")

print(input_folder)
print(output_folder_1)
print(output_folder_2)
print(lookup_file)

if not os.path.exists(output_folder_1):
    os.mkdir(output_folder_1)

if not os.path.exists(output_folder_2):
    os.mkdir(output_folder_2)

for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.endswith('.laz'):
            found = False
            with open(lookup_file, 'r') as f:
                for line in f:
                    if filename[:-4] == line.strip():
                        found = True
                        break

            if found:
                output_path = os.path.join(output_folder_1, filename)
                if os.path.exists(output_path):
                    print(f"File {filename} already exists in output_folder_1, skipping...")
                    continue
                shutil.move(os.path.join(root, filename), output_folder_1)
                print(f"Moving file {filename} to inside_BuildUpZone")
            else:
                output_path = os.path.join(output_folder_2, filename)
                if os.path.exists(output_path):
                    print(f"File {filename} already exists in output_folder_2, skipping...")
                    continue
                shutil.move(os.path.join(root, filename), output_folder_2)

print("Moving of files finished.")