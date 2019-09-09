# Netze und Auswertung

## Klassifikation
Das UNet wurde zuerst mit drei und dann mit zwei Kategorien trainiert. In der Datei ```categorization.py``` werden die konvertierten Radardaten aus ```Data/samplebundles``` geladen, in Trainings- und Validierungsdaten aufgeteilt, kategorisiert und damit das Netz trainiert.
Das UNet verwendet als Aktivierungsfunktion der Hidden- und Output Layer Softmax.

## Auswertung
Zur Auswertung können zu einem Netz die Confusion-Matrix und die ROC-Kurve generiert werden. Dazu gibt es je ein Skript, in denen jeweils das Verzeichnis angepasst werden.

### Confusion-Matrix
Mit dem Skript ```eval_2D_classification.py``` kann man sich zu einem Netz die Confusion-Matrix berechnen lassen, die Varieble ```directory``` muss angepasst werden.

### ROC-Kurve
Mit dem Skript ```roc_script.py``` erstellt zu einem Netz die ROC-Kurve und eine Grafik zur Sicherheit der Klassen als SVG. Hier müssen ```directory``` und ```netname``` angepasst werden.
