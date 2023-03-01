
@echo off

rem unpack_laz.bat: extract .laz files to .las  
rem ---------------------------------------------------------------------------------------------------------------------------------------
rem author: Willeke A'Campo
rem created: 07.02.2022
rem project: Trekroner-prosjektet 
rem 
rem Description: upacking .laz tiles and moving them as .las into the designated folders 
rem Doc: see NINA technical - Tree Detection 2023 "3. Data preprocessing"
rem ---------------------------------------------------------------------------------------------------------------------------------------

set kommune=baerum

set source_folder="P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data\%kommune%\lidar\laz\inside_BuildUpZone"
set destination_folder="P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data\%kommune%\lidar\las_inside_BuildUpZone"
set laszip_exe="P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Willeke\treeDetection\tools\LAStools\bin\laszip.exe"

rem Display source and destination folder
echo --------------------------------------------------------------------------------------------------------------------------------------
echo source folder *laz: %source_folder%
echo destination folder *las: %destination_folder%
echo use lastool: %laszip_exe%

rem Loop through files in source folder and unzip them in the destination_folder
for /f %%a in ('dir /b %source_folder%\*.laz') do (
  echo ------------------------------------------------------------------
  echo Unzipping file: %%a
  if not exist %destination_folder%\%%~na.las (
    %laszip_exe% -i %source_folder%\%%a -o %destination_folder%\%%~na.las
    echo Unzipping %%a complete.
  ) else (
    echo Skipped %%a, output file already exists in destination folder.
  )
  echo ------------------------------------------------------------------
)



pause


