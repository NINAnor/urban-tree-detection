urban-treeDetection 
==============================

**repo-status: work in progress**

This project provides a workflow for preparing an input dataset for i-Tree Eco analysis using a municipal tree dataset supplemented by lidar segmented tree crowns and auxilliary GIS datasets.

------------

Code is provided for the following tasks:

1. **preparing Airborne laser scanning (ALS)** data from Kartverket (<https://hoydedata.no/>)

2. **detecting tree crowns** in the built-up zone of Norwegian municipalities using a watershed segmentation method following the workflow from *Hanssen et al. (2021)*.

4. **preparing an input dataset for i-Tree Eco analysis** by supplementing existing municipal tree inventories with crown geometry from the ALS data and auxiliary spatial datasets following the workflow by *Cimburova and Barton (2020).*  

4. **extrapolating the outputs from i-Tree Eco analysis** to all municipal trees following the workflow by Cimburova and Barton (2020).    

The repository is applied on the Norwegian municipalities: *Bærum, Bodø, Kristiansand* and *Oslo.* 

------------

### Installation 

The code is build in an ArcGIS Pro 3.1.0. conda environment with 3D analyst, image analyst, spatial analyst licensed. 

Here are the steps to create a conda env compatible with ArcGIS Pro 3.0.1 and to install the local project package `treeDetection`:

1. Create a new conda environment with the necessary dependencies described in `environment.yml`
    
        cd /d P:\%project_folder%\treeDetection
        cd ...\urban-treeDetection
        conda env create environment.yml
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

### References 
- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007
- Cimburova, Z., & Barton, D. N. (2020). The potential of geospatial analysis and Bayesian networks to enable i-Tree Eco assessment of existing tree inventories. Urban Forestry & Urban Greening, 55, 126801. https://doi.org/10.1016/j.ufug.2020.126801

### Citation 

### Acknowledgments

*This repository is part of the project:*

**TREKRONER Prosjektet** | Trærs betydning for klimatilpasning, karbonbinding, økosystemtjenester og biologisk mangfold. 


