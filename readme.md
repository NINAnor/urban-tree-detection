## urban-treeDetection ##

This project provides a workflow for preparing an input dataset for i-Tree Eco analysis using a municipal tree dataset supplemented with lidar-segmented crown geometry and auxiliary GIS datasets. 

This repository provides code for:

(i) preparing Airborne laser scanning (ALS) data from Kartverket (<https://hoydedata.no/>)

(ii) a watershed segmentation method following the workflow from Hanssen et al. (2021) to detect trees in the built-up zone of Norwegian municipalities using ALS data. 

(iii) preparing an input dataset for an i-Tree Eco analysis by supplementing existing municipal tree inventories with crown geometry from the ALS data and auxiliary spatial datasets following the workflow by Cimburova and Barton (2020).  

(iv) extrapolating the outputs from i-Tree Eco analysis to all municipal trees following the workflow by Cimburova and Barton (2020).    

The repository is applied on the Norwegian municipalities: Bærum, Bodø, Kristiansand and Oslo. 

This work is part of the project: **TREKRONER Prosjektet** Trærs betydning for klimatilpasning, karbonbinding, økosystemtjenester og biologisk mangfold. 


This project provides a workflow for preparing a complete input dataset for i-Tree Eco analysis using a municipal tree dataset supplemented by lidar segmented tree crowns and auxilliary GIS datasets. 





### References ###
- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007
- Cimburova, Z., & Barton, D. N. (2020). The potential of geospatial analysis and Bayesian networks to enable i-Tree Eco assessment of existing tree inventories. Urban Forestry & Urban Greening, 55, 126801. https://doi.org/10.1016/j.ufug.2020.126801

### Installation ###

The code is build in an ArcGIS Pro 3.1.0. conda environment with 3D analyst, image analyst, spatial analyst licensed. 

Here are the steps to create a conda env compatible with ArcGIS Pro 3.0.1 and to install the package treeDetection:

1. Create a new conda environment with the necessary dependencies described in `environment.yml`

    # navigate to the project directory
    cd /d P:\%project_folder%\treeDetection
    cd ...\urban-treeDetection
    conda env create environment.yml
    conda activate treeDetection

    # remove conda env incase you need to re-install

2. Install the treeDetection (urban-treeDetection/src) as a local package using pip:

    # install in development mode if you wish to build further on this project
    pip install -e . 

    # this creates a folder treeDetection.egg-info

    conda remove --name myenv --all
    # verify name is deleted from list
    conda info --envs













### Detect trees in your Municipality ###

3. Create Folder structure

4. Run the script ...

5. Run the script ...



### Citation ###

If you use or build upon this repository, please cite the following papers:

- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007
- Cimburova, Z., & Barton, D. N. (2020). The potential of geospatial analysis and Bayesian networks to enable i-Tree Eco assessment of existing tree inventories. Urban Forestry & Urban Greening, 55, 126801. https://doi.org/10.1016/j.ufug.2020.126801

### References ###
- Hanssen, F., Barton, D. N., Venter, Z. S., Nowell, M. S., & Cimburova, Z. (2021). Utilizing LiDAR data to map tree canopy for urban ecosystem extent and condition accounts in Oslo. Ecological Indicators, 130, 108007. https://doi.org/10.1016/j.ecolind.2021.108007
- Cimburova, Z., & Barton, D. N. (2020). The potential of geospatial analysis and Bayesian networks to enable i-Tree Eco assessment of existing tree inventories. Urban Forestry & Urban Greening, 55, 126801. https://doi.org/10.1016/j.ufug.2020.126801


### Acknowledgments ###


