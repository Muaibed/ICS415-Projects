from PIL import Image
from vector3 import Vector3

class DrawingBase:
    def __init__(self, width, height, viewport_size, projection_plane_z, background_color):

        self.width = width
        self.height = height
        self.viewport_size = viewport_size
        self.projection_plane_z = projection_plane_z
        self.background_color = background_color


    def putPixel(self, pixels, x, y, color):
        """Draw a single pixel on the canvas."""

        x = self.width // 2 + x
        y = self.height // 2 - y

        if x < 0 or x >= self.width or y < 0  or y >= self.height:
            return

        r, g, b = int(color[0]), int(color[1]), int(color[2])

        pixels[x, y] = (r, g, b)


    def canvasToViewPort(self, p2d):
        """
            Converts 2D canvas coordinates to 3D viewport coordinates.
            :type p2d: tuple
        :rtype: Vector3
        """

        return Vector3(
            p2d[0] * self.viewport_size / self.width,
            p2d[1] * self.viewport_size / self.height,
            self.projection_plane_z,
        )

    def clear_image(self):
        """Clear logic to clear the image."""

        for x in range(self.width):
            for y in range(self.height):
                self.pixels[x, y] = self.background_color

    def run(self):
        """Run logic (to be overridden in subclass)."""
        pass


    def update(self):
        """Update logic (to be overridden in subclasses if needed)."""
        pass


    def initialize_image(self):
        image = Image.new("RGB", (self.width, self.height), self.background_color)
        pixels = image.load()
        return image, pixels
