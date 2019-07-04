# Daten
Dises Kapitel geht darauf ein, woher wir die Daten für das Training des Netzes beschaffen und wie wir diese vor-bearbeiten.

## Quelle (Crawler)
Die Daten, die wir verwenden, stammen vom Deutschen Wetterdienst (ab jezt DWD) und sind Radardaten von deren Radarstationen. Die Messungen liegen in einer Auflösung von 5 Minuten vor und ergeben den Niederschlag in mm. Z.zt. liegen die Daten vom Januar 2001 bis Januar 2018 vor (jeweils inklusive). Für unsere Zwecke verwenden wir die 18 kompletten Jahre 2001 bis 2017.

Mit einem in Python geschriebenem Crawler werden die Tar-Archive, die jeweils einen Monat beinhalten heruntergeladen und entpackt; die Tage sind jeweils wieder in einem Tarball komprimiert. Die Binärdateien werden letztendlich auf einer Btrfs-formatierten Partition gespeichert, da diese wegen der häufigen Nullen einfach komprimierbar sind.

[DWD Opendata Jahre 2001 bis 2017](https://opendata.dwd.de/climate_environment/CDC/grids_germany/5_minutes/radolan/reproc/2017_002/bin/)

## Preprocessing (Konverter)
Die Daten liegen in einem Binärformat des DWD vor, aus dem man den Niederschlag (auch für bestimmte Koordinaten) in mm extrahieren kann. Dazu muss man die Python-Bibliothek "Wradlib" über den Package-Manager von Anaconda installieren.

Damit lesen wir die 5-minütlichen Daten ein und rastern daraus den Niederschlag in einer Deutschlandkarte mit einer Auflösung von 1100x900 Pixeln, der Standardauflösung der DWD-Daten. Visualisiert man diese Daten, sieht man eine Menge von Kreisen, die jeweils dem Radius einer Radarstation entsprechen. Diese bedecken Deutschland und reichen leicht über die Grenzen.

Danach bestimmen wir für jede Datei das Maximum des Niederschlags (in mm), um die Werte auf einen Bereich spreizen zu können; das Minimum muss nicht berechnet werden und kann als 0 angenommen werden, was keinem Niederschlag entspricht.
Nach dem Ersten Durchgang, bei dem das Globale Maximum bestimmt wurde, werden die Daten in einem zweiten Durchgang mittels  des globalen Maximalwertes auf einen Wertebereich zwischen 0 und 255 gespreizt, damit die Bilder in einem Bildformat mit einer Bittiefe von 8 Bit gespeichert werden Können. Wir haben uns für das PNG-Format entschieden, weil es verlustfrei komprimiert und von platformübergreifenden Bibliotheken gelesen und geschrieben werden kann.

Zum Schluss werden die Werte mit dem Faktor 4 multipliziert; dabei werden die Werte über 255 auf den Maximalwert geclampt. Dadurch verwerfen wir Ausreißer und das Training funktioniert besser.

## Herausforderungen in diesem Kapitel
Die größte Herausforderung in diesem Kapitel war zweifelsfrei die große Datenmenge, die wir verarbeitet haben. Die Rohdaten der 18 Jahre in 5-Minuten-Auflösung hätte unseren zugewiesenen Speicher gesprengt, mit dem Btrfs, das die Dateien on-the-fly komprimiert und dedupliziert, passten die Daten doch auf unsere Festplatte.

Darüber hinaus lagen die Archive des DWD im Tar-Format vor, das keine Checksumme anbietet und somit erst beim Entpacken bemerkt werden kann, dass beim Download einer Datei ein Fehler auftrat. Bei den großen Tar-Archiven des DWD ist leider mehrmals ein Download-Fehler aufgetreten, der sehr spät auffiel.

Die dritte Herausforderung lag darin, dass es in den Daten nicht erklärbare Ausreißer gab und wie man diese eliminieren soll. Weil es extrem lange dauern würde, für 18 Jahre in 5-Minuten-Aulösung ein Histogram zu berechnen, haben wir einen (hoffentlich) Educated Guess gemacht und das Viertel des Maximalwertes als neuen Maximalwert gewählt.


# Environment
Das Trainieren von unserem Netz geschieht mit der Tensorflow-Library in der Version 1.14.0. Diese haben wir in einem Docker-Image für unsere CPU selbst kompiliert und umgehen dadurch Inkompatibilitäten mit vor-kompilierten Builds, haben die optimale Performance auf unserer CPU und haben Zugriff auf die neuesten Features.

Mithilfe des Docker-Images können wir mehrere Container starten und somit können wir parallel mehrere Loss-Funktionen validieren.


# Klassifizierung
Statt die genaue Regenmenge vorherzusagen, stellten wir drei Kategorien auf: kein Regen (= 0mm), wenig Regen (<= 10mm) und viel Regen (> 10mm). Diese Kategorien haben wir als One-Hot-Vector kodiert. `[1, 0, 0]` entspricht hierbei kein Regen, sodass man aus der ersten Dimension der Vorhersage einfach ein Vorschaubild generieren kann aus dem man gleich feststellen kann, ob es am jeweiligen Pixel regnet oder nicht.

Für das Training mit Kategorien kann man nicht mehr den MSE verwenden, hier würde selbst nach 80 Epochen nur "kein Regen" vorhergesagt. Stattdessen wurde als Loss-Funktion die "Categorical Crossentropy" von Keras verwendet; die binäre Crossentropy können wir nicht verwenden, weil wir mehr als zwei Kategorien verwenden. Die "Categorical Crossentropy" funktioniert relativ gut, aber es wird ein Blob vorhersagt, der etwas über den Bereich ragt, in dem es eigentlich regnet.

Danach wurde noch die Aktivierungsfunktion für den Output-Layer Sigmoid durch Softmax ersetzt. Dadurch erscheint das Vorschaubild etwas verwaschener, aber der Blob um das Regengebiet wird kleiner und die Differenz zum Referenzbild wird kleiner.

Wenn man die Aktivierungsfunktion der Hidden-Layer (von ReLu) zu Tanh verändert, verbessert sich auch die Kategorisierung: der Blob nähert sich weiter dem Regengebiet aus derm zu vorhersagendem Bild an, ist aber immer noch merkbar größer und franst an den kanten aus.

Als nächstes wird die Metrik "categorical_accuracy" verwendet, um die Vorhersage zu überwachen. Dadurch kann der Fortschritt beim Trainieren besser überwacht werden.

## Endgültige Architektur des Netzes


## Herausforderungen in diesem Kapitel
- Richtige Kategorien finden
- Training mit richtiger Aktivierungsfunktion / Optimizer
