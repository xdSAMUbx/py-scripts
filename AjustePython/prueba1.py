from pathlib import Path
from typing import Optional, Union
import numpy as np
import pandas as pd

def genA(data:str):

    df = pd.read_csv(data)
    nodos = sorted(pd.unique(df[["ini","fin"]].values.ravel()))
    idx_nodo = {nodo: i for i, nodo in enumerate(nodos)} 
    numNodos= len(nodos)
    numAristas = len(df)
    A = np.zeros((numAristas,numNodos), dtype=int)
    for r, (u,v) in enumerate(zip(df['ini'],df['fin'])):
        A[r, idx_nodo[u]] = -1
        A[r, idx_nodo[v]] = +1

    return A

def GMM(data:str, ref:Optional[pd.DataFrame]=None, Weigth:bool = False):

    df = pd.read_csv(data)
    if not Weigth:
        P = np.eye(len(df))
    else:
        d = np.array(df.iloc[:,3])
        inv = 1/d
        P = np.diag(inv)
    
    A = genA(data)
    L = np.array(df.iloc[:,2], dtype = float).reshape(-1,1)
    ATP = A.T@P
    N = ATP@A
    c = ATP@L

    rowN = N.shape[0]
    colN = N.shape[1]

    if ref is not None:
        # n_par = ncol(A)
        n_par = A.shape[1]  # número de incógnitas (columnas de A)

        # n_ref = nrow(ref)
        n_ref = ref.shape[0]

        # Construir K: matriz n_par x n_ref llena de ceros
        # Filas = incógnitas (mismos nombres que columnas de A)
        # Cols = nombres de referencia declaradas en ref["nom"]
        rn = list(A.columns)           # nombres vértices incógnitos
        cn = list(ref["nom"])          # nombres vértices de referencia

        K = np.zeros((n_par, n_ref), dtype=float)

        # Buscar intersección de nombres (comunes)
        comunes = set(rn).intersection(cn)
        # Para cada nombre común, poner 1 en la posición (match)
        for name in comunes:
            i = rn.index(name)         # fila en K
            j = cn.index(name)         # columna en K
            K[i, j] = 1.0

        # Nc: matriz aumentada de tamaño (n_par + n_ref) x (n_par + n_ref)
        Nc = np.zeros((n_par + n_ref, n_par + n_ref), dtype=float)

        # Parte superior izquierda = N
        Nc[0:n_par, 0:n_par] = N

        # Parte superior derecha = K
        Nc[0:n_par, n_par:n_par + n_ref] = K

        # Parte inferior izquierda = K^T
        Nc[n_par:n_par + n_ref, 0:n_par] = K.T

        # RHS aumentado
        HCon = np.array(ref["h"], dtype=float).reshape(-1, 1)

        Cc = np.zeros((n_par + n_ref, 1), dtype=float)
        Cc[0:n_par, 0] = c
        Cc[n_par:n_par + n_ref, 0] = HCon[:, 0]

    else:

        rowNc = rowN + 1  # rowN viene de N.shape[0]
        colNc = colN + 1  # colN viene de N.shape[1]

        # Nc inicializada en ceros
        Nc = np.zeros((rowNc, colNc), dtype=float)
        Cc = np.zeros((rowNc, 1), dtype=float)

        # Bloque N
        Nc[0:rowN, 0:colN] = N

        # Columna extra de 1's arriba
        Nc[0:rowN, colNc - 1] = 1.0

        # Fila extra de 1's a la izquierda
        Nc[rowNc - 1, 0:colN] = 1.0

        # RHS
        Cc[0:rowN, :] = c
        Cc[rowNc - 1, 0] = 0.0

    x_full = np.linalg.solve(Nc, Cc)        # (n_par + extra, 1)
    x_par = x_full[:rowN, :]                # solo las incógnitas verdaderas (tamaño n_par x 1)
    Ax = A @ x_par 

    e = L - Ax
    L_Corr = L - e

    if ref is not None:
        return {"A": A, "P": P, "L": L,
                "x": x_full, "v": e, "K": K,
                "L_Corregida": L_Corr}
    else:
        return {"A": A, "P": P, "L": L,
            "x": x_full, "v": e, "L_Corregida": L_Corr}

def matriz_estilo_R(M: np.ndarray, nombre: str, fmt="{: .6f}"):
    """
    Devuelve un string que representa la matriz M con estilo similar a R:
          [,1]    [,2]   ...
    [1,]   1.000  0.000  ...
    [2,]   ...
    """
    # Asegurarse de que M sea 2D
    M = np.atleast_2d(M)

    n_rows, n_cols = M.shape

    # Encabezado de columnas
    # Ej: "      [,1]     [,2]     [,3]"
    header_cols = ["[,{}]".format(j+1) for j in range(n_cols)]
    # ancho fijo para alinear bonitamente
    # definimos un ancho de campo, p.ej. 12 caracteres
    col_width = 12

    header = " " * 6  # espacio para las etiquetas de fila "[i,]"
    header += "".join(h.rjust(col_width) for h in header_cols)

    # Filas
    rows_str = []
    for i in range(n_rows):
        row_label = "[{},]".format(i+1)
        valores = [fmt.format(M[i, j]) for j in range(n_cols)]
        fila = row_label.ljust(6) + "".join(v.rjust(col_width) for v in valores)
        rows_str.append(fila)

    cuerpo = "\n".join(rows_str)

    return f"{nombre}:\n{header}\n{cuerpo}\n"

path = "G:\\Otros ordenadores\\Mi PC\\IGAC\\EsquemasPruebas\\EjercicioGomez1.csv"

result = GMM(data=path,Weigth=True)

with open("informe_GMM.txt", "w", encoding="utf-8") as f:

    f.write(matriz_estilo_R(result["A"], "A", fmt="{: .6f}"))
    f.write("\n")

    f.write(matriz_estilo_R(result["P"], "P", fmt="{: .6f}"))
    f.write("\n")

    f.write(matriz_estilo_R(result["L"], "L", fmt="{: .6f}"))
    f.write("\n")

    f.write(matriz_estilo_R(result["x"], "x", fmt="{: .6f}"))
    f.write("\n")

    f.write(matriz_estilo_R(result["v"], "v", fmt="{: .6f}"))
    f.write("\n")

    f.write(matriz_estilo_R(result["L_Corregida"], "L_Corregida", fmt="{: .6f}"))
    f.write("\n")

    if "K" in result:
        f.write(matriz_estilo_R(result["K"], "K", fmt="{: .6f}"))
        f.write("\n")




