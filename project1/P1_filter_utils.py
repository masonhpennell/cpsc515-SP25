import numpy as np
import math

#============ TODO: Task 7 - Implement Different Methdos for Out-Of-Bounds Pixels
'''
README: getPixelRepeated(), getPixelReflected(), and getPixelWrapped() all
have the same input arguments:
- data:     the image's data
- width:    the image's width
- height:   the image's height
- x:        the x coordinate of the pixel you are attempting to access
- y:        the y coordinate of the pixel you are attempting to access
'''

# Repeats the pixel on the edge of the image such that A,B,C,D looks like ...A,A,A,B,C,D,D,D...
# Return the pixel at (new_x, new_y)
def getPixelRepeated(data, width, height, x, y):
    new_x = 0 if x < 0 else min(x, width - 1)
    new_y = 0 if y < 0 else min(y, height - 1)
    return data[width * new_y + new_x]

# TODO: Reflect pixel values about the edge of the image such that A,B,C,D looks like ...C,B,A,B,C,D,C,B...
# Return the pixel at (new_x, new_y)
def getPixelReflected(data, width, height, x, y):
    new_x = abs(x) if x < 0 else (2 * width - x - 2 if x >= width else x)
    new_y = abs(y) if y < 0 else (2 * height - y - 2 if y >= height else y)
    return data[width * new_y + new_x]

# TODO: Wrap the image such that A,B,C,D looks like ...C,D,A,B,C,D,A,B
# Return the pixel at (new_x, new_y)
def getPixelWrapped(data, width, height, x, y):
    new_x = x % width
    new_y = y % height
    return data[width * new_y + new_x]

#============ END Task 7

# TODO: Task 6 - Implement Convolve2D
'''
Switch between different edge-pixel handling methods:
`edge_pixel_method`:
- 'Rep': use `getPixelRepeated` method
- 'Ref': use `getPixelReflected` method
- 'Wra': use `getPixelWrapped` method
'''
def convolve2D(data, width, height, kernel, edge_pixel_method):
    # TODO: Initialize a 1D numpy array (np.uint8), called 'result', to temporarily store your output image data
    result = np.zeros_like(data, dtype=np.uint8)

    # TODO: Obtain the side size of the input kernel (square, odd number)
    kernel_size = int(math.sqrt(len(kernel)))

    # TODO: Obtain the padding size based on kernel size
    padding = kernel_size // 2

    # TODO: Rotate the kernel by 180 - think of a clever way to flip the kernel through indexing
    kernel = kernel[::-1]

    for row in range(height):
        for col in range(width):
            print(f"\r--- row: {row}, column: {col}", end='', flush=True)
            index = width * row + col # row-major order

            # TODO: Initialize redAcc, greenAcc, and blueAcc to store accumulated color channels, float
            redAcc, greenAcc, blueAcc = 0.0, 0.0, 0.0

            # Iterate over the kernel using its dimensions
            for k_row in range(kernel_size // 1):
                for k_col in range(kernel_size // 1):
                    # TODO: get 'weight' from the kernel at the current position (k_row, k_col)
                    weight = kernel[k_row * kernel_size + k_col]

                    # TODO: Compute the corresponding pixel coordinates (img_x,img_y) based on the current kernel element and padding
                    img_x = col + (k_col - padding)
                    img_y = row + (k_row - padding)

                    # TODO: Get the pixel at (img_x, img_y) by handling out-of-bounding pixels - swtich between 'Rep', 'Rep', 'Wra' here
                    if edge_pixel_method == 'Rep':
                        pixel = getPixelRepeated(data, width, height, img_x, img_y)
                    elif edge_pixel_method == 'Ref':
                        pixel = getPixelReflected(data, width, height, img_x, img_y)
                    elif edge_pixel_method == 'Wra':
                        pixel = getPixelWrapped(data, width, height, img_x, img_y)
            
                    # TODO: Accumulate `weight * pixel` for each channel in redAcc, greeAcc, and blueAcc accordingly
                    redAcc += weight * pixel[0]
                    greenAcc += weight * pixel[1]
                    blueAcc += weight * pixel[2]
        
            # TODO: Update `result`` with the new RGBA pixel value created from redAcc, greenAcc, and blueAcc
            result[index] = (int(redAcc), int(greenAcc), int(blueAcc), 255)
    
    # TODO: Copy the RGBA data from `result` to `data`
    data[:] = result[:]

# TODO: Task 9 - Create a shift kerenl
'''
Goal: Create a 2D kernel that shifts an image `num` pixels in the given direction `shiftDir`

Args:
    shiftDir (str): "shiftLeft" or "shiftRight"
    num (int): Number of pixels to shift

Returns:
    shift kernel as a 1D list (row-major)
'''
def createShiftKernel(shiftDir, num):
    if shiftDir not in ["shiftLeft", "shiftRight"]:
        raise ValueError("shiftDir must be 'shiftLeft' or 'shiftRight'")

    # TODO: Determine kernel size (odd-numbered)
    kernel_size = 2 * num + 1

    # TODO: Initialize kernel as a 1D array with zeros
    kernel = [0] * kernel_size * kernel_size

    # TODO: Set `1` at a proper position based on `shiftDir` and `num`
    if shiftDir == "shiftLeft":
        kernel[num * kernel_size] = 1
    elif shiftDir == "shiftRight":
        kernel[num * (kernel_size + 2)] = 1

    # TODO: Return the kernel 
    return kernel

# TODO: Task 11 - Implement Convolve1D with the row and column kernels from 
#                   a separable 2D kernel on the input image (i.e., `data`)
def convolve1d(image, kernel):
    """
    A simple 2D convolution (with zero-padding) between a grayscale image
    and a given kernel. Returns an output array of the same size as `image`.
    """
    # image shape: (H, W)
    # kernel shape: (kH, kW)
    # We'll do zero-padding so output has same (H, W) size.

    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape
    
    # Calculate padding
    pad_h = kernel_height // 2
    pad_w = kernel_width // 2
    
    # Pad the image with zeros on all sides
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant', constant_values=0)
    
    # Prepare an output array
    output = np.zeros_like(image, dtype=np.float64)
    
    # Convolve
    for i in range(image_height):
        for j in range(image_width):
            # Region of interest in padded image
            region = padded[i:i+kernel_height, j:j+kernel_width]
            # Element-wise multiplication and sum
            output[i, j] = np.sum(region * kernel)
    
    return output

# TODO: Task 12 - Create a 1D triangle kernel based on any input kernel size (odd number)
def createTriangleFilter(kernel_size):
    # TODO: initial a 1D array as the kernel

    # TODO: determine the formula for deriving the weights within the kernel

    # TODO: iterate and fill up the kernel with weights based on the formula in a loop

    # TODO: return the kernel

    pass # you may delete this once you complete this function 


# TODO: Task 14 - Create a 1D Gaussian kernel based on an arbitrary input `blur radius``
def createGaussianFilter(blur_radius):
    # TODO: compute standard deviation and kernel size based on blur_radius, list your formulas here


    # TODO: initial a 1D array as the kernel with kernel size



    # TODO: iterate and fill up the kernel with weights in a loop based on the Gaussian function


    # TODO: return the kernel


    pass # you may delete this once you complete this function 