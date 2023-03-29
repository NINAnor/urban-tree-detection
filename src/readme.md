
## TODO
- update folder structure
- license 
- lookat makefile etc. 

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