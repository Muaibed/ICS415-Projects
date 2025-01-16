from math import sqrt, inf
from drawing_base import DrawingBase


class RayTracing(DrawingBase):
    def __init__(self, width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres):
        super().__init__(width, height, viewport_size, projection_plane_z, background_color)
        self.camera_position = camera_position
        self.spheres = spheres


    def intersectRaySphere(self, origin, direction, sphere):
        """
        Computes the intersection of a ray and a sphere. Returns the values
        of t for the intersections.
        :type origin: Vector3
        :type direction: Vector3
        :type sphere: Sphere
        :rtype: [List[int]]
        """
        oc = origin - sphere.center
        k1 = direction.dot(direction)
        k2 = 2 * oc.dot(direction)
        k3 = oc.dot(oc) - sphere.radius * sphere.radius

        discriminant = k2 * k2 - 4 * k1 * k3
        if discriminant < 0:
            return [inf, inf]

        t1 = (-k2 + sqrt(discriminant)) / (2 * k1)
        t2 = (-k2 - sqrt(discriminant)) / (2 * k1)
        return [t1, t2]


    def traceRay(self, origin, direction, min_t, max_t):
        """
        Traces a ray against the set of spheres in the scene.
        :type origin: Vector3
        :type direction: Vector3
        :type min_t: float
        :type max_t: float
        :rtype: color
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

        if closest_sphere == None:
            return self.background_color

        return closest_sphere.color



    def run(self):
        image, pixels = self.initialize_image()

        for x in range(-self.width // 2, self.width // 2):
            for y in range(-self.height // 2, self.height // 2):
                direction = self.canvasToViewPort((x, y))
                color = self.traceRay(self.camera_position, direction, 1, inf)
                self.putPixel(pixels, x, y, color)

        image.save("raytracying01.png")

