import pygame
import time
import os
import math
import math_helpers

from global_var import airplane_data
from global_var import input_commands

root_path = os.path.abspath(os.path.dirname(__file__))

pygame.init()
fonts = {
    'default': pygame.font.Font('freesansbold.ttf', 32),
    'helvetica': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 32),
    'dbxl': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 32),
    'dbxl_massive': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 60),

}

fonts['helvetica'].set_bold(True)

colours = {
    'white' : (255,255,255),
    'black' : (0  ,0  ,0  ),
    'bgd'   : (1  ,17 ,21 ),
    'pearl' : (247,255,228),
    'red'   : (255,102,95 ),

}

SCREEN_WIDTH = 1920
SREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SREEN_HEIGHT), pygame.RESIZABLE)
# Can set pygame.FULLSCREEN later if a quit button is made.

DELTA_TIME = 0.1
delta_time_record = time.time()
def GET_DELTA_TIME():
    global delta_time_record
    global DELTA_TIME
    current_time = time.time()
    DELTA_TIME = current_time - delta_time_record
    delta_time_record = current_time

def draw_text(text, font, colour, x, y):
    text = text.replace('-', '\u2212') # Unicodes of negative sign is not handled properly
    img = font.render(text, True, colour)
    screen.blit(img, (x, y))
                
def draw_text_centered(text, font, colour, x, y):
    text = text.replace('-', '\u2212')
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width()/2, y))

def draw_background_colour():
    pygame.draw.rect(screen, colours['bgd'], (0,0,1920,1080))

def draw_bad_screen():
    draw_background_colour()
    pygame.draw.line(screen, colours['red'], (102, 978), (709, 627), 4)
    pygame.draw.line(screen, colours['red'], (102, 1080-978), (709, 1080-627), 4)
    pygame.draw.line(screen, colours['red'], (1920-102, 978), (1920-709, 627), 4)
    pygame.draw.line(screen, colours['red'], (1920-102, 1080-978), (1920-709, 1080-627), 4)
    draw_text_centered( 'NO   ACTIVE', fonts['dbxl_massive'], colours['red'], 1920/2, 1080/2 - 70)
    draw_text_centered( 'CONNECTION', fonts['dbxl_massive'], colours['red'], 1920/2, 1080/2)

    pygame.display.update() # called once only

def draw_control_square(x, y):
    pygame.draw.line(screen, colours['pearl'], (x, y), (x+450, y), 4)
    pygame.draw.line(screen, colours['pearl'], (x, y), (x, y+450), 4)
    pygame.draw.line(screen, colours['pearl'], (x+450, y+450), (x+450, y), 4)
    pygame.draw.line(screen, colours['pearl'], (x+450, y+450), (x, y+450), 4)

def draw_control_handle():
    x_coord = math_helpers.lerp( (-1, 1) , (158, 158+450), input_commands['aileron'])
    y_coord = math_helpers.lerp( (-1, 1) , (269, 269+450), input_commands['elevator'])
    pygame.draw.circle(screen, colours['pearl'], (x_coord, y_coord), 20)

mouse_attached_to_ctrl = False

def attach_control(): # if x and y is in range, attach the mouse control
    global mouse_attached_to_ctrl
    mouse_attached_to_ctrl = True

def detach_control():
    global mouse_attached_to_ctrl
    mouse_attached_to_ctrl = False


elevator_damper = math_helpers.SmoothDamp()
aileron_damper = math_helpers.SmoothDamp()

def update_mouse_control():
    pitch_command = 0
    roll_command = 0

    if mouse_attached_to_ctrl:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        roll_command = math_helpers.lerp((158, 158+450), (-1 , 1), mouse_x)
        roll_command = math_helpers.clamper(roll_command, -1, 1)
        pitch_command = math_helpers.lerp((269, 269+450), (-1 , 1), mouse_y)
        pitch_command = math_helpers.clamper(pitch_command, -1, 1)

    input_commands['elevator'] = elevator_damper.smooth_damp(input_commands['elevator'], pitch_command, 0.07, 1000000, DELTA_TIME)
    input_commands['aileron'] = aileron_damper.smooth_damp(input_commands['aileron'], roll_command, 0.07, 1000000, DELTA_TIME)

## Below are the update loop and draw loop, they should always be at the bottom

def pygame_functions():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if math_helpers.within(mouse_x, 158, 158+450) and math_helpers.within(mouse_y, 269, 269+450) :
                attach_control()
        elif event.type == pygame.MOUSEBUTTONUP:
            detach_control()

    GET_DELTA_TIME() # should come before anything else
    update_mouse_control()

def draw_loop(): #loop
    draw_background_colour()
    draw_text_centered( 'YAW : ' + str(round(math.degrees(airplane_data['yaw']), 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2)
    draw_text_centered( 'ROLL : ' + str(round(math.degrees(airplane_data['roll']), 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*1)
    draw_text_centered( 'PITCH : ' + str(round(math.degrees(airplane_data['pitch']), 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*2)
    draw_text_centered( 'AOA : ' + str(round(math.degrees(airplane_data['aoa']), 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*3)

    draw_control_square(158, 269)
    draw_control_handle()
    pygame.display.update()