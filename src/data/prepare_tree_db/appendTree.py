
# field mapping Bodø
arcpy.management.Append(
    inputs="treetop_in_situ",
    target="treetop_in_situ",
    schema_type="NO_TEST",
    field_mapping='tree_id "tree_id" true true false 4 Long 0 0,First,#,treetop_in_situ,OBJECTID,-1,-1;itree_species_code "itree_species_code" true true false 255 Text 0 0,First,#;norwegian_name "norwegian_name" true true false 255 Text 0 0,First,#,treetop_in_situ,norwegian_name,0,255;taxon_name "taxon_name" true true false 255 Text 0 0,First,#;taxon_type "taxon_type" true true false 255 Text 0 0,First,#;english_name "english_name" true true false 255 Text 0 0,First,#;registration_date "registration_date" true true false 8 Date 0 0,First,#,treetop_in_situ,regristration_date,-1,-1;address "address" true true false 255 Text 0 0,First,#,treetop_in_situ,address,0,255;land_use "land_use" true true false 255 Text 0 0,First,#;dbh "dbh" true true false 4 Float 0 0,First,#,treetop_in_situ,dbh,-1,-1;dbh_heigth "dbh_heigth" true true false 4 Float 0 0,First,#;dieback "dieback" true true false 2 Short 0 0,First,#;crown_missing "crown_missing" true true false 2 Short 0 0,First,#;crown_ligth_exposure "crown_ligth_exposure" true true false 2 Short 0 0,First,#;total_tree_heigth "total_tree_heigth" true true false 4 Float 0 0,First,#;live_tree_heigth "live_tree_heigth" true true false 4 Float 0 0,First,#;crown_base_heigth "crown_base_heigth" true true false 4 Float 0 0,First,#;lat "lat" true true false 8 Double 0 0,First,#,treetop_in_situ,lat,-1,-1;long "long" true true false 8 Double 0 0,First,#,treetop_in_situ,long,-1,-1',
    subtype="",
    expression="OBJECTID IS NOT NULL",
    match_fields=None,
    update_geometry="NOT_UPDATE_GEOMETRY"
)

arcpy.management.Append(
    inputs="ByTreBodø_lokal",
    target="treetop_in_situ",
    schema_type="NO_TEST",
    field_mapping='tree_id "tree_id" true true false 4 Long 0 0,First,#,ByTreBodø_lokal,OBJECTID,-1,-1;itree_species_code "itree_species_code" true true false 255 Text 0 0,First,#;norwegian_name "norwegian_name" true true false 255 Text 0 0,First,#,ByTreBodø_lokal,Treslag,0,25;taxon_name "taxon_name" true true false 255 Text 0 0,First,#;taxon_type "taxon_type" true true false 255 Text 0 0,First,#;english_name "english_name" true true false 255 Text 0 0,First,#;registration_date "registration_date" true true false 8 Date 0 0,First,#,ByTreBodø_lokal,Registreringsdato,-1,-1;address "address" true true false 255 Text 0 0,First,#,ByTreBodø_lokal,Sted,0,50;land_use "land_use" true true false 255 Text 0 0,First,#;dbh "dbh" true true false 0 Long 0 0,First,#,ByTreBodø_lokal,Omkrets,-1,-1;dbh_heigth "dbh_heigth" true true false 0 Long 0 0,First,#;dieback "dieback" true true false 2 Short 0 0,First,#;crown_missing "crown_missing" true true false 2 Short 0 0,First,#;crown_ligth_exposure "crown_ligth_exposure" true true false 2 Short 0 0,First,#;total_tree_heigth "total_tree_heigth" true true false 4 Float 0 0,First,#;live_tree_heigth "live_tree_heigth" true true false 4 Float 0 0,First,#;crown_base_heigth "crown_base_heigth" true true false 4 Float 0 0,First,#;lat "lat" true true false 8 Double 0 0,First,#;long "long" true true false 8 Double 0 0,First,#',
    subtype="",
    expression="OBJECTID IS NOT NULL",
    match_fields=None,
    update_geometry="NOT_UPDATE_GEOMETRY"
)