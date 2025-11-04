import re

# BLOCK: Patron que separa los bloques
BLOCK_RE = re.compile(r'^\s*(?P<code_block>[^+\s]+)\+[^?]*\?.*?(?P<method_block>[1-4]|10)\b')

# VERT: Patron que estandariza los vertices XXXX-XXXX-09
STD_VERT_RE = re.compile(r'^([A-Z0-9]+)([A-Z]{2,4})(\d{1,2})$')

# FECHA6: Extrae fechas
DATE6_RE = re.compile(r'(\d{6})')

# INI: siguiente línea del bloque. Se exige 83..[068]<valor> y se toma como ini si <valor> == 0
INI_RE = re.compile(r"""
    (?P<est>[A-Z0-9]+)\s+
    (?P<idx_83>83)\.\.(?P<p5_83>[25])(?P<p6_83>[068])(?P<val_83>[+-]?\d+)
""", re.X)

# FIN: línea BF completa (573, 574, 83)
FIN_RE_BF = re.compile(r"""
    (?P<est>[A-Z0-9]+)\s+
    (?P<idx_573>573)\.\.(?P<p6_573>[068])(?P<val_573>[+-]?\d+)\s+
    (?P<idx_574>574)\.\.(?P<p6_574>[068])(?P<val_574>[+-]?\d+)\s+
    (?P<idx_83>83)\.\.(?P<p5_83>[0125])(?P<p6_83>[068])(?P<val_83>[+-]?\d+)
""", re.X)