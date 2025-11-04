from typing import Union, Optional, List, Dict, Iterator, Tuple
from pathlib import Path
from datetime import date
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

# FECHA6: Extrae fechas
FECHA6_RE = re.compile(r'(\d{6})')

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
def vert_std(codigo:str) -> str:
    code_mayusc = codigo.replace("-", "").replace(" ", "").upper()
    m = VERT_RE.match(code_mayusc)
    if m:
        g1, g2, g3 = m.groups()
        return f"{g1}-{g2}-{g3}"
    
    return codigo

# Función que ordena el archivo orden
def clasi_orden(forden:Path):
    ida: List[Dict[str, str]] = []
    reg: List[Dict[str, str]] = []

    with open(forden, "r", encoding="utf-8") as f:
        # suponemos primera línea encabezado
        for i, linea in enumerate(f.readlines()[1:]):
            linea = linea.strip()
            if not linea or ";" not in linea:
                continue
            a, b = linea.split(";")
            a = vert_std(a)
            b = vert_std(b)
            if i % 2 == 0:
                ida.append({"ini" : a, "fin": b})
            else:
                reg.append({"ini" : a, "fin": b})

    return [ida,reg]

def ext_fecha(fname:str):
    m = FECHA6_RE.search(fname)
    if not m:
        return None
    
    y, mth, d = int(m.group(1)[:2]), int(m.group(1)[2:4]), int(m.group(1)[4:6])

    # regla para siglo: 00–49 → 2000s, 50–99 → 1900s
    year = 2000 + y if y < 50 else 1900 + y

    try:
        return date(year, mth, d).isoformat()
    except ValueError:
        return None

# 1) Mantener parser_ini SIN listas: retorna 1 tupla o None
def parser_ini(linea: str) -> Optional[Tuple[str, float]]:
    s = linea.strip()
    m = INI_RE.search(s)
    if not m:
        return None

    ini = vert_std(m.group(1).lstrip('0'))

    # flag = valor inicial 83..26 (escalado). 0.0 si no existe o es cero.
    flag_init = 0.0
    try:
        # Solo si el regex del INI trae estos grupos
        gidx = m.re.groupindex
        if ('val_83' in gidx) and ('p6_83' in gidx):
            g6 = m.group('p6_83')
            base = 1e4 if g6 == '6' else 1e5 if g6 == '8' else None
            if base is not None:
                raw = m.group('val_83')
                if raw is not None:
                    v83 = float(raw) / base
                    # Trata casi-cero como cero para estabilidad numérica
                    if abs(v83) > 1e-12:
                        flag_init = v83
    except Exception:
        # Si algo no cuadra en la línea, dejamos 0.0 (comportamiento seguro)
        pass

    return (ini, flag_init)


# 2) parser_med: sin cambios lógicos; retorna dict o None
def parser_med(m_fin):
    if m_fin is not None and m_fin.group('p5_83') == '2':
        g6 = m_fin.group('p6_83')
        base = 1e4 if g6 == '6' else 1e5 if g6 == '8' else None
        if base is None:
            return None
        dif_dist   = float(m_fin.group('val_573')) / base
        total_dist = float(m_fin.group('val_574')) / base
        dif_height = float(m_fin.group('val_83'))   / base  # <- valor "final" 83
    else:
        raise SyntaxError("No se realizó la corrección por curvatura")

    return {"fin": None, "dif_dist": dif_dist, "total_dist": total_dist, "dif_height": dif_height}


# 3) parser_fin: sin cambios de contrato
def parser_fin(prev_line: Optional[str], curr_line: str) -> Optional[Dict[str, float | str]]:
    if prev_line is None:
        return None

    m_block = BLOCK_RE.search(curr_line.strip())
    if m_block is None:
        return None

    if m_block.group('codigo') == '1':
        m_fin = FIN_RE_BF.search(prev_line.strip())
        if not m_fin:
            return None

        fin: str = vert_std(m_fin.group('est').lstrip('0'))
        datos_med = parser_med(m_fin)
        if datos_med is None:
            return {"fin": fin}
        datos_med["fin"] = fin
        return datos_med

    return None


