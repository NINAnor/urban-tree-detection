urban-treeDetection 
==============================

**repo-status: work in progress**

This project provides a workflow for detecting trees in urban areas using Airborne Laser Scanning (ALS) data and national geographic datasets. The output is a tree database with **tree crown** polygons and **tree top** points per neighbourhood. 

This tree database can be used as input for the [i-Tree Eco](https://www.itreetools.org/tools/i-tree-eco) model to estimate the ecosystem services of trees in urban areas. However, the laser data must be supplemented with in situ tree data (e.g. tree species, dbh, etc.) and gis-derived data (e.g. land use, building footprints, etc.) to succesfully run the i-Tree Eco model. The repository *[itree-supportTools](https://github.com/ac-willeke/itree-supportTools)* provides a workflow for preparing and linking in situ data and gis-derived data to the detected laser trees. 

In addition, the tree crowns can be used as an input to model other ecosystem services not included in the i-Tree Eco model, such as   local climate regulating services and tree crown visibility cultural services. These workflows are included in the following repositories:

- [urban-climateServices](<https://github.com/ac-willeke>) for urban heat modelling
- [r.viewshed.exposure](<https://github.com/OSGeo/grass-addons/tree/grass8/src/raster/r.viewshed.exposure>) for estimating tree crown visibility.
- [r.viewshed.impact](https://github.com/zofie-cimburova/r.viewshed.impact) for estimating tree crown impact. 


------------

Code is provided for the following tasks:

1. **preparing Airborne laser scanning (ALS)** data from [Kartverket](https://hoydedata.no/).
2. **detecting tree crowns** in the built-up zone of Norwegian municipalities using a watershed segmentation method following the workflow from *Hanssen et al. (2021)*.

3. **detecing false positives**  (e.g. objects that are detected as trees but are instead buildings, lamp posts, etc.) by identifying outliers in the geometrical shape of the tree crowns.
   

The repository is applied on the Norwegian municipalities: *Bærum, Bodø, Kristiansand* and *Oslo.* 

------------

### Installation 

The code runs in an ArcGIS Pro 3.1.0. conda environment and depends on 3D analyst, image analyst, spatial analyst licenses. 

Here are the steps to create a conda env compatible with ArcGIS Pro 3.0.1 and to install the local project package `urban-treeDetection`:

1. Create a new conda environment with the necessary dependencies described in `environment.yml`
    
        cd /d P:\%project_folder%\treeDetection
        cd ...\urban-treeDetection
        conda env create -f environment.yml
        conda activate treeDetection

2. Install the treeDetection (urban-treeDetection/src) as a local package using pip:

        pip install -e .
        # installs project packages in development mode 
        # this creates a folder treeDetection.egg-info

3. In case you run into errors remove your conda env and reinstall 

        conda remove --name myenv --all
        # verify name is deleted from list
        conda info --envs

### Detect trees in your Municipality 
--> project is not ready for use. 

1. Create Folder structure

2. Run the script `main.py`
    - prepares lidar data
    - segments tree crowns
    - joins municpal dataset with laser dataset

3. Run i-Tree Eco 

4. Extrapolate i-Tree Eco values 

### Workflow

1. Prepare Data 
script catalog: `src\data`
        a. Create project folder structure  
        b. Clean and prepare the muncipality tree database `prepare_tree_db`
        c. Clean and preprocess laser data `prepare_lidar`
2. Lidar tree detection 
script catalog: `src\segmentation`
        



### References 
- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007

### Citation 

### Acknowledgments

*This repository is part of the project:*

**TREKRONER Prosjektet** | Trærs betydning for klimatilpasning, karbonbinding, økosystemtjenester og biologisk mangfold. 


