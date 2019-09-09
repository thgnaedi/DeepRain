# Datenverarbeitung

## DWD to PNG
Das Skript ```DWDtoPNGScript.py``` konvertiert die DWD-Radardaten nach PNG und spreizt dabei die Daten auf einen Bereich von 0 bis 255, damit die Daten als 8-bit PNGs gespeichert werden können. Dafür werden 2 Durchläufe benötigt. Im ersten Durchlauf wird das Maximum bestimmt, um die Daten richtig skalieren zu können (das Minimum wird als 0/kein Regen angenommen).

## Benutzung
Dem Skript muss der Ordner mit dem entpakten Radardaten übergenen werden (siehe [DWD-Crawler Readme0](https://github.com/thgnaedi/DeepRain/blob/master/DWD_Crawler/README.md)), dazu noch das Verzeichnis, in dem die PNGs gespeichert werden sollen.

Argument    | Bedeutung
------------|--------
-h          | Hilfe mit Beschreibung und Kommandozeilenoptionen         | Only unpacks already downloaded files (use with -z, do not use with -d)
-i \<dir\>  | Verzeichnis mit den (unkomprimierten) DWD-Binärdateien
-o \<dir\>  | Verzeichnis in dem die PNGs gespeichert werden sollen
-m \<file\> | Datei in/aus der die Metadaten der DWD-Binärdateien gespeichert/gelesen werden sollen
-c          | Flag das bestimmt, ob Metadaten zu neuen Dateien berechnet werden sollen oder nicht (überspringt ersten Durchlauf)
-f <number> | Faktor, mit dem jedes Datum multipliziert wird (Werte höher als 1 können die Vorhersage des Netzes verbessern)
