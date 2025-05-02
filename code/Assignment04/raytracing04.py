from PIL import Image
from typing import Tuple, Union
import numpy as np
from numba import jit
from math import sqrt, inf
from vector3 import Vector3
from Assignment03.raytracing03 import RayTracing03

from multiprocessing import Pool
import trimesh


class RayTracing04(RayTracing03):
    def __init__(
        self,
        save_filename,
        width,
        height,
        viewport_size,
        projection_plane_z,
        background_color,
        camera_position,
        spheres,
        lights,
        EPSILON,
        recursion_depth,
        bunny_filename,
    ):
        super().__init__(
            save_filename,
            width,
            height,
            viewport_size,
            projection_plane_z,
            background_color,
            camera_position,
            spheres,
            lights,
            EPSILON,
            recursion_depth
        )
        self.bunny_filename = bunny_filename
        self.triangles = self.prepare_triangles()

    def load_obj(self):
        vertices = []
        faces = []

        # with open(self.bunny_filename, "r") as file:
        #     for line in file:
        #         parts = line.strip().split()
        #         if not parts:
        #             continue
        #         if parts[0] == "v":  # Vertex
        #             vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        #         elif parts[0] == "f":  # Face (1-based index)
        #             face = [int(index.split("/")[0]) - 1 for index in parts[1:4]]
        #             faces.append(face)


        # Load the Stanford Bunny model
        mesh = trimesh.load(self.bunny_filename)  # Or bunny.ply

        # Get the vertex positions
        vertices = mesh.vertices

        scale_factor = 10  # Adjust as needed
        vertices *= scale_factor

        # Get the face indices (each face consists of 3 vertex indices)
        faces = mesh.faces

        # vertices = np.array([
        #     [ 1,  1,  0],  # v0 (Base)
        #     [-1,  1,  0],  # v1 (Base)
        #     [-1, -1,  0],  # v2 (Base)
        #     [ 1, -1,  0],  # v3 (Base)
        #     [ 0,  0,  1]   # v4 (Apex)
        # ])

        
        # faces = np.array([
        #     [0, 1, 2],  # Base triangle 1
        #     [0, 2, 3],  # Base triangle 2
        #     [0, 1, 4],  # Side triangle 1
        #     [1, 2, 4],  # Side triangle 2
        #     [2, 3, 4],  # Side triangle 3
        #     [3, 0, 4]   # Side triangle 4
        # ])

        return vertices, faces

    def prepare_triangles(self):
        vertices, faces = self.load_obj()

        triangles = []
        # for face in faces:
        #     triangles.append(vertices[face])
        triangles = [(vertices[f[0]], vertices[f[1]], vertices[f[2]]) for f in faces]

        print(np.array(triangles))

        # vertices = np.array([[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [10.0, 0.0, 0.0]])
    
        # return vertices
        return np.array(triangles)


    def ray_triangle_intersection(
        self,
        vertices: np.ndarray,
        ray_origin: np.ndarray,
        ray_direction: np.ndarray,
        culling: bool = True,
    ) -> Union[bool, Tuple[float, float, float]]:
        """
        Implementation of the Möller-Trumbore ray-triangle intersection algorithm.

        Parameters
        ----------
        vertices : np.ndarray
            2D array with the x, y and z coordinates of the triangle vertices as rows.
        ray_origin : np.ndarray
            Ray origin.
        ray_direction : np.ndarray
            Ray direction.
        culling : bool, optional
            If True, back facing triangles are discarded. When the ray hits the
            triangle from "behind" (the ray and the normal points in the same
            direction), the triangle is said to be back-facing. In this case the
            determinant is negative.
            The default is False.
        epsilon : float, optional
            Tolerance. The default is 1e-6.

        Returns
        -------
        Union[bool, Tuple[float, float, float]]
            If the ray and triangle do not intersect False is always returned.
            Otherwise, the distance and the barycentric coordinates u and v are returned.

        References
        ----------
        Möller, T., & Trumbore, B. (1997). Fast, minimum storage ray-triangle
        intersection. Journal of graphics tools, 2(1), 21-28.

        https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/moller-trumbore-ray-triangle-intersection

        Examples
        --------

        >>> vertices = np.array([[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [10.0, 0.0, 0.0]])
        >>> ray_origin = np.array([1.0, 1.0, 1.0])
        >>> ray_direction = np.array([0.0, 0.0, -1.0])
        >>> intersection = ray_triangle_intersection(vertices, ray_origin, ray_direction)
        (1.0, 0.1, 0.1)

        """
        vertex_0 = vertices[0]
        vertex_1 = vertices[1]
        vertex_2 = vertices[2]

        edge_1 = vertex_1 - vertex_0
        edge_2 = vertex_2 - vertex_0

        p_vec = np.cross(ray_direction, edge_2)

        determinant = np.dot(p_vec, edge_1)

        if culling:
            if determinant < self.EPSILON:
                return False

            t_vec = ray_origin - vertex_0
            u_ = np.dot(p_vec, t_vec)
            if u_ < 0.0 or u_ > determinant:
                return False

            q_vec = np.cross(t_vec, edge_1)
            v_ = np.dot(q_vec, ray_direction)
            if v_ < 0.0 or (u_ + v_) > determinant:
                return False

            inv_determinant = 1.0 / determinant
            t = np.dot(q_vec, edge_2) * inv_determinant
            u = u_ * inv_determinant
            v = v_ * inv_determinant

            return t, u, v

        else:
            if np.abs(determinant) < self.EPSILON:
                return False

            inv_determinant = 1.0 / determinant

            t_vec = ray_origin - vertex_0
            u = np.dot(p_vec, t_vec) * inv_determinant
            if u < 0.0 or u > 1.0:
                return False

            q_vec = np.cross(t_vec, edge_1)
            v = np.dot(q_vec, ray_direction) * inv_determinant
            if v < 0.0 or (u + v) > 1.0:
                return False

            t = np.dot(q_vec, edge_2) * inv_determinant
            if t < self.EPSILON:
                return False
            return t, u, v

    def traceRay(self, origin, direction, t_min, t_max):
        closest_t = inf
        hit_color = self.background_color

        direction = np.array([direction[0], direction[1], direction[2]])

        origin = np.array([0.0, 2.0, -2.0])
        for triangle in self.triangles:
            # print(triangle)
            r = self.ray_triangle_intersection(triangle, origin, direction)

            if r is not False:
                print(r)
                t, u, v = r
                if t is not None and t_min <= t < closest_t and t <= t_max:
                    closest_t = t
                    hit_color = (255,255,255)

        return hit_color

    
    def render_pixel(self, args):
        x, y = args
        direction = self.canvasToViewPort((x, y))
        return (x, y, self.traceRay(self.camera_position, direction, 1, float("inf")))


    def run(self):
        image, pixels = self.initialize_image()


        # for x in range(-self.width // 2, self.width // 2):
        #     for y in range(-self.height // 2, self.height // 2):
        #         direction = self.canvasToViewPort((x, y))
        #         color = self.traceRay(self.camera_position, direction, 1, inf)
        #         self.putPixel(pixels, x, y, color)

        pool = Pool()

        pixel_args = [(x, y) for x in range(-self.width//2, self.width//2) 
                      for y in range(-self.height//2, self.height//2)]

        for x, y, color in pool.map(self.render_pixel, pixel_args):
            self.putPixel(pixels, x, y, color)


        image.save("images/raytracying04.png")
