@echo off
SET kommune=bodo
SET location="P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\raw_data\%kommune%\lidar\las_inside_BuildUpZone"

FOR /R "%location%" %%A IN (*.las) DO CALL :rename "%%A"
GOTO :eof

:rename
SET "_filename=%~nx1"
IF /I "%_filename:~-4%"==".las" (
  REN "%1" "%_filename:-=_%"
)
GOTO :eof


