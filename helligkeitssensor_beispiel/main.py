from ir_sensors import QTRRCSensors
import time

def wert_aufzeichnen(wert):
    skaliert = int(wert / 100)
    return ("[%4d] " % wert) + (skaliert * "#")  + ((10 - skaliert) * " ")



### INITIALISIERUNG ###
liniensensoren = QTRRCSensors() # immer angeschlossen an die Digital-Pins 18, 19, 17, 16, 15, 14



### HAUPTPROGRAMM ###
try:
    print("Helligkeit wird gelesen...")
    while True:
        # Sensor nach den Werten fragen:
        # gibt ein Array aus 6 Zahlen zurück: [außen_links, links, mitte_links, mitte_rechts, rechts, außen_rechts]
        # 0:  Sensor sieht gar nichts oder sehr dunkle Farbe oder Sensor nicht angeschlossen
        # 1024: sehr hell
        helligkeiten = liniensensoren.read()

        # Werte in der Konsole ausgeben:

        # Beispiel: nur eine Helligkeit benutzen:
        # print(helligkeiten[0]) # ganz links (wenn angeschlossen)
        # print(helligkeiten[5]) # ganz rechts (wenn angeschlossen)

        # alle Helligkeiten ausgeben:
        for helligkeit in helligkeiten:
            print(wert_aufzeichnen(helligkeit), end = "  ") # alles in eine Zeile schreiben
        print("") # neue Zeile

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Abbruch.")

finally:
    print("Programm Ende.")
