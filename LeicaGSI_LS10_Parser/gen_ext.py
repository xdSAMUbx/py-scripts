from typing import Union, Optional, List, Dict, Iterable, Tuple
from pathlib import Path
import pandas as pd
import re

PATH = Path("G:\\Otros ordenadores\\Mi PC\\IGAC\\archivosPrueba\\Archivos_Pruebas\\L5_GSI_1")
L5Crudos = PATH / 'CRUDOS_L5'
L5Orden = PATH / 'Orden_L5' / 'L5_Principio_Linea;Fin_linea.txt'
crudos = [p for p in L5Crudos.iterdir() if p.is_file() is True]

# --- patrones base ---
# BLOCK: Patron que separa los bloques
BLOCK_RE = re.compile(r'^\s*(?P<grupo>[^+\s]+)\+[^?]*\?.*?(?P<codigo>[1-4]|10)\b')

# VERT: Patron que estandariza los vertices XXXX-XXXX-09
VERT_RE = re.compile(r'^([A-Z0-9]+)([A-Z]{2,4})(\d{1,2})$')

# INI: siguiente línea del bloque. Se exige 83..[068]<valor> y se toma como ini si <valor> == 0
INI_RE = re.compile(r"""
    (?P<est>[A-Z0-9]+)\s+
    (?P<idx_573>83)\.\.5(?P<p6_83>[068])(?P<val_83>[+-]?\d+)
""", re.X)

# FIN: línea BF completa (573, 574, 83)
FIN_RE_BF = re.compile(r"""
    (?P<est>[A-Z0-9]+)\s+
    (?P<idx_573>573)\.\.(?P<p6_573>[068])(?P<val_573>[+-]?\d+)\s+
    (?P<idx_574>574)\.\.(?P<p6_574>[068])(?P<val_574>[+-]?\d+)\s+
    (?P<idx_83>83)\.\.(?P<p5_83>[0125])(?P<p6_83>[068])(?P<val_83>[+-]?\d+)
""", re.X)

# Función que estandariza las nomenclaturas
def vert_std(codigo:str):
    code_mayusc = codigo.replace("-", "").replace(" ", "").upper()
    m = VERT_RE.match(code_mayusc)
    if m:
        g1, g2, g3 = m.groups()
        return f"{g1}-{g2}-{g3}"
    
    return codigo

# 1) Mantenga parser_ini sin listas: retorna 1 tupla o None
def parser_ini(linea: str) -> Optional[Tuple[str, str]]:
    s = linea.strip()
    m = INI_RE.search(s)
    if not m:
        return None
    # Comparación textual (sin int): +00000000 => flag '0'
    flag = '0' if m.group(4).lstrip('+-0') == "" else '1'
    ini = vert_std(m.group(1).lstrip('0'))
    return (ini, flag)

# 2) parser_med: sin cambios lógicos; retorna dict o None
def parser_med(m_fin):
    if m_fin is not None and m_fin.group('p5_83') == '2':
        g6 = m_fin.group('p6_83')
        base = 1e4 if g6 == '6' else 1e5 if g6 == '8' else None
        if base is None:
            return None
        dif_dist   = float(m_fin.group('val_573')) / base
        total_dist = float(m_fin.group('val_574')) / base
        dif_height = float(m_fin.group('val_83'))   / base
    else:
        raise SyntaxError("No se realizó la corrección por curvatura")

    return {"dif_dist": dif_dist, "total_dist": total_dist, "dif_height": dif_height}

# 3) parser_fin: retorna SIEMPRE dict o None (sin listas)
def parser_fin(prev_line: Optional[str], curr_line: str, *, last:bool = True) -> Optional[Dict[str, float | str]]:
    if prev_line is None:
        return None

    m_block = BLOCK_RE.search(curr_line.strip())
    if m_block is None:
        return None

    if m_block.group('codigo') == '1':
        m_fin = FIN_RE_BF.search(prev_line.strip())
        if not m_fin:
            return None

        fin = vert_std(m_fin.group('est').lstrip('0'))
        datos_med = parser_med(m_fin)
        if datos_med is None:
            return {"fin": fin}
        # fusiona sin copiar más de lo necesario
        datos_med["fin"] = fin
        return datos_med

    # Código '2' (si aplica en el futuro)
    return None

# 4) ext_vert: streaming por archivo/ línea, sin diccionarios intermedios
def ext_vert(crudos: Path, ext: str) -> List[Dict[str, object]]:
    est: List[Dict[str, object]] = []
    suf = ext if ext.startswith(".") else f".{ext}"

    # Itera directo por archivos; evita read_lines y dict gigante en RAM
    for file in sorted(crudos.glob(f"*{suf}"), key=lambda f: f.name):
        if not file.is_file():
            continue

        pending_ini: Optional[Tuple[str, str]] = None
        prev_line: Optional[str] = None

        # Lectura en streaming, robusta a errores de encoding
        with open(file, "r", encoding="utf-8", errors="replace") as f:
            for curr_line in f:
                # 1) Inicios: guarde el último visto (tupla)
                v_ini = parser_ini(curr_line)
                if v_ini is not None:
                    pending_ini = v_ini

                # 2) Fines BF: se disparan por la línea actual (bloque)
                v_fin = parser_fin(prev_line, curr_line)
                if v_fin is not None:
                    if pending_ini is not None:
                        ini, flag = pending_ini
                        # compone un único registro; evita copias innecesarias
                        est.append({
                            "ini": (ini, flag),
                            **v_fin,
                            "file": file.name
                        })
                        pending_ini = None
                    else:
                        est.append({**v_fin, "file": file.name})

                # Ventana deslizante
                prev_line = curr_line

    return est

# Parser vertices inicio
print(ext_vert(L5Crudos, ".GSI"))