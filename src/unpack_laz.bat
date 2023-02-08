
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

set source_folder="P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\LiDAR_DATA\Bodo\laz\test-unzip"
set destination_folder="P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Willeke\treeDetection\data\interim\lidar\bodo"
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
  %laszip_exe% -i %source_folder%\%%a -o %destination_folder%\%%~na.las
  echo Unzipping %%a complete.
  echo ------------------------------------------------------------------
)

pause


