def wert_aufzeichnen(wert: float):
    skaliert = int(wert / 100)
    return ("[%4d] " % wert) + (skaliert * "#")  + ((10 - skaliert) * " ")