# Datenverarbeitung

## DWD to PNG
Das Skript ```DWDtoPNGScript.py``` konvertiert die DWD-Radardaten nach PNG und spreizt dabei die Daten auf einen Bereich von 0 bis 255, damit die Daten als 8-bit PNGs gespeichert werden können. Dafür werden 2 Durchläufe benötigt. Im ersten Durchlauf wird das Maximum bestimmt, um die Daten richtig skalieren zu können (das Minimum wird als 0/kein Regen angenommen).

Es wird ebenfalls eine CSV-Datei mit Metadaten angelegt, die für jede Datei mit Radardaten dessen Minimum und Maximum enthält. Dadurch kann bei einem zukünftigem Aufruf die Bestimmung die Bestimmung der Werte für die entsprechenden Dateien entfallen (es wird Zeit gespart). 

## Benutzung
Dem Skript muss der Ordner mit dem entpakten Radardaten übergenen werden (siehe [DWD-Crawler Readme](https://github.com/thgnaedi/DeepRain/blob/master/DWD_Crawler/README.md)), dazu noch das Verzeichnis, in dem die PNGs gespeichert werden sollen.

Es kann explizit der Name der anzulegenden Metadaten-Datei angegeben werden. Falls nicht, wird automatisch im Verzeichnis des Scripts ```radolan_metadata.csv``` angelegt.

Der Faktor, mit dem die Daten multipliziert werden, ist normalerweise 1. Jedoch hat sich zum Trainieren der Wert 4 als nützlich herausgestellt.

Argument    | Bedeutung
------------|--------
-h          | Hilfe mit Beschreibung und Kommandozeilenoptionen         | Only unpacks already downloaded files (use with -z, do not use with -d)
-i \<dir\>  | Verzeichnis mit den (unkomprimierten) DWD-Binärdateien
-o \<dir\>  | Verzeichnis in dem die PNGs gespeichert werden sollen
-m \<file\> | Datei in/aus der die Metadaten der DWD-Binärdateien gespeichert/gelesen werden sollen
-c          | Flag das bestimmt, ob Metadaten zu neuen Dateien berechnet werden sollen oder nicht (überspringt ersten Durchlauf)
-f <number> | Faktor, mit dem jedes Datum multipliziert wird (Werte höher als 1 können die Vorhersage des Netzes verbessern)
