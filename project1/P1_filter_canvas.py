import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from collections import namedtuple
import numpy as np
import P1_filter_utils

# TODO: Task 2 - This function should return the gray value of a pixel 
#       by computing a weighted sum of its red, green, and blue components.
#       Recommend use the "luma method".
#       Return the gray value as np.uint8 
def rgbaToGray(color) -> np.uint8:
    gray = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    return np.uint8(gray)

# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size = 1):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Initialize the canvas data
        self.data = []
        self.initCanvas()

        # Status of filter application
        self.b_filtered = False

    def initCanvas(self):
        canvas_color = [0, 0, 0, 255] # black color
        self.data = np.array([canvas_color] * (self.width * self.height), dtype=np.uint8)

    def load_image(self, image_path):
        image = pygame.image.load(image_path)
        image_width, image_height = image.get_size() # get image dimensions

        # update teh canvas dimensions to match the image's aspect ratio
        self.width = image_width
        self.height = image_height

        # scale the image to fit the updated canvas dimensions
        image = pygame.transform.scale(image, (self.width, self.height)) 
        image_data = pygame.image.tobytes(image, "RGBA", True)  # Convert to raw pixel data
        self.data = np.frombuffer(image_data, dtype=np.uint8).reshape(self.width * self.height, 4).copy()

    # TODO: Task 1 - Implement Grayscale Filter:
    #       Iterate through every pixel in the image (i.e., self.data)
    #       Convert each pixel color into a grayscale value
    #       Update the image (self.data) with the grayscale value (np.uint8)
    def filterGray(self):
        for i in range(len(self.data)):
            gray_value = rgbaToGray(self.data[i])
            self.data[i] = [gray_value, gray_value, gray_value, gray_value]
    
    # TODO: Task 3 - Implement Invert filter:
    #       Iterate through every pixel in the image (i.e., self.data)
    #       Inverting each color channel by subtracting its value from the maximum value, i.e., 255.
    #       Update the image (self.data) with the inverted r,g,b values (np.uint8)
    def filterInvert(self):
        for i in range(len(self.data)):
            for j in range(3):
                self.data[i][j] = 255 - self.data[i][j]

    # TODO: Task 4 & Task 5 - Implement Brighten filter:
    #       Iterate through every pixel in the image
    #       Increase each color channel by 30%
    #       Update the image with the brightened r, g, b values (np.uint8)
    def filterBrighten(self):
        for i in range(len(self.data)):
            for j in range(3):
                brightness = 1.3 * self.data[i][j]
                if brightness > 255:
                    self.data[i][j] = 255
                else:
                    self.data[i][j] = brightness

    # TODO: Task 8 - Create an identity filter kernel and call convolve2D() from FilterUtils.py with it.
    #   If your kernel is correct, convolving with the identity kernel returns the original image.
    def filterIdentity(self, edge_pixel_method):
        # TODO: Create a 3x3 Identity kernel as a 1D list (row-major order)
        kernel = [0,0,0,0,1,0,0,0,0] 

        # Convolve the identity kernel to the image
        P1_filter_utils.convolve2D(data=self.data, width=self.width, height=self.height, kernel=kernel, edge_pixel_method=edge_pixel_method)


    # TODO: Task 9 - Create a Shift filter kernel
    """
    Goal: Applies a shift filter to self.data using 2D convolution.

    Args:
        shiftDir (str): "shiftLeft" or "shiftRight"
        num (int): Number of pixels to shift 
    """
    def filterShift(self, shiftDir, num, edge_pixel_method):
        # TODO: Create a shift kernel by calling `createShiftKernel()`
        kernel = P1_filter_utils.createShiftKernel(shiftDir=shiftDir, num=num)

        # TODO: Apply 2d convolution using the shift kernel
        P1_filter_utils.convolve2D(data=self.data, width=self.width, height=self.height, kernel=kernel, edge_pixel_method=edge_pixel_method)


    # TODO: Task 10 - Implement Edge Detection using Sobel operators (Separable kernels)
    def edgeDetection(self, sensitivity = 1, edge_pixel_method = 'Rep'):
        for i in range(len(self.data)):
            gray_value = rgbaToGray(self.data[i])
            self.data[i] = [gray_value, gray_value, gray_value, gray_value]

        # 2. Define Sobel kernels
        sobel_x = np.array([[-1,  0,  1],
                            [-2,  0,  2],
                            [-1,  0,  1]], dtype=np.float64)

        sobel_y = np.array([[-1, -2, -1],
                            [ 0,  0,  0],
                            [ 1,  2,  1]], dtype=np.float64)

        # 3. Convolve with the Sobel kernels
        gx = P1_filter_utils.convolve1d(self.data, sobel_x)
        gy = P1_filter_utils.convolve1d(self.data, sobel_y)

        # 4. Compute the gradient magnitude
        magnitude = np.sqrt(gx**2 + gy**2)

        # 5. Normalize/scale to [0, 255]
        #    We'll clip to ensure values are in range before converting to uint8
        magnitude = (magnitude / magnitude.max()) * 255.0
        magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
        
        final_data = []
        for pixel in range(self.data.shape[0]):
            g = magnitude[pixel]
            # Replicate the same gray value into R, G, B, and set alpha=255
            final_data.append([g, g, g, 255])
            
        self.data = magnitude

    # TODO: Task 13 - Implement Triangle Blur using a Triangle filter (separable kernels)
    def triangleBlur(self, kernel_size):
        # TODO: check if the input kernel size is value (i.e., odd number, >= 3)
        if kernel_size % 2 == 0 or kernel_size < 3:
            raise ValueError("kernel_size must be an odd number >= 3")

        # TODO: create a 1D triangle kernel based on kernel_size by calling `createTriangleFilter` from "P1_filter_utils.py"
        kernel = P1_filter_utils.createTriangleFilter(kernel_size)

        # TODO: Apply two 1D triangle kernels sequentially to the image, self.data, using `convolve1D()` from "P1_filter_utils.py"


        # TODO: Update self.data


        pass # you may delete this once you complete this function


    # TODO: Task 15 - Implement Gaussian Blur using a Gaussian filter (separable kernels)
    def GaussianBlur(self, blur_radius):
        # TODO: create a 1D triangle kernel based on blur radius by calling `createGaussianFilter` from "P1_filter_utils.py"


        # TODO: Apply two 1D Gaussian kernels sequentially to the image, self.data, using `convolve1D()` from "P1_filter_utils.py"


        # TODO: Update self.data


        pass # you may delete this once you complete this function