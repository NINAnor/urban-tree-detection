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
- Open the Anaconda Prompt and run the following commands:
    
        ```console
        cd /d P:\%project_folder%\urban-tree-detection
        cd ...\urban-tree-detection
        conda env create -f environment.yml
        conda activate urban-tree-detection
        ```
 
- OR clone your ArcGIS Pro 3.0.1 base env and manually install the dependencies listed in `requirements.txt` using conda or pip. [ArcGIS Pro | Clone an environment](<https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/clone-an-environment.htm>)

2. Install the urban-tree-detection (urban-tree-detection/src) as a local package using pip:

        pip install -e .
        # installs project packages in development mode 
        # this creates a folder urban-tree-detection.egg-info

3. In case you run into errors remove your conda env and reinstall 

        conda remove --name myenv --all
        # verify name is deleted from list
        conda info --envs

4.  Install linters using pipx 
    ```bash
        # install linters using make
        make install-global
        # test linters
        make codestyle
    ```

    **note:** As `pre-commit` unfortunately gives acces-denied errors on Windows OS, I would recommend to run `make codestyle` command before you commit your changes. This command runs black, isort and ruff on all files.

### Configuration
This project uses a .env and a config.yaml file to store configuration variables. The module `utils.config.py` and `yaml_utils.py` provides functions to read and write these files.

Run `src/test/test_config.py` to test the configuration and logger.

#### .env
        # R GeoSpatialData
        FKB_BUILDING_PATH="path/to/gdbfile"
        FKB_WATER_PATH="path/to/gdbfile"
        SSB_DISTRICT_PATH="path/to/gdbfile"
        AR5_LANDUSE_PATH="path/to/filgdbfilee"

        # Trekroner project 
        RAW_DATA_PATH="path/to/raw/data/folder"
        PROJECT="path/to/project/folder/which/contains/the/data/folder"   
        LOCAL_GIT="path/to/the/local/version/of/this/repository" 

        
### Workflow

1. **TODO:** Create Folder structure

2. **TODO:** Import Data using FME
a. study area [vector - fileGDB feature class]
b. laser data [laz - zipped las file]  
c. building footprints [vector - fileGDB feature class]
d. water bodies [vector - fileGDB feature class]
e. land use [vector - fileGDB feature class]

2. Create a municipality-specific study area mask in ArcGIS Pro 
We recommend to create a study area mask manually, as it is specific to each municipality and you might want to mask out areas that are not relevant for your analysis (e.g. water bodies, buildings but that are not yet available in national datasets). 
**Example of a mask formula:**
mask = study_area_200m_buffer - fkb_bygning_omr_1m_buffer - fkb_vann_omrade - ssb_lufthavn - ssb_bane 

4. **TODO:** Pre-process the laser data
script: `src\data\prepare_lidar.py`

5. **TODO:** Detect tree crowns
sub-package: `src\tree_detection`
a. Create a Canopy Height Model (CHM) `model_chm.py`
b. Detect trees using a watershed segmentation method `watershed_segmentation.py`
c. Identify false positives `identify_false_positives.py`

**TODO:**
Step 1 can be run using makefile `src\Makefile`
Steps 4 and 5 can be run using subroutines in `src\main.py`
### References 
- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007

### Acknowledgments

*This repository is part of the project:*

**TREKRONER Prosjektet** | Trærs betydning for klimatilpasning, karbonbinding, økosystemtjenester og biologisk mangfold. 


