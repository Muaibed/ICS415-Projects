import sys
import os
# Modify the sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collections import namedtuple
from vector3 import Vector3
from raytracing01 import RayTracing01

Sphere = namedtuple("Sphere", ["center", "radius", "color"])

viewport_size = 1
projection_plane_z = 1
camera_position = Vector3(0, 0, 0)
background_color = (255, 255, 255)
spheres = [
    Sphere(Vector3(0.0, -1.0, 3.0), 1.0, (237, 31, 37)),
    Sphere(Vector3(2.0, 0.0, 4.0), 1.0, (56, 82, 164)),
    Sphere(Vector3(-2.0, 0.0, 4.0), 1.0, (106, 188, 68)),
]

width = 600
height = 600

if __name__ == "__main__":
    app = RayTracing01(width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres)
    app.run()
