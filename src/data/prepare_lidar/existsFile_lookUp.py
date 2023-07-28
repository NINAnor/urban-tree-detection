import csv
import os


kommune = "baerum"
root = r"P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data"


# Define the name of the lookup CSV file
lookup_file = os.path.join(root, kommune, "lidar", kommune + "_LUT.csv")


# Define the name of the output CSV file for files that are not downloaded
log_filename = os.path.join(
    root, kommune, "lidar\laz", "inside_BuildUpZone", "file_not_downloaded.csv"
)

# Create a set to store the filenames from the lookup CSV
lookup_filenames = set()

# Open the lookup CSV file and read in the filenames
with open(lookup_file, newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lookup_filenames.add(
            os.path.join(
                root,
                kommune,
                "lidar\laz",
                "inside_BuildUpZone",
                row[0] + ".laz",
            )
        )

# Check each filename in the lookup set to see if it exists
for filename in lookup_filenames:
    if not os.path.exists(filename):
        # print(filename, "does not exists")
        # If the file does not exist, write its filename to the output CSV file
        with open(log_filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([filename])
    else:
        print(filename, "exists")
