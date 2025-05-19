import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

from P2_transformView_model import Camera, Scarecrow

width, height = 800, 600                                                    # width and height of the screen created

# drawing x, y, z axis in world space
def drawAxes():                                                             # draw x-axis and y-axis
    glLineWidth(3.0)                                                        # specify line size (1.0 default)
    glBegin(GL_LINES)                                                       # replace GL_LINES with GL_LINE_STRIP or GL_LINE_LOOP
    glColor3f(1.0, 0.0, 0.0)                                                # x-axis: red
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(100.0, 0.0, 0.0)                                             # v1
    glColor3f(0.0, 1.0, 0.0)                                                # y-axis: green
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 100.0, 0.0)                                             # v1
    glColor3f(0.0, 0.0, 1.0)                                                # z-axis: blue
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 0.0, 100.0)                                             # v1
    glEnd()

# drawing the ground
def drawGround():
    ground_vertices = [[-500, -12.6, -500],
                       [-500, -12.6, 500],
                       [500, -12.6, 500],
                       [500, -12.6, -500]]

    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_QUADS)
    for vertex in ground_vertices:
        glVertex3fv(vertex)
    glEnd()


def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC515: Transform & View - Mason Pennell')     # set title of the program window

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)                                             # set mode to projection transformation
    glLoadIdentity()                                                        # reset transf matrix to an identity
    gluPerspective(45, (width / height), 0.1, 1000.0)                       # specify perspective projection view volume

    glMatrixMode(GL_MODELVIEW)                                              # set mode to modelview (geometric + view transf)
    initmodelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)
    modelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)

    # initialize the Scarecrow: body dimensions and transformation parameters 
    scarecrow = Scarecrow(version="basic") # by default, draw the basic Scarecrow

    # initialize the camera: camera parameters 
    camera = Camera(view_mode="front") # default view mode is "front"

    # initialize the states of all the designated keys
    key_l_on = False        # if key 'L' is PRESSED - Switch to turn on/off arm/leg swinging animation for walk-in-place 
    key_r_on = False        # if key 'R' is PRESSED (not held) - Switch to turn on/off straightline/freeform walking

    while True:
        bResetModelMatrix = False
        glPushMatrix()
        glLoadIdentity()

        #--------START: pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    glRotatef(event.rel[1], 1, 0, 0)
                    glRotatef(event.rel[0], 0, 1, 0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:                 # Press key '0' to reset the view by resetting the current model-view matrix
                    bResetModelMatrix = True
                elif event.key == pygame.K_SPACE:           # Press the space bar to switch view modes: front/side/back/first_person..
                    camera.switch_view()                    # Task 7: Switch front/side/back views here
                    bResetModelMatrix = True
                elif event.key == pygame.K_u:               # Press key 'U' to switch between the basic and upgraded Scarecrow
                    if scarecrow.version == "basic":
                        scarecrow.version = "upgraded"
                    elif scarecrow.version == "upgraded":
                        scarecrow.version = "basic"
                elif event.key == pygame.K_l:               # Press key 'L' to turn on/off arm/leg swinging animation for walk-in-place
                    key_l_on = not key_l_on
                elif event.key == pygame.K_r:               # Press key 'R' to turn on/off straightline/freeform walking
                    key_r_on = not key_r_on
                elif event.key == pygame.K_ESCAPE:          # Press key 'ESC' to quit the program
                    pygame.quit()
                # add more key events and set key states here...

            

        
        #--------END: pygame.event.get()

        # Task 2: Update Scarecrow's head angle based on I, O key states
        if pygame.key.get_pressed()[pygame.K_i] & (scarecrow.head_angle < 85.0):
            scarecrow.head_angle += 1.0
        if pygame.key.get_pressed()[pygame.K_o] & (scarecrow.head_angle > -85.0):
            scarecrow.head_angle -= 1.0

        # Task 4: Update Scarecrow's limb motion parameters (arm_angle, leg_angle) for walk-in-place 
        #        based on L, R key states
        if key_l_on:
            # === Update arm angle ===
            scarecrow.arm_angle += scarecrow.arm_direction * scarecrow.swing_speed
            if abs(scarecrow.arm_angle) > 30:
                scarecrow.arm_angle = 30 * scarecrow.arm_direction
                scarecrow.arm_direction *= -1  # reverse swing direction

            # === Update leg angle ===
            scarecrow.leg_angle += scarecrow.leg_direction * scarecrow.swing_speed
            if abs(scarecrow.leg_angle) > 30:
                scarecrow.leg_angle = 30 * scarecrow.leg_direction
                scarecrow.leg_direction *= -1  # reverse swing direction            
        
        # Task 5 and Task 6: Update Scarecrow's walk motion parameters 
        #       (walk_angle, walk_direction, walk_vector) for straightline walk and freeform walk  
        #        based on LEFT and RIGHT key states
        #       Call `update_walk_vector()` after updating walk_angle
        if key_r_on:
            if not key_l_on:
                key_l_on = True
            # === Update walk angle ===
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                scarecrow.walk_angle += 4.0
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                scarecrow.walk_angle -= 4.0

            # === Update walk vector ===
            scarecrow.update_walk_vector()
        
        # TODO: Task 8: Update viewing parameters to transform (tilt, move forward/backward) the camera
        #       based on W/A/S/D/Q/E key states
        if pygame.key.get_pressed()[pygame.K_w]:
            camera.tilt_angle_vertical += 3
        if pygame.key.get_pressed()[pygame.K_s]:
            camera.tilt_angle_vertical -= 3
        if pygame.key.get_pressed()[pygame.K_a]:
            camera.tilt_angle_horizontal += 3
        if pygame.key.get_pressed()[pygame.K_d]:
            camera.tilt_angle_horizontal -= 3
        if pygame.key.get_pressed()[pygame.K_q]:
            camera.zoom_distance -= 0.5
        if pygame.key.get_pressed()[pygame.K_e]:
            camera.zoom_distance += 0.5

        # When '0' is tapped, reset the view 
        if (bResetModelMatrix):
            camera.zoom_distance = 0.0
            camera.tilt_angle_vertical = 0.0
            camera.tilt_angle_horizontal = 0.0
            glLoadIdentity()
            modelMatrix = initmodelMatrix
        glMultMatrixf(modelMatrix)
        modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        glLoadIdentity()
        
        # Task 7: Upate camera parameters: eye_position and look_at point
        new_eye_pos, new_lookat = camera.update_view()

        # Use updated camera parameters to update camera model
        gluLookAt(new_eye_pos[0], new_eye_pos[1], new_eye_pos[2], 
                  new_lookat[0], new_lookat[1],new_lookat[2],
                  camera.view_up[0], camera.view_up[1], camera.view_up[2])


        glMultMatrixf(modelMatrix)        

        # Task 1 & Task 3: Draw Scarecrow
        if scarecrow.version == "basic":        
            scarecrow.draw_Scarecrow()
        elif scarecrow.version == "upgraded":
            scarecrow.draw_Scarecrow_Upgrade()

        # draw other entities in the scene
        drawAxes()
        drawGround()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

main()