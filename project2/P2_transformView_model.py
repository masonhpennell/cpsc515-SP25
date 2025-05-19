import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

#TODO: Complete the function for rotating the input `vector` around `rot_axis` by `angle_degrees`
#      Construct a 3x3 rotation matrix (no need Homogeneous) and multiply it with the input vector
#      rot_axis: "X", "Y", or "Z"
#      Return the rotated vector.
def rotate_vector(vector, angle_degrees, rot_axis):
    # TODO: convert angle degrees to radians
    radians = np.radians(angle_degrees)

    # TODO: construct a 3x3 rotation matrix using np.array based on angle and rotation axis
    if rot_axis == "Y":
        R = np.array([[np.cos(radians), 0, np.sin(radians)],
                    [0, 1, 0],
                    [-np.sin(radians), 0, np.cos(radians)]])
        rotate_vector = np.dot(R, vector)
    elif rot_axis == "X":
        R = np.array([[1, 0, 0],
                    [0, np.cos(radians), -np.sin(radians)],
                    [0, np.sin(radians), np.cos(radians)]])
        rotate_vector = np.dot(R, vector)
    elif rot_axis == "Z":
        R = np.array([[np.cos(radians), np.sin(radians), 0],
                    [-np.sin(radians), np.cos(radians), 0],
                    [0, 0, 1]])
        rotate_vector = np.dot(R, vector)

    # TODO: rotate the input vector by multiplying with the matrix using np.dot()
    return rotate_vector

