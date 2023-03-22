## how to run files 

1. moveFile_lookUp.py
2. extract_laz.bat

4. moveFile_substring.py
--> are .prj files also moved?
--> move them manuale for baerum 
3. renameFile.bat
3. define_projection.py
5. perform_tree_detection #rewrite script
a. v1 = bodo, kristiandsand
b. v2 = baerum


TO DO
make parameterfile 
write down folder structure 
see cookiecutter and chatgpt chat
make project and APPLY 
to bodo 
kristiansand etc. 


BODO: do step 5
Kristiandsand + Baerum: do step 1-5

```shell
## folder structure
## raw data folder
P:/
    152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst/
    │──	raw_data/
        │──	baerum/
            │── lidar/
                │── las_inside_BuildUpZone/
                    │── all/
                    │── inside_BuildUpZone/
                    └── outside_BuildUpZone/	
                │── laz/
                └── raw/	
            └── vector/	
        │──	bodo/
        │──	kristiansand/
        └──	oslo/
        

## modelling folder 
P:/
    15220700_gis_samordning_2022_(marea_spare_ecogaps)/Willeke/
        │──	baerum/
        │──	treeDetection/
            │── arcgispro/
            │──	data/
            │──	docs/
            │──	src/
                │──	data/     -> scripts for collecting, processing, and cleaning raw data. 
                │──	features/ -> scripts for creating features from cleaned data
                │──	models/   -> scripts for training/evaluating models
                └──	visualization/	-> scripts for creating visualizations from the cleaned data and the models. 
            │──	test/
            └──	tools/	
        │──	bodo/
        │──	kristiansand/
        └──	oslo/
        
```