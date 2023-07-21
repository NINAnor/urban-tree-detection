General Data 
-----------------
| English name | Norsk Navn | Type | beskrivelse | Datakilde |
|--------------|------------|------|-------------|-----------|
| %municipality%_base_data.gdb | %kommune%_basisdata.gdb | FileGDB | grunnleggende geografiske data | FKB veg, FKB vann, FKB bygg, N50 |
| %municipality%_admin_data.gdb | %kommune%_admindata.gdb | FileGDB | anaylseomrade, grunnkretser, bydeler, kartblad | AdminEnheter, SSB Grunnkrets |

basisdata
-----------------

```markdown
data/%muncicipality%/general 
├── admindata.gdb
│   │── analyseomrade
│   │── kommune
│   │── bydeler
│   │── grunnkretser
│   │── markaomrade
│   └── kartblad1000
└── basisdata.gdb
    │── fkb_bygning_omrade
    │── fkb_vann_omrade
    │── fkb_veg_omrade
    └── n50_samferdsel_senterlinje
```



