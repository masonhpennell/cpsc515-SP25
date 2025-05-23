import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from A1_pencil_canvas import Canvas

def main():
    pygame.init()                                                                                   # initialize a pygame program
    glutInit()                                                                                      # initialize glut library    
    display = (500, 500)                                                                            # specify the screen size of the new program window
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)                                            # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC515: Pencils - Mason Pennell')                                      # set title of the program window

    # Set up the OpenGL viewport and projection
    glViewport(0, 0, display[0], display[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)                                                                    # Set up a simple orthographic projection
    glMatrixMode(GL_MODELVIEW)

    # Initialize the canvas
    width, height = 10, 10                                                                          # canvas' resolution (different from the pygame window's)
    pixel_size = 50                                                                                 # Size of each pixel on canvas to fill the window
    canvas = Canvas(width=width, height=height, pixel_size=pixel_size, canvas_type="color")   # TODO: Switch `canvas_type` here for Task 1.3, Task 4.2

    # Main loop
    running = True
    left_mouse_held = False 
    right_mouse_held = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                        # Left mouse button pressed
                left_mouse_held = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:                          # Left mouse button released
                left_mouse_held = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                right_mouse_held = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                right_mouse_held = False
        
        # Implement actions you'd like to do when the LEFT-button is held
        if left_mouse_held:
            mouse_x, mouse_y = pygame.mouse.get_pos()                                               # get mouse's pixel coordinates on the display
            #print(f"mouse clicks on display at pixel ({mouse_x}, {mouse_y})")                        
            
            canvas_x = mouse_x // pixel_size
            canvas_y = (display[1] - mouse_y) // pixel_size

            # uncomment the code below to verify your code
            #print(f"mouse clicks on canvas at pixel ({canvas_x}, {canvas_y})")                     
            
            if (canvas_x >= 0 and canvas_x < width) and (canvas_y >= 0 and canvas_y < height):
                canvas.data[canvas.posToIndex(canvas_y, canvas_x)] = (255, 0, 255, 255)


        # Implement actions you'd like to do when the RIGHT-button is held
        # TODO: Task 5.2: Draw a flower - write your code below
        if right_mouse_held:
            mouse_x, mouse_y = pygame.mouse.get_pos()                                               # get mouse's pixel coordinates on the display
            #print(f"mouse clicks on display at pixel ({mouse_x}, {mouse_y})")                        
            
            canvas_x = mouse_x // pixel_size
            canvas_y = (display[1] - mouse_y) // pixel_size

            canvas.draw_flower(canvas_y, canvas_x)

        glClear(GL_COLOR_BUFFER_BIT)                                                                # clear the color buffer
        
        canvas.render()                                                                             # Draw the image on the canvas

        glFlush()                                                                                   # ensure drawing is done befoer flipping double-buffer
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()