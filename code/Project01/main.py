import sys
import os
# Modify the sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
from collections import namedtuple
from vector3 import Vector3
from Assignment02.raytracing02 import Light 
from Assignment03.raytracing03 import RayTracing03

Sphere = namedtuple("Sphere", ["center", "radius", "color", 'specular', 'reflective'])

viewport_size = 1
projection_plane_z = 1
camera_position = Vector3(0, 1, 0)
background_color = (230, 230, 255)
spheres = [
    Sphere(Vector3(0.0, -1000.0, 0.0), 1000.0, Vector3(200, 200, 200), 0, 0), # Ground
    Sphere(Vector3(-0.4, 0.8, 8), 0.8, (255, 255, 0), 0, 0),
    Sphere(Vector3(0.3, 0.8, 6), 0.8, (0, 0, 255), 0, 0.6),
    Sphere(Vector3(0.9, 0.8, 4), 0.8, (255, 255, 0), 0, 0.8),
]

    
def generate_sphere(radius, specular, reflective):
    x = random.uniform(-5, 5)
    z = random.uniform(-10, 10)
    reflective = random.random() ** 3
    color = Vector3(random.uniform(0,255), random.uniform(0,255), random.uniform(0,255))
    return Sphere(Vector3(x, radius, z), radius, color, specular, reflective)


matt_spheres = 200
reflective_spheres = 20
semireflective_spheres = 100

specular = 0
radius = 0.125
for _ in range(matt_spheres):
    reflective = 0
    spheres.append(generate_sphere(radius, specular, reflective))

for _ in range(reflective_spheres):
    reflective = 0.8
    spheres.append(generate_sphere(radius, specular, reflective))

for _ in range(semireflective_spheres):
    reflective = random.random() ** 3
    spheres.append(generate_sphere(radius, specular, reflective))    


width = 2000
height = 2000

lights = [
  Light('AMBIENT', 0.4),
  Light('DIRECTIONAL', 0.2, Vector3(1, 4, 4))
]

EPSILON = 0.001
recursion_depth = 3

if __name__ == "__main__":
    app = RayTracing03("Project01.png", width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres, lights, EPSILON, recursion_depth)
    app.run()
