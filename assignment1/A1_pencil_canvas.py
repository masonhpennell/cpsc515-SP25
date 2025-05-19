import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Draw an image using OpenGL functions
def draw_image(pixels, pixel_size, width, height, show_grid = False):
    # Draw the pixels 
    for index, pixel in enumerate(pixels):
        row_idx = index // width
        col_idx = index % width
        glColor4ub(pixel[0], pixel[1], pixel[2], pixel[3])
        x = -1 + col_idx * pixel_size / 250.0  # Map to [-1, 1] in X
        y = -1 + row_idx * pixel_size / 250.0  # Map to [-1, 1] in Y
        glRectf(x, y, x + pixel_size / 250.0, y + pixel_size / 250.0)

    # Draw grid lines
    if show_grid == True:
        draw_gridline(width=width, height=height, pixel_size=pixel_size)

# Draw the grid lines on canvas (optional)
def draw_gridline(width, height, pixel_size):
    glColor3f(0.5, 0.5, 0.5)  # Grid line color (dark gray)
    for row_idx in range(height + 1):
        y = -1 + row_idx * pixel_size / 250.0
        glBegin(GL_LINES)
        glVertex2f(-1, y)
        glVertex2f(1, y)
        glEnd()
    for col_idx in range(width + 1):
        x = -1 + col_idx * pixel_size / 250.0
        glBegin(GL_LINES)
        glVertex2f(x, -1)
        glVertex2f(x, 1)
        glEnd()


# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size = 1, canvas_type="randomColor", show_grid = False):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.canvas_type = canvas_type
        self.show_grid = show_grid

        # Initialize the canvas data (list of RGBA namedtuples)
        self.data = []
        if canvas_type == "color":
            self.initColorCanvas()
        elif canvas_type == "grayscale":
            self.initGrayCanvas()
            self.show_grid = True
        elif canvas_type == "randomColor":
            self.data = [(r, g, b, 255) for r, g, b in ((np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)) for _ in range(width * height))]

    # Function to convert intensity (float, [0, 1]) to an integer [0 - 255]
    #   Return grayscale as an integer
    def floatToInt(self, intensity):
        return int(intensity * 255)

    # Function to convert (row, column) coordinates 
    #   into an index in a 1D array in row-majored order
    #   Return index
    def posToIndex(self, row, column):
        return row * self.width + column

    # Initialize the canvas data with grayscale (int, [0 - 255])
    def initGrayCanvas(self):
        intensity = 0.2 # TODO: Task 1.4: Modify this to see the difference in grayscale
        gray = self.floatToInt(intensity)
        self.data = [(gray, gray, gray, 255) for _ in range(self.width * self.height)]
        self.createHeart()

    # Initialize the canvas data with RGBA color data
    def initColorCanvas(self):
        constant_color = (0, 123, 123, 255) # (r,g,b,a)
        self.data = [constant_color for _ in range(self.width * self.height)]

    # Function to create a heart on a grayscale image
    #   Modify specific pixels in self.data by set the intensity to 1.0 so it draws a heart 
    def createHeart(self):
        heart_coords = [
            (2, 5), (3, 4), (3, 6), (4, 3), (4, 7), 
            (5, 2), (5, 8), (6, 2), (6, 8), (7, 3), 
            (7, 7), (7, 4), (7, 6), (6, 5)
        ]
        for y, x in heart_coords:
            self.data[self.posToIndex(y, x)] = (255, 255, 255, 255)

    # Function to draw a flower centered onthe input position
    def draw_flower(self, y, x):
        self.data[self.posToIndex(y, x)] = (255, 255, 255, 255)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.height and 0 <= nx < self.width:
                self.data[self.posToIndex(ny, nx)] = (255, 0, 255, 255)


    # Function to render the image on the canvas using OpenGL
    def render(self):
        draw_image(pixels=self.data, pixel_size=self.pixel_size, width=self.width, height=self.height, show_grid=self.show_grid)
        

