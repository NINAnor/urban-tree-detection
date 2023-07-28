import os

import shutil
import logging
import dotenv
from dotenv import dotenv_values

from src import RAW_PATH, MUNICIPALITY

kommune = MUNICIPALITY

input_folder = os.path.join(RAW_PATH, "laz", "all")
output_folder_1 = os.path.join(RAW_PATH, "laz", "inside_BuildUpZone")
output_folder_2 = os.path.join(RAW_PATH, "laz", "outside_BuildUpZone")
lookup_file = os.path.join(RAW_PATH, kommune + "_LUT.csv")

logger = logging.getLogger(__name__)
# print(input_folder)
# print(output_folder_1)
# print(output_folder_2)
# print(lookup_file)

if not os.path.exists(output_folder_1):
    os.mkdir(output_folder_1)

if not os.path.exists(output_folder_2):
    os.mkdir(output_folder_2)

for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.endswith(".laz"):
            found = False
            with open(lookup_file, "r") as f:
                for line in f:
                    if filename[:-4] == line.strip():
                        found = True
                        break

            if found:
                output_path = os.path.join(output_folder_1, filename)
                if os.path.exists(output_path):
                    print(
                        f"File {filename} already exists in output_folder_1, skipping..."
                    )
                    continue
                shutil.move(os.path.join(root, filename), output_folder_1)
                print(f"Moving file {filename} to inside_BuildUpZone")
            else:
                output_path = os.path.join(output_folder_2, filename)
                if os.path.exists(output_path):
                    print(
                        f"File {filename} already exists in output_folder_2, skipping..."
                    )
                    continue
                shutil.move(os.path.join(root, filename), output_folder_2)

print(
    "The .laz files are succesfully split into inside_BuildUpZone and outside_BuildUpZone \nusing the LookUp file and moved to specified katalogs accordingly."
)
