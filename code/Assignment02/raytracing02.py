from PIL import Image
from math import sqrt, inf
from vector3 import Vector3
from Assignment01.raytracing01 import RayTracing01


class RayTracing02(RayTracing01):
    def __init__(self, width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres, lights):
        super().__init__(width, height, viewport_size, projection_plane_z, background_color, camera_position, spheres)
        self.lights = lights
        
    def ComputeLighting(self, point, normal, view, specular):
        """
        :type point: Vector3, location
        :type normal: Vector3, vector
        """
        intensity = 0

        for light in self.lights:
            if light.ltype == 'AMBIENT':
                intensity += light.intensity
            else:
                vec_l = Vector3(0 , 0, 0)
                if light.ltype == 'POINT':
                    vec_l = light.position - point 
                else:
                    vec_l = -light.position # direction

                n_dot_l = normal.dot(vec_l)
                if n_dot_l > 0:
                    intensity += light.intensity * n_dot_l / (normal.length * vec_l.length)

                if specular != -1:
                    vec_r = 2 * normal * normal.dot(vec_l)
                    r_dot_v = view.dot(vec_r)
                    if r_dot_v > 0:
                        intensity += light.intensity * pow((r_dot_v / (view.length * vec_r.length)), specular)

        return intensity

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

        point = origin + closest_t * direction
        normal = (point - closest_sphere.center).normalize()

        color_r = closest_sphere.color[0] * self.ComputeLighting(point, normal, -direction, sphere.specular)
        color_g = closest_sphere.color[1] * self.ComputeLighting(point, normal, -direction, sphere.specular)
        color_b = closest_sphere.color[2] * self.ComputeLighting(point, normal, -direction, sphere.specular)

        return (int(color_r), int(color_g), int(color_b))



    def run(self):
        image, pixels = self.initialize_image()

        for x in range(-self.width//2, self.width//2):
            for y in range(-self.height//2,self.height//2):
                direction = self.canvasToViewPort((x, y))
                color = self.traceRay(self.camera_position, direction, 1, inf)
                self.putPixel(pixels, x, y ,color)

        image.save("images/raytracying02.png")


class Light(object):
	"""
	Light class
	:type ltype: string
	:type intensity: float
	:type position: vector
	"""
	def __init__(self, ltype, intensity, position = None):
		self.ltype = ltype
		self.intensity = intensity
		self.position = position