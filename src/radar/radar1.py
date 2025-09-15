from typing import Optional
import math

# Resolución
def rt(ct:Optional[float], theta:Optional[float]) -> float:
    return  ct/(2*math.cos(math.radians(theta)))

# Resoluación
def ra(h:Optional[float], lmd:Optional[float], d:Optional[float]):
    return h * (lmd/d)

# Antena Pasiva
def rActivEq(pt:Optional[float], gt: Optional[float], ar:Optional[float], 
             sigma:Optional[float],r:Optional[float], f:Optional[float]=1) -> float:
    """ 
        Para la ecuación del radar en su forma activa, se tienen los siguientes parametros:

        - pt: Potencia transmitida (Watts)
        - gt: Ganancia de la antena de transmición (En K o Decibeles)
        - ar: El area efectiva de la antena de recepción (m2)
        - sigma: Seccion transversal del radar o coeficiente de decaimiento del objetivo (m2)
        - f: Factor de propagación (K)
        - r: Distancia del objeto al receptor (el mismo emisor recibe)

        Devuelve:
        - pt: potencia reflejada de la antena de recepción
    """    
    return (pt*gt*ar*sigma*(f**2))/((4*math.pi)**2*(r**4))

# Antena Activa
def rPassivEq(pt:Optional[float], gt:Optional[float], ar:Optional[float], sigma:Optional[float], 
              f:Optional[float], rt:Optional[float],rr:Optional[float]) -> float:
    """ 
        Para la ecuación del radar en su forma activa, se tienen los siguientes parametros:

        - pt: Potencia transmitida (Watts)
        - gt: Ganancia de la antena de transmición (En K o Decibeles)
        - ar: El area efectiva de la antena de recepción (m2)
        - sigma: Seccion transversal del radar o coeficiente de decaimiento del objetivo (m2)
        - f: Factor de propagación (K)
        - rt: Distancia del transmisor al objetivo (m)
        - rr: Distancia del objetivo al receptor (m)

        Devuelve:
        - pt: potencia reflejada de la antena de recepción
    """
    return (pt*gt*ar*sigma*(f**4))/(((4*math.pi)**2)*(rt**2)*(rr**2))

def menu():
    
    print("Bienvenido al solucionador de los talleres 1 y 2 de sistemas de radar.")
    print("1) Ecuación de Radar para antena activa\n2) Ecuación de Radar para antena pasiva")
    print("3) Resolución en Rango\n4) Resolución en Azimut")
    op = int(input("Seleccione una opción: "))
    if op == 1:
        print("-----------------------------------------------")
        pt = float(input("Potencia transmitida: "))
        gt = float(input("Ganancia de la antena: "))
        ar = float(input("Area efectiva: "))
        sg = float(input("Coeficiente de decaimiento: "))
        f = float(input("Factor de propagación: "))
        rt = float(input("Distancia del transmisor: "))
        rr = float(input("Distancia del objetivo: "))
        res = rPassivEq(pt,gt,ar,sg,f,rt,rr)
        print("La respuesta es: ", res)
        print("En decibeles : ", math.log10(res))
    elif op == 2:
        print("-----------------------------------------------")
        pt = float(input("Potencia transmitida: "))
        gt = float(input("Ganancia de la antena: "))
        ar = float(input("Area efectiva: "))
        sg = float(input("Coeficiente de decaimiento: "))
        f = float(input("Factor de propagación (si varia, si no continue): "))
        r = float(input("Distancia: "))
        res = rActivEq(pt,gt,ar,sg,r,f)
        print("La respuesta es: ", res)
        print("En decibeles : ", math.log10(res))
 

if __name__ == "__main__":
    menu()
