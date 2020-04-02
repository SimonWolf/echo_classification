# echo_classification
Ähnlich der Echoortung bei Tieren soll in diesem Projekt ein kurzes Tonsignal gesendet werden.
Mit einem Mikrofon wird das Signal und dessen Echo aufgezeichnet.
![audiosignal](/images/audiosignal.png)
Die Audiosignale sollen dann in Spektrogramme umgewandelt werden, welche anschließend als Trainingsdaten
für verschiedene KI-Modelle verwendet werden können.
![spektrogramm](/images/spektrogramm.png)


Im Notbook **01_Trainingsdaten.ipynb** ist der Quellcode und die Beschreibung, für das Erzeugen und Aufzeichnen der Ultraschallsignale. Außerdem ist dort das Skript zu finden, welches automatisiert Trainingsdaten erzeugt:
  - Ton abspielen
  - Echo aufzeichnen
  - Echo in Spektrogramm umwandeln
  - Spektrogramm als Bild abspeichern

Im Notebook **02_CNN_Klassifikation.ipynb** ist der Quellcode und die Beschreibung für ein erstes KI experiment.
Dabei soll der Raum (Küche, Toilette, Wohnzimmer, Schlafzimmer) in welchem sich der Laptop befindet erkannt werden.
Dafür wurden mit dem Script 01_Trainingsdaten.ipynb Trainingsdaten erzeugt.(ca. 300 pro Raum).
Anschließend wurde mit diesen Daten ein einfaches CNN Trainiert.
