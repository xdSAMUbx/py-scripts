from typing import Optional
import math

# Antena Pasiva
def rActivEq(pt:Optional[float], gt: Optional[float], ar:Optional[float], 
             sigma:Optional[float], r:Optional[float]):
    return (pt*gt*ar*sigma)/((4*math.pi)**2*(r**5))

# Antena Activa
def rPassivEq(pt:Optional[float], gt:Optional[float], ar:Optional[float], sigma:Optional[float], 
              f:Optional[float], rt:Optional[float],rr:Optional[float]):
    return (pt*gt*ar*sigma*(f**4))/(((4*math.pi)**2)*(rt**2)*(rr**2))

if __name__ == "__main__":
    print("Hola")
