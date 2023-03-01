import os
import shutil

source_dir = r'P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data\Bodo\lidar\laz\all'
target_dir = r'P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data\Bodo\lidar'

start_num = 494
end_num = 505

for filename in os.listdir(source_dir):
    if os.path.isfile(os.path.join(source_dir, filename)):
        for num in range(start_num, end_num+1):
            if f"33-1-{num}" in filename:
                target_subdir = str(num)
                print(f"Moving file {filename} to directory {target_subdir}")
                break
        else:
            print(f"No directory found for file {filename}")
            continue
        
        target_path = os.path.join(target_dir, target_subdir)
        if not os.path.exists(target_path):
            print(f"Make directory{num}")
            os.makedirs(target_path)
        
        shutil.move(os.path.join(source_dir, filename), os.path.join(target_path, filename))
