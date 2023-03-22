@echo off
SET kommune=kristiansand
SET location="P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\treeDetection\data\%kommune%\interim\lidar"

echo %location%
FOR /R "%location%" %%A IN (*.las) DO CALL :rename "%%A"
GOTO :eof

:rename
SET "_filename=%~nx1"
IF /I "%_filename:~-4%"==".las" (
  REM REN "%1" "%_filename:-=_%"
  REN "%1" "%_filename:32=utm32%"
)
GOTO :eof


