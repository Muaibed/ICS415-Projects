from PIL import Image
from multiprocessing import Pool
from math import sqrt, inf
from vector3 import Vector3
from Assignment02.raytracing02 import RayTracing02


class RayTracing03(RayTracing02):
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
        )
        self.EPSILON = EPSILON
        self.recursion_depth = recursion_depth

    def ComputeLighting(self, point, normal, view, specular):
        """
        :type point: Vector3, location
        :type normal: Vector3, vector
        """
        intensity = 0

        for light in self.lights:
            if light.ltype == "AMBIENT":
                intensity += light.intensity
            else:
                vec_l = Vector3(0, 0, 0)
                t_max = 1
                if light.ltype == "POINT":
                    vec_l = light.position - point
                    t_max = 1
                else:
                    vec_l = light.position  # direction
                    t_max = inf

                # Shadow check
                blocker, _  = self.closestIntersection(point, vec_l, self.EPSILON, t_max)
                if blocker:
                    continue

                n_dot_l = normal.dot(vec_l)
                if n_dot_l > 0:
                    intensity += (
                        light.intensity * n_dot_l / (normal.length * vec_l.length)
                    )

                if specular != -1:
                    vec_r = 2 * normal * normal.dot(vec_l) - vec_l
                    r_dot_v = vec_r.dot(view)
                    if r_dot_v > 0:
                        intensity += light.intensity * pow(
                            (r_dot_v / (view.length * vec_r.length)), specular
                        )

        return intensity
    
    def closestIntersection(self, origin, direction, min_t, max_t):
        """
        Find the closest intersection between a ray and the spheres in the scene.
        :type origin: Vector3
        :type direction: Vector3
        :type min_t: float
        :type max_t: float
        :rtype: closest_sphere, closest_t
        """
        closest_t = inf
        closest_sphere = None

        for sphere in self.spheres:
            t1, t2 = self.intersectRaySphere(origin, direction, sphere)
            if t1 < closest_t and min_t < t1 and t1 < max_t:
                closest_t = t1
                closest_sphere = sphere
            if t2 < closest_t and min_t < t2 and t2 < max_t:
                closest_t = t2
                closest_sphere = sphere

        return (closest_sphere, closest_t)
    
    def reflectRay(self, R, N):
        return 2 * N * N.dot(R) - R

    def traceRay(self, origin, direction, min_t, max_t, depth):
        """
        Traces a ray against the set of spheres in the scene.
        :type origin: Vector3
        :type direction: Vector3
        :type min_t: float
        :type max_t: float
        :rtype: color
        """
        (closest_sphere, closest_t) = self.closestIntersection(origin, direction, min_t, max_t)

        if closest_sphere == None:
            # for calculation
            return Vector3(self.background_color[0], self.background_color[1], self.background_color[2]) 

        point = origin + closest_t * direction
        normal = (point - closest_sphere.center).normalize()

        local_color_r = closest_sphere.color[0] * self.ComputeLighting(
            point, normal, -direction, closest_sphere.specular
        )
        local_color_g = closest_sphere.color[1] * self.ComputeLighting(
            point, normal, -direction, closest_sphere.specular
        )
        local_color_b = closest_sphere.color[2] * self.ComputeLighting(
            point, normal, -direction, closest_sphere.specular
        )
        
        r = closest_sphere.reflective
        if r <= 0 or depth <=0:
            return (int(local_color_r), int(local_color_g), int(local_color_b))
        
        reflected_ray = self.reflectRay(-direction, normal)
        reflected_color = self.traceRay(point, reflected_ray, self.EPSILON, inf, depth-1)

        reflected_color_r = (1 - r) * local_color_r + r * reflected_color[0]
        reflected_color_g = (1 - r) * local_color_g + r * reflected_color[1]
        reflected_color_b = (1 - r) * local_color_b + r * reflected_color[2] 

        return (int(reflected_color_r), int(reflected_color_g), int(reflected_color_b))
    
    def render_pixel(self, args):
        x, y = args
        direction = self.canvasToViewPort((x, y))
        return (x, y, self.traceRay(self.camera_position, direction, 1, inf, self.recursion_depth))
    
    def run(self):
        image, pixels = self.initialize_image()

        pool = Pool()

        pixel_args = [(x, y) for x in range(-self.width//2, self.width//2) 
                      for y in range(-self.height//2, self.height//2)]

        for x, y, color in pool.map(self.render_pixel, pixel_args):
            self.putPixel(pixels, x, y, color)

        image.save("images/" + self.save_filename)