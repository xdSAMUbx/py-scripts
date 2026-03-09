import pyshtools
import numpy as np

# grado máximo
lmax = 10

# crear coeficientes vacíos
# formato: (2, lmax+1, lmax+1)
# 0 = cos
# 1 = sin
coeffs = np.zeros((2, lmax+1, lmax+1))

# agregar algunos coeficientes
coeffs[0,2,0] = 1.0   # C20
coeffs[0,3,1] = 0.5   # C31
coeffs[1,3,1] = 0.2   # S31

# convertir a objeto SHCoeffs
clm = pyshtools.SHCoeffs.from_array(coeffs)

# expandir a grilla global
grid = clm.expand()

# imprimir dimensiones
print("Grid shape:", grid.data.shape)

# valor en un punto
print("Valor en lat=0 lon=0:", grid.data[90,0])