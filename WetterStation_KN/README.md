## Wetterstation Konstanz

### Rohdateien:
Allgemeine Infos ```ftp://ftp-cdc.dwd.de/pub/CDC/Liesmich_intro_CDC-FTP.pdf```

Aktuelle und Historische Daten ```ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/1_minute/precipitation/recent/```
* Konstanzer Wetterstation hat ID: 02712  (Strg+F)
* Zip-File mit Textdatei

#### .txt Format:
```
STATIONS_ID;MESS_DATUM;QN;RS_01;RS_IND_01
      ...
       2712;201801012003;    3;   0.00; 1
       2712;201801012004;    3;   0.04; 1
       2712;201801012005;    3;   0.02; 1
       2712;201801012006;    3;   0.04; 1
       2712;201801012007;    3;   0.03; 1
       2712;201801012008;    3;   0.05; 1
       2712;201801012009;    3;   0.03; 1
       2712;201801012010;    3;   0.00; 1
      ...
```
Genauere erläuterungen der Spaltennamen gibt es unter ```ftp://ftp-cdc.dwd.de/pub/CDC/help/Abkuerzung_Spaltenname_CDC_20180308.xlsx```

| Abkürzung | Alter Spaltenname | Beschreibung  |
| ------------- |:-------------:| -----|
| STATIONS_ID | - | ID der Station |
| MESS_DATUM  | - |   Datum der Messung YYYYMMDDHHMM |
| QN | - |  - |
| RS_01 | NIEDERSCHLAGSHOEHE |  Niederschlagshoehe 1min |
| RS_IND_01 | NIEDERSCHLAG_IND |  Niederschlagsindikator 1min |

Offene Punkte:
* Regenmenge Einheit ?
* umspeichern der .txt in leichteres Format?

