import os
import shutil

kommune="baerum"
root= r"P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data"

input_folder = os.path.join(root, kommune, "lidar\laz", "all")
output_folder_1 = os.path.join(root, kommune,"lidar\laz", "inside_BuildUpZone")
output_folder_2 = os.path.join(root, kommune,"lidar\laz", "outside_BuildUpZone")
lookup_file = os.path.join(root, kommune,"lidar", kommune+"_LUT.csv")


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
                print(f"Moving file {filename} to inside_BuildUpZone")
                shutil.move(os.path.join(root, filename), output_folder_1)
            else:
                shutil.move(os.path.join(root, filename), output_folder_2)

print("Moving of files finished.")