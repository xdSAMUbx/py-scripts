from shapely import distance, Point

punto1 = Point(0,0)
punto2 = Point(1,1)
dist = punto1.distance(punto2)
print(f"{dist:.4f}")