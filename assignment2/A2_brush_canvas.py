import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size=1):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Initialize the canvas data
        self.data = []
        self.initCanvas()

        # brush related variables
        self.brush_radius = 1
        self.brush_size = 3                 # mask's height or width (equal); TODO: update its value based on bru
        self.brush_color = (0, 0, 0, 255)   # black brush by default
        self.brush_mask = []                # use a 1D array of brush_size * brush_size to store mask data

    def initCanvas(self):
        canvas_color = (255, 255, 255, 255) # background color
        self.data = np.array([canvas_color] * (self.width * self.height), dtype=np.uint8)

    def initBrush(self, brush_radius, brush_color, brush_type):
        self.brush_radius = brush_radius
        self.brush_color = brush_color
        
        # TODO: Calculate self.brush_size based on brush_radius
        self.brush_size = 2 * self.brush_radius + 1

        # Initialize a mask of different distributions based on brush type
        if brush_type == "constant":
            self.brush_mask = self.createConstantBrushMask()
        elif brush_type == "linear":
            self.brush_mask = self.createLinearBrushMask()
        elif brush_type == "quadratic":
            self.brush_mask = self.createQuadraticBrushMask()
        else:
            # Default to constant if not recognized
            self.brush_mask = self.createConstantBrushMask()

    # TODO: Create a constant brush mask of brush_size x brush_size, 
    #       Populate the mask with 1s where the distance is within the radius and 0s elsewhere 
    #       Return the mask as a 1D array (float)
    def createConstantBrushMask(self):
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        center = self.brush_radius

        # TODO: iterate and fill up the mask
        for j in range(self.brush_size):
            for i in range(self.brush_size):
                dx = i - center
                dy = j - center
                dist = np.sqrt(dx*dx + dy*dy)
                if dist <= self.brush_radius:
                    mask[j, i] = 1.0

        # TODO: flatten the mask into a 1D array
        return mask.flatten()
    
    # TODO: Create a linear brush mask of brush_size x brush_size,
    #       Linearly descrease the value at each pixel as moving away from the center (1.0)
    #           and the values at the edge is 0.
    #       Return the mask as a 1D array (float)
    def createLinearBrushMask(self):
        # initialize the mask as an empty 2D array of brush_size x brush_size
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        center = self.brush_radius

        # TODO: iterate and fill up the mask based on f(d)
        for j in range(self.brush_size):
            for i in range(self.brush_size):
                dx = i - center
                dy = j - center
                dist = np.sqrt(dx*dx + dy*dy)
                if dist <= self.brush_radius:
                    value = 1.0 - (dist / self.brush_radius)
                    mask[j, i] = value

        # TODO: flatten the mask into a 1D array
        return mask.flatten()

    # TODO: Create a quadratic brush mask of brush_size x brush_size,
    #           value at each pixel: f(d) = A * d^2 + B * d + C
    #             (You may first calculate A, B, and C based on the given 3 conditions)
    #       Return the mask as a 1D array (float)
    def createQuadraticBrushMask(self):
        # initialize the mask as an empty 2D array of brush_size x brush_size
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        center = self.brush_radius
        r = float(self.brush_radius)

        # TODO: list the parameters A, B, C for f(d)
        A = 1.0 / (r*r)
        B = -2.0 / r
        C = 1.0

        # TODO: iterate and fill up the mask based on f(d)
        for j in range(self.brush_size):
            for i in range(self.brush_size):
                dx = i - center
                dy = j - center
                dist = np.sqrt(dx*dx + dy*dy)

                if dist <= r:
                    val = A*(dist**2) + B*dist + C
                    # clamp the value
                    if val < 0.0:
                        val = 0.0
                    elif val > 1.0:
                        val = 1.0
                    mask[j, i] = val

        # TODO: flatten the mask into a 1D array
        return mask.flatten()

    # TODO: Apply brush_mask, centered at (canvas_x, canvas_y), to the canvas 
    #           by iterating over the mask and apply the brush color to the canvas
    #       For each pixel color, mixing colors of brush and canvas based on the values (weights) stored in the mask
    #       Make sure you update self.data with the mixed color at the end. 
    #       Hint: When mixing colors, convert each channel from uint8 [0, 255] to float [0.0, 1.0] first
    #        and remember to convert it back to np.uint8 before updating self.data
    def apply_brush(self, canvas_x, canvas_y):
        r = self.brush_radius
        size = self.brush_size
        mask = self.brush_mask

        # Convert brush color to floats [0..1]
        brush_r = self.brush_color[0] / 255.0
        brush_g = self.brush_color[1] / 255.0
        brush_b = self.brush_color[2] / 255.0
        brush_a = self.brush_color[3] / 255.0  # if used

        for j in range(size):
            for i in range(size):
                px = canvas_x + (i - r)
                py = canvas_y + (j - r)

                if (0 <= px < self.width) and (0 <= py < self.height):
                    mask_index = j * size + i
                    alpha = mask[mask_index]

                    if alpha > 0.0:
                        data_index = py * self.width + px

                        old_color = self.data[data_index] / 255.0
                        new_color = alpha * np.array([brush_r, brush_g, brush_b, brush_a]) + (1 - alpha) * old_color
                        self.data[data_index] = (new_color * 255).astype(np.uint8)