class Camera:
    def __init__(self, view_mode = "front"):
        self.view_mode = view_mode
        # camera parameters
        self.eye_pos = np.array([0.0, 10.0, 50.0]) # initial setting for the front view
        self.look_at = np.array([0.0, 0.0, -1.0])
        self.view_up = np.array([0.0, 1.0, 0.0])

        # viewing parameters adjustable by keyboard input
        self.tilt_angle_horizontal = 0.0 # the angle (degrees) to rotate the gaze vector to the left or right
        self.tilt_angle_vertical = 0.0 # the angle (degrees) to rotate the gaze vector upward or downward
        self.zoom_distance = 0.0 # camera forward/backward distance along the gaze vector, positive or negative

    # Task 7: Switch between 3 standard view modes: front, side, and back
    #               For each view mode, pre-define camera parameters here 
    def switch_view(self):
        # Switch the current view_mode to the next in the cycle: 
        #   front -> side -> back -> (first_person) -> front -> side -> ...
        if self.view_mode == "front":
            self.view_mode = "side"
        elif self.view_mode == "side":
            self.view_mode = "back"
        elif self.view_mode == "back":
            self.view_mode = "front"
        
        # Front view
        if self.view_mode == "front":
            self.eye_pos = np.array([0.0, 10.0, 50.0]) 
            self.look_at = np.array([0.0, 0.0, -1.0])
            self.view_up = np.array([0.0, 1.0, 0.0])

        # Side view
        elif self.view_mode == "side":
            self.eye_pos = np.array([50.0, 10.0, 0.0]) 
            self.look_at = np.array([-1.0, 0.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])

        # Back view
        elif self.view_mode == "back":
            self.eye_pos = np.array([45.0, 33.0, -70.0]) 
            self.look_at = np.array([16.0, 0.0, 8.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        
    # TODO: Task 8: Update camera parameters (eye_pos and look_at) based on the new 
    #               tilt_angle_horizontal, tilt_angle_vertical, and zoom_distance updated by key input (A, D, W, S, Q, E)
    def update_view(self):
        # calculate the current gaze vector
        gaze_vector = self.look_at - self.eye_pos

        ## calculate new look-at point
        # TODO: tilt horizontally: rotate the gaze vector around SOME axis by tilt_angle_horizontal
        gaze_vector = rotate_vector(gaze_vector, self.tilt_angle_horizontal, "Y")

        # TODO: tilt vertically: rotate the gaze vector around SOME axis by title-angle_vertical
        if self.view_mode == "front":
            gaze_vector = rotate_vector(gaze_vector, self.tilt_angle_vertical, "X")
        elif self.view_mode == "side":
            gaze_vector = rotate_vector(gaze_vector, self.tilt_angle_vertical, "Z")
        
        # TODO: calculate the current look-at point
        new_lookat = self.eye_pos + gaze_vector
        
        ## calculate new eye position by moving the camera along the gaze vector by zoom_distance
        gaze_vector_unit = gaze_vector / np.linalg.norm(gaze_vector)

        new_eye_pos = self.eye_pos + gaze_vector_unit * self.zoom_distance
        new_lookat = new_lookat + gaze_vector_unit * self.zoom_distance

        # return new eye position and look-at point
        return new_eye_pos, new_lookat


class Scarecrow:
    def __init__(self, version = "basic"):
        self.version = version 
        # Scarecrow body part dimensions, for both "basic" and "upgraded"
        self.head_sphere = 2.5 # radius
        self.nose_cylinder = [0.3, 0.0, 1.8] # base radius, top radius, height
        self.torso_cylinder = [2.5, 2.5, 10.0] # base radius, top radius, height
        # basic scarecrow
        self.leg_cylinder = [1.0, 1.0, 12.0] # base radius, top radius, height
        self.arm_cylinder = [1.0, 1.0, 10.0] # base radius, top radius, height
        # upgraded scarecrow
        self.upper_lower_leg_cylinder = [1.0, 1.0, 6.0] # base radius, top radius, height
        self.upper_lower_arm_cylinder = [1.0, 1.0, 5.0] # base radius, top radius, height
        self.joint_leg_sphere = 1.0 # radius
        self.joint_arm_sphere = 1.0 # radius
        self.hand_sphere = 1.1 # radius
        self.foot_cube = 1.5 # cube's side length
        
        # head/limb motion parameters (Task 4: Walk-in-place)
        self.head_angle = 0.0 # head rotation angle used in Task 2
        self.arm_angle = 0.0 # arm rotation angle, with a range [-30,30], used for walk-in-place and freeform walking animations
        self.arm_direction = 1 # 1 for swinging backward (CCW), -1 for forward (CW)
        self.leg_angle = 0.0 # leg rotation angle, with a range [-30,30], used for walk-in-place and freeform walking animations
        self.leg_direction = 1 # 1 for swinging backward (CCW), -1 for forward (CW)
        self.swing_speed = 0.5 # arm and leg swinging speed, delta angle to increase/decrease arm_angle and leg_angle each iteration
        
        # walk motion parameters (Task 5: Straightline and Task 6: Freeform)
        self.walk_direction = np.array([0.0, 0.0, 1.0]) # unit vector; initially aligned with z-axis
        self.walk_angle = 0.0 # the angle (degrees) between the walk_direction and the z-axis [0, 0, 1]
        self.walk_speed = 0.27*self.swing_speed # straigntline and freeform walking speed
        self.walk_vector = np.array([0.0, 0.0, 0.0]) # = walk_speed * walk_direction; updated for every iteration to translate the scarecrow during walking (TODO)

    # Task 6 Use: Update Scarecrow's walk_direction and walk_vector based on walk_angle changed by key input
    def update_walk_vector(self):
        # self.walk_vector = rotate_vector(self.walk_vector, self.walk_angle, "Y")
        self.walk_direction[0] = np.sin(np.radians(self.walk_angle)) # x-axis
        self.walk_direction[2] = np.cos(np.radians(self.walk_angle)) # z-axis
        self.walk_vector += self.walk_speed * self.walk_direction

    # Task 1 and Task 2
    # 1. Create a Basic Scarecrow
    # 2. Rotate its head and nose based on transformation parameters updated by key input
    # NOTE: Body parts needed for the basic scarcrow have been created already
    #       you will need to transform them to approporate positions
    def draw_Scarecrow(self): 
        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        # Head (sphere: radius=2.5)
        glPushMatrix()
        glRotatef(self.head_angle, 0, 1, 0) # rotate the head
        glTranslatef(0, 12.5, 0) # move to the top of the torso
        glColor3f(0.0, 1.0, 0.0)
        gluSphere(quadratic, self.head_sphere, 32, 32)
        glPopMatrix()

        # Nose (cylinder: base-radius=0.3, top-radius=0, length=1.8)
        glPushMatrix()
        glRotatef(self.head_angle, 0, 1, 0) # rotate the head
        glTranslatef(0, 12.5, self.head_sphere)
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, *self.nose_cylinder, 32, 32)
        glPopMatrix()

        # Torso (cylinder: radius=2.5, length=10)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 1.0, 0.0)
        gluCylinder(quadratic, *self.torso_cylinder, 32, 32)
        glPopMatrix()
    
        # Right Leg (cylinders: radius=1.0, length=12)
        glPushMatrix()
        glTranslatef(-1.2, 0, 0) # move to the bottom of the torso
        glRotatef(90, 1, 0, 0) # rotate legs
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, *self.leg_cylinder, 32, 32)
        glPopMatrix()

        # Left Leg (cylinders: radius=1.0, length=12)
        glPushMatrix()
        glTranslatef(1.2, 0, 0) # move to the bottom of the torso
        glRotatef(90, 1, 0, 0) # rotate legs
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, *self.leg_cylinder, 32, 32)
        glPopMatrix()

        # right Arm (cylinders: radius=1.0, length=10)]
        glPushMatrix()
        glTranslatef(-self.torso_cylinder[0], 9, 0) # move to the bottom of the torso
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(quadratic, *self.arm_cylinder, 32, 32)
        glPopMatrix()

        # left Arm (cylinders: radius=1.0, length=10)
        glPushMatrix()
        glTranslatef(self.torso_cylinder[0], 9, 0) # move to the bottom of the torso
        glRotatef(90, 0, 1, 0)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(quadratic, *self.arm_cylinder, 32, 32)
        glPopMatrix()


    # Task 3: Upgrade the Scarecrow with more joints 
    #       Task 4: Walk-in-place animation
    #       Task 5: Walk-in-straightline animation
    #       Task 6: Freeform walk animation with keyboard input
    # NOTE: Create a new Scarecrow with more joints, hands, and feet according to scene graph
    #       Use the given body part dimensions defined within __init__()
    #       Transform them in a cumulative manner 
    def draw_Scarecrow_Upgrade(self): 
        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        glPushMatrix() # DO NOT DELETE THIS
        
        # move whole scarecrow
        glTranslatef(*self.walk_vector)
        glRotatef(self.walk_angle, 0, 1, 0)

        # Torso
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 1.0, 0.0)
        gluCylinder(quadratic, *self.torso_cylinder, 32, 32)
        
        # === Arms ===
        for side in [-1, 1]:  # -1 = left, 1 = right
            glPushMatrix()
            glTranslatef(self.torso_cylinder[0] * side, 0, 10)  # Move to shoulder joint
            glRotatef(-15 * side, 0, 1, 0)
            glRotatef(180 + self.arm_angle * side, 1, 0, 0) # rotate arms
            glColor3f(0.0, 0.0, 1.0)
            gluCylinder(quadratic, *self.upper_lower_arm_cylinder, 32, 32)

            # Move to elbow and draw joint
            glTranslatef(0, 0, 5)
            gluSphere(quadratic, self.joint_arm_sphere, 32, 32)

            # Draw lower arm
            if self.arm_angle * side < 0:
                glRotatef(self.arm_angle * side * 2, 1, 0, 0) # rotate lower arm
            gluCylinder(quadratic, *self.upper_lower_arm_cylinder, 32, 32)

            # Move to wrist and draw hand
            glTranslatef(0, 0, 5)
            glColor3f(0.0, 1.0, 0.0)
            gluSphere(quadratic, self.hand_sphere, 32, 32)
            glPopMatrix()

        # === Legs ===
        for side in [-1, 1]:  # -1 = left, 1 = right
            glPushMatrix()
            glRotatef(180 - self.leg_angle * side, 1, 0, 0)  # rotate legs
            glTranslatef(1.2 * side, 0, 0)  # hip position
            glColor3f(1.0, 0.0, 0.0)
            gluCylinder(quadratic, *self.upper_lower_leg_cylinder, 32, 32)  # upper leg

            # Move to knee and draw joint
            glTranslatef(0, 0, 6)
            gluSphere(quadratic, self.joint_leg_sphere, 32, 32)

            # Draw lower leg
            if self.leg_angle * side < 0:
                glRotatef(-self.leg_angle * side, 1, 0, 0) # rotate lower leg
            gluCylinder(quadratic, *self.upper_lower_leg_cylinder, 32, 32)  

            # Draw feet
            glTranslatef(0, 1, 6)
            glColor3f(1.0, 0.5, 0.0)
            glScalef(1, 1.8, 0.8)  # squish the depth
            glutSolidCube(self.foot_cube)  # foot
            glPopMatrix()        
        
        # Head
        glRotatef(self.head_angle, 0, 0, 1) # rotate the head
        glTranslatef(0, 0, 12.5) # move to the top of the torso
        glColor3f(0.0, 1.0, 0.0)
        gluSphere(quadratic, self.head_sphere, 32, 32)
        
        # Nose
        glTranslatef(0, -self.head_sphere, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, *self.nose_cylinder, 32, 32)
        
        glPopMatrix() # DO NOT DELETE THIS