# 4) ext_vert_iter: streaming por archivo/línea
def ext_vert_iter(crudos: Path, ext: str) -> Iterator[Dict[str, object]]:
    suf = ext if ext.startswith(".") else f".{ext}"

    def _fin_from_line(line: Optional[str]) -> Optional[Dict[str, float | str]]:
        if not line:
            return None
        m_fin = FIN_RE_BF.search(line.strip())
        if not m_fin:
            return None
        fin: str = vert_std(m_fin.group('est').lstrip('0'))
        datos_med = parser_med(m_fin)
        if datos_med is None:
            return {"fin": fin}
        datos_med["fin"] = fin
        return datos_med

    for file in sorted(crudos.glob(f"*{suf}"), key=lambda f: f.name):
        if not file.is_file():
            continue

        pending_ini: Optional[Tuple[str, float]] = None  # (ini, flag_ini)
        prev_line: Optional[str] = None
        last_nonempty: Optional[str] = None

        with open(file, "r", encoding="utf-8", errors="replace") as f:
            for i, curr_line in enumerate(f):
                # INI: guardamos ini y flag_ini (valor 83 inicial escalado o 0.0)
                v_ini = parser_ini(curr_line)
                if v_ini is not None:
                    pending_ini = v_ini

                # FIN de bloque
                v_fin = parser_fin(prev_line, curr_line)
                fecha = ext_fecha(file.name)

                if v_fin is not None:
                    if pending_ini is not None:
                        ini, flag_ini = pending_ini
                        out = {"ini": ini, **v_fin}

                        # Ajuste en línea: dif_height = final_83 - flag_ini (si flag_ini != 0.0)
                        if ("dif_height" in out) and (out["dif_height"] is not None) and (abs(flag_ini) > 1e-12):
                            out["dif_height"] = float(out["dif_height"]) - float(flag_ini)

                        # Guarda flag_ini para poder recalcular "al final" si lo prefieres
                        out.update({
                            "flag_ini": flag_ini,
                            "curv": 'Si' if abs(flag_ini) <= 1e-12 else 'No',
                            "file": file.name,
                            "date": fecha,
                        })
                        yield out
                        pending_ini = None
                    else:
                        # No hubo INI (caso raro): emitir sin ajuste, sin flag_ini
                        yield {**v_fin, "file": file.name, "date": fecha}

                if curr_line.strip():
                    last_nonempty = curr_line
                prev_line = curr_line

        # EOF: cierre de pendiente
        if pending_ini is not None:
            fecha = ext_fecha(file.name)
            ini, flag_ini = pending_ini
            v_fin_eof = _fin_from_line(last_nonempty)

            if v_fin_eof is not None:
                out = {"ini": ini, **v_fin_eof}
                if ("dif_height" in out) and (out["dif_height"] is not None) and (abs(flag_ini) > 1e-12):
                    out["dif_height"] = float(out["dif_height"]) - float(flag_ini)
                out.update({
                    "flag_ini": flag_ini,
                    "curv": 'Si' if abs(flag_ini) <= 1e-12 else 'No',
                    "file": file.name,
                    "date": fecha,
                })
                yield out
            # Si no hay FIN detectable, no emitimos nada (no hay observación completa)
            
def ext_vert(crudos: Path, ext: str) -> pd.DataFrame:
    rows = list(ext_vert_iter(crudos, ext))
    return pd.DataFrame.from_records(rows) 

def gen_ext(crudos: Path, orden: Path, ext: str):
    df_vert = ext_vert(crudos, ext)
    ida, reg = clasi_orden(orden)

    df_ida = pd.DataFrame(ida, columns=["ini", "fin"])
    df_reg = pd.DataFrame(reg, columns=["ini", "fin"])

    # Clave única por tramo (ini-fin)
    df_vert["key"] = df_vert["ini"].astype(str) + "_" + df_vert["fin"].astype(str)
    df_ida["key"]  = df_ida["ini"].astype(str)  + "_" + df_ida["fin"].astype(str)
    df_reg["key"]  = df_reg["ini"].astype(str)  + "_" + df_reg["fin"].astype(str)

    # Orden según posición en df_ida y df_reg
    orden_dict_I = {k: i for i, k in enumerate(df_ida["key"])}
    orden_dict_R = {k: i for i, k in enumerate(df_reg["key"])}

    # Mapear orden a df_vert
    df_vert["orden_I"] = df_vert["key"].map(orden_dict_I)
    df_vert["orden_R"] = df_vert["key"].map(orden_dict_R)

    # Filtrar y ordenar para IDA
    df_vert_I = (
        df_vert[df_vert["key"].isin(df_ida["key"])]
        .sort_values("orden_I", kind="stable")
        .drop(columns=["key", "orden_I", "orden_R"], errors="ignore")
        .reset_index(drop=True)
    )

    # Filtrar y ordenar para REGRESO
    df_vert_R = (
        df_vert[df_vert["key"].isin(df_reg["key"])]
        .sort_values("orden_R", kind="stable")
        .drop(columns=["key", "orden_I", "orden_R"], errors="ignore")
        .reset_index(drop=True)
    )

    return df_vert_I, df_vert_R

# --- Uso ---
df_ida, df_reg = gen_ext(L5Crudos, L5Orden, ".GSI")

df_vert = ext_vert(L5Crudos,".GSI")

df_vert.to_excel("vertices-prueba-1.xlsx",index=False)
df_ida.to_excel("prueba-ida.xlsx", index=False)
df_reg.to_excel("prueba-regreso.xlsx", index=False)
