import sys
import os
OSGEO4W_ROOT = r"C:\Users\samue\AppData\Local\Programs\OSGeo4W"
# --- DLLs ---
os.add_dll_directory(os.path.join(OSGEO4W_ROOT, "bin"))
os.add_dll_directory(os.path.join(OSGEO4W_ROOT, "apps", "qgis", "bin"))
os.add_dll_directory(os.path.join(OSGEO4W_ROOT, "apps", "qt5", "bin"))
os.add_dll_directory(os.path.join(OSGEO4W_ROOT, "apps", "Python312"))
# --- Variables de entorno ---
os.environ["OSGEO4W_ROOT"] = OSGEO4W_ROOT
os.environ["QGIS_PREFIX_PATH"] = os.path.join(OSGEO4W_ROOT, "apps", "qgis")
os.environ["GDAL_FILENAME_IS_UTF8"] = "YES"
os.environ["VSI_CACHE"] = "TRUE"
os.environ["VSI_CACHE_SIZE"] = "1000000"
os.environ["PROJ_DATA"] = os.path.join(OSGEO4W_ROOT, "share", "proj")  # Evita conflicto con PostgreSQL
os.environ["QT_PLUGIN_PATH"] = os.path.join(OSGEO4W_ROOT, "apps", "qgis", "qtplugins") + ";" + \
                                os.path.join(OSGEO4W_ROOT, "apps", "qt5", "plugins")
os.environ["PATH"] = os.path.join(OSGEO4W_ROOT, "bin") + ";" + \
                     os.path.join(OSGEO4W_ROOT, "apps", "qgis", "bin") + ";" + \
                     os.path.join(OSGEO4W_ROOT, "apps", "qt5", "bin") + ";" + \
                     os.environ["PATH"]
# --- Rutas de Python ---
sys.path.insert(0, os.path.join(OSGEO4W_ROOT, "apps", "Python312", "Lib", "site-packages"))
sys.path.insert(0, os.path.join(OSGEO4W_ROOT, "apps", "qgis", "python"))
sys.path.insert(0, os.path.join(OSGEO4W_ROOT, "apps", "qgis", "python", "plugins"))
# --- Inicializar QGIS sin interfaz gráfica ---
from qgis.core import QgsApplication, Qgis
app = QgsApplication([], False)
app.setPrefixPath(os.path.join(OSGEO4W_ROOT, "apps", "qgis"), True)
app.initQgis()
# --- Prueba completa ---
from osgeo import gdal
from qgis.core import QgsVectorLayer, QgsProject
print("GDAL version:", gdal.__version__)
print("QGIS version:", Qgis.QGIS_VERSION)
# --- Siempre cerrar QGIS al final ---
app.exitQgis()