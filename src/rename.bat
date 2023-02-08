SET location="P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Zofie\synergi_3_tree_accounts\DATA"
FOR /R %location% %%A in (*.prj) DO CALL :rename "%%A"
GOTO :eof 

:rename
SET "_filename=%~nx1"
REN %1 "%_filename:-=_%"