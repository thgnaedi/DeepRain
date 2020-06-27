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
| QN | - |  Qualitäts Niveau (0-16) |
| RS_01 | NIEDERSCHLAGSHOEHE |  Niederschlagshoehe 1min |
| RS_IND_01 | NIEDERSCHLAG_IND |  Niederschlagsindikator 1min |

Offene Punkte:
* Regenmenge Einheit ?
* umspeichern der .txt in leichteres Format?

### Auswertung:

Die Aktuellen Daten werden mit dem [Python-Script](https://github.com/thgnaedi/DeepRain/blob/DataUnderstanding/WetterStation_KN/Read_TXT.py) eingelesen und ein paar kleine Statistiken zum Validieren der Daten vorgenommen.

#### Niederschlagswerte (referenz):

| Zeitraum | Region | Menge | Quelle  |
| ------------- |:-------------:| -----|-----|
| 2017 | Baden-Württemberg | 975 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/249926/umfrage/niederschlag-im-jahr-nach-bundeslaendern/) |
| 2018 - 01 | Deutschland | 100 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 02 | Deutschland | 20 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 03 | Deutschland | 50 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 04 | Deutschland | 35 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 05 | Deutschland | 50 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 06 | Deutschland | 50 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 07 | Deutschland | 40 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 08 | Deutschland | 40 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 09 | Deutschland | 45 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 10 | Deutschland | 28 L/m² | [statista.com](https://de.statista.com/statistik/daten/studie/5573/umfrage/monatlicher-niederschlag-in-deutschland/) |
| 2018 - 10 | Konstanz | 33,5 L/m² | [wetterkontor.de](https://www.wetterkontor.de/de/wetter/deutschland/monatswerte.asp?y=2018&m=10) |

#### Vergleich mit Messwerten aus .txt File:
![=)](https://github.com/thgnaedi/DeepRain/blob/master/WetterStation_KN/result.JPG)

* Messwerte stimmen teilweise sehr gut überein
* Einige Monate sind weit daneben
* Gemmesener Extremwert ```30.05.2018 19:16 2.7``` ist laut [Regenradar](https://kachelmannwetter.com/de/regenradar/konstanz/20180530-1715z.html) nicht möglich, Fehlmessungen in Daten!
vgl. [Textauszug](https://github.com/thgnaedi/DeepRain/blob/DataUnderstanding/WetterStation_KN/snipet.md) aus .txt File


### Historische Textdateien:
Die Historischen Daten sind Monatlich als Textdatei gespeichert. Im Vergleich mit den historischen Daten fallen neue Spalten im Header auf, diese sind aber "ungenutzt" bzw. über alle (geprüft auf Jahr 2017) einträge identisch. Diese sind: QN, RTH_01 und RWH_01.

Die Messwerte wurden wie auch zuvor Monatsweise zusammenaddiert und mit den Historischen Daten von [wetterkontor.de](https://www.wetterkontor.de/de/wetter/deutschland/monatswerte.asp?y=2018&m=10) verglichen, Ergebnis siehe Abbildung:
![=)](https://github.com/thgnaedi/DeepRain/blob/master/WetterStation_KN/result_2017.JPG)

Extremwerte wurden folgende gefunden:
```
08.07.2017 15:36 3.02
14.07.2017 14:56 2.81
02.08.2017 01:13 2.66
02.08.2017 01:14 4.4
02.08.2017 01:15 4.25
18.08.2017 17:30 2.52
```
diese gilt es noch mit dem Regenradar zu vergleichen.
