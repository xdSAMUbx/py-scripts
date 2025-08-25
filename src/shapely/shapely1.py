import matplotlib.pyplot as plt
from shapely import Polygon

poly = Polygon([(0,0),(0,1),(1,1),(1,0)])
fig, ax = plt.subplots(figsize=(6,6))
x,y = poly.exterior.xy

ax.fill(x, y, color='blue', alpha=0.5, label='Polígono')
ax.plot(x, y, color='black', linewidth=3, solid_capstyle='round')

ax.set_title("Visualización de una geometría de Shapely")
ax.set_aspect('equal', 'box')
ax.legend()
ax.grid(True)
plt.show()