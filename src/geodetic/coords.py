import re
import math as mh
from typing import Tuple, Optional

# Función que calcula las coordenadas XYZ
def coordsXYZ(lat:Optional[float|int] = None, lon:Optional[float|int] = None,
              h:Optional[float] = None, a:Optional[float] = 6378137.0, 
              e2:Optional[float] = 6.669438e-3) -> Tuple[float, float, float]:

    if lat is None:
        print("Ingrese la latitud en formato DMS (Incluyendo N/S)")
        lat = grados()

    if lon is None:
        print("Ingrese la longitud en formato DMS (Incluyendo E/W)")
        lon = grados()

    if h is None:
        h = float(input("Ingrese la altura en metros: "))

    N : float = a / mh.sqrt(1 - e2 * (mh.sin(lat))**2) 
    X : float = (N + h) * mh.cos(lat) * mh.cos(lon)
    Y : float = (N + h) * mh.cos(lat) * mh.sin(lon)
    Z : float = (N*(1-e2)+ h) * mh.sin(lat)
    
    return [X,Y,Z]

# Función que entrega los grados en radianes para posteriores operaciones
def grados(val:Optional[str] = None) -> float | int:
    if val is None:
        val = input()

    pat = r'(\d+)°(\d+)[\'](\d+(?:\.\d+)?)"([NSEW])'
    coinc = re.match(pat, val)
    if coinc:
        gra : int = int(coinc.group(1)) 
        min : int = int(coinc.group(2))
        seg : float = float(coinc.group(3))
        hemis : str = coinc.group(4)
        graDec : float = gra + (min/60) + (seg/3600)
        graRad : float = graDec * 3.1416/180
        if hemis == "N" or hemis == "E":
            graRad = graRad
        elif hemis == "S" or hemis == "W":
            graRad = -(graRad)
        else:
            raise SyntaxError("No ingreso una dirección, formato invalido")
        
        print("Angulo Invalido") if (hemis == "N" or hemis == "S") and abs(graDec) > 90 else None
        print("Angulo Invalido") if (hemis == "E" or hemis == "W") and abs(graDec) > 360 else None
    
        return graRad
    else:
        raise SyntaxError("Formato Invalido")

if __name__ == "__main__":
    res = coordsXYZ()
    print(f"Las coordenadas para el punto son: \nX:{res[0]}\nY:{res[1]}\nZ:{res[2]}")
