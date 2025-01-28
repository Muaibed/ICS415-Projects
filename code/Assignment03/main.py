import sys
import os
# Modify the sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collections import namedtuple
from vector3 import Vector3
from Assignment02.raytracing02 import Light 
from raytracing03 import RayTracing03

Sphere = namedtuple("Sphere", ["center", "radius", "color", 'specular', 'reflective'])

viewport_size = 1
projection_plane_z = 1
camera_position = Vector3(0, 0, 0)
background_color = (0, 0, 0)
spheres = [
    Sphere(Vector3(0.0, -1.0, 3.0), 1.0, (255, 0, 0), 500, 0.2),
    Sphere(Vector3(2.0, 0.0, 4.0), 1.0, (0, 0, 255), 500, 0.3),
    Sphere(Vector3(-2.0, 0.0, 4.0), 1.0, (0, 255, 0), 10, 0.4),
    Sphere(Vector3(0.0, -5001.0, 0.0), 5000.0, Vector3(255, 255, 0), 1000, 0.5),
]

width = 600
height = 600

lights = [
  Light('AMBIENT', 0.2),
  Light('POINT', 0.6, Vector3(2, 1, 0)),
  Light('DIRECTIONAL', 0.2, Vector3(1, 4, 4))
]

EPSILON = 0.001
recursion_depth = 3

if __name__ == "__main__":
    app = RayTracing03(width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres, lights, EPSILON, recursion_depth)
    app.run()
