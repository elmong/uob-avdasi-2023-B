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
    'dbxl_title': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 20),
    'dbxl_massive': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 60),

}

fonts['helvetica'].set_bold(True)

colours = {
    'white' : (255,255,255),
    'black' : (0  ,0  ,0  ),
    'bgd'   : (1  ,17 ,21 ),
    'pearl' : (247,255,228),
    'red'   : (255,102,95 ),
    'light_blue'   : (154,255,255 ),
    'green_blue'   : (0  ,201,186 ),
    'dark_blue'   : (0  ,98,114 ),
}

SCREEN_WIDTH = 1920
SREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SREEN_HEIGHT), pygame.RESIZABLE)
# Can set pygame.FULLSCREEN later if a quit button is made.

cursor_ctrl_box_x = 939
cursor_ctrl_box_y = 540
cursor_ctrl_side_length = 244
cursor_ctrl_boost_factor = 1.05 # cursor_ctrl_boost_factor for aesthetics, so that the cross don't stick to the edge

class Button:
    instances = []
    def __init__(self, x, y, width, height, colour, text_row1, text_row2=None, callback = None):
        Button.instances.append(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.text_row1 = text_row1
        self.text_row2 = text_row2
        self.is_hovered = False
        self.callback = callback
    
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, self.colour, 3)
        if self.text_row2:
            draw_text_centered(self.text_row1, fonts['dbxl_title'], self.colour, self.x + self.width/2, self.y + self.height/2 - 20)
            draw_text_centered(self.text_row2, fonts['dbxl_title'], self.colour, self.x + self.width/2, self.y + self.height/2)
        else:
            draw_text_centered(self.text_row1, fonts['dbxl_title'], self.colour, self.x + self.width/2, self.y + self.height/2 - 10)
    
    def check_hot(self, mouse_x, mouse_y):
        self.is_hovered = (
            self.x < mouse_x < self.x + self.width and
            self.y < mouse_y < self.y + self.height
        )
        return self.is_hovered
    
    def actuate(self):
        if not self.callback:
            print("WARNING! Button " + str(self.text_row1) + " has no callback!")
            return
        self.callback()

class ToggleButton(Button):
    def __init__(self, x, y, width, height, colour, text_row1, text_row2=None, callback = None):
        super().__init__( x, y, width, height, colour, text_row1, text_row2, callback)
        self.state = False
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, self.colour, 3)
        text_colour = colours['pearl'] # essentially overriding whatever colour argument. All toggle buttons should be of same colour
        if self.state:
            text_colour = colours['dark_blue']
            pygame.draw.rect(screen, colours['green_blue'], (self.x + 3 ,self.y + 3, self.width - 5, self.height - 5))
    
        if self.text_row2:
            draw_text_centered(self.text_row1, fonts['dbxl_title'], text_colour, self.x + self.width/2, self.y + self.height/2 - 20)
            draw_text_centered(self.text_row2, fonts['dbxl_title'], text_colour, self.x + self.width/2, self.y + self.height/2)
        else:
            draw_text_centered(self.text_row1, fonts['dbxl_title'], text_colour, self.x + self.width/2, self.y + self.height/2 - 10)

    def actuate(self):
        self.state = not self.state # change the status of the button
        super().actuate() # at the same time toggle a function

############ The land of button creation
quit_button = Button(1704, 0, 122, 64, colours['red'], "QUIT", callback=lambda: quit())
pid_tuning_button = Button(865, 0, 1920-865*2, 64, colours['pearl'], "PID TUNING")
button_1 = Button(865 - 208 * 1, 0, 1920-865*2, 64, colours['pearl'], "BUTTON 1")
button_2 = Button(865 - 208 * 2, 0, 1920-865*2, 64, colours['pearl'], "BUTTON 2")
button_4 = Button(865 + 208 * 1, 0, 1920-865*2, 64, colours['pearl'], "BUTTON 4")
button_5 = ToggleButton(155, 910, 120, 68, colours['pearl'], "FLT", "DIR", callback = lambda: input_commands.update(ap_on=not input_commands['ap_on'])) # This code is so dirty I hate it

############  I love OOP

DELTA_TIME = 0.1
delta_time_record = time.time()
def GET_DELTA_TIME():
    global delta_time_record
    global DELTA_TIME
    current_time = time.time()
    DELTA_TIME = current_time - delta_time_record
    delta_time_record = current_time

def draw_line(coord_1, coord_2, width, colour):
    pygame.draw.line(screen, colour, coord_1, coord_2, width)

def draw_text(text, font, colour, x, y):
    text = text.replace('-', '\u2212') # Unicodes of negative sign is not handled properly
    img = font.render(text, True, colour)
    screen.blit(img, (x, y))
                
def draw_text_centered(text, font, colour, x, y):
    text = text.replace('-', '\u2212')
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width()/2, y))

def draw_rectangle(x, y, width, height, colour, line_width):
    pygame.draw.line(screen, colour, (x, y), (x+width, y), line_width)
    pygame.draw.line(screen, colour, (x, y+height), (x+width, y+height), line_width)
    pygame.draw.line(screen, colour, (x, y), (x, y+height), line_width)
    pygame.draw.line(screen, colour, (x+width, y), (x+width, y+height), line_width)

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

def draw_control_square():
    draw_rectangle(cursor_ctrl_box_x, cursor_ctrl_box_y, cursor_ctrl_side_length, cursor_ctrl_side_length, colours['pearl'], 2)

def draw_control_handle():
    x = math_helpers.lerp( (-1, 1) , (cursor_ctrl_box_x, cursor_ctrl_box_x+cursor_ctrl_side_length), input_commands['aileron']/cursor_ctrl_boost_factor)
    y = math_helpers.lerp( (-1, 1) , (cursor_ctrl_box_y, cursor_ctrl_box_y+cursor_ctrl_side_length), input_commands['elevator']/cursor_ctrl_boost_factor)
    offsets = 3
    line_length = 14
    pygame.draw.line(screen, colours['pearl'], (x + offsets, y + offsets) , (x + offsets + line_length, y + offsets), 3)
    pygame.draw.line(screen, colours['pearl'], (x + offsets, y + offsets) , (x + offsets , y + offsets + line_length), 3)

    pygame.draw.line(screen, colours['pearl'], (x - offsets, y + offsets) , (x - offsets - line_length, y + offsets), 3)
    pygame.draw.line(screen, colours['pearl'], (x - offsets, y + offsets) , (x - offsets , y + offsets + line_length), 3)

    pygame.draw.line(screen, colours['pearl'], (x + offsets, y - offsets) , (x + offsets + line_length, y - offsets), 3)
    pygame.draw.line(screen, colours['pearl'], (x + offsets, y - offsets) , (x + offsets , y - offsets - line_length), 3)

    pygame.draw.line(screen, colours['pearl'], (x - offsets, y - offsets) , (x - offsets - line_length, y - offsets), 3)
    pygame.draw.line(screen, colours['pearl'], (x - offsets, y - offsets) , (x - offsets , y - offsets - line_length), 3)

def draw_adi():
    draw_rectangle(220, 319, 464, 464, colours['light_blue'], 3)

def draw_menu():
    draw_line((0, 112), (1920, 112), 3, colours['pearl'])

mouse_attached_to_ctrl = False
elevator_damper = math_helpers.SmoothDamp() #init the instances
aileron_damper = math_helpers.SmoothDamp()

def attach_control(): # if x and y is in range, attach the mouse control
    global mouse_attached_to_ctrl
    mouse_attached_to_ctrl = True

def detach_control():
    global mouse_attached_to_ctrl
    mouse_attached_to_ctrl = False

def update_mouse_control():
    pitch_command = 0
    roll_command = 0

    if mouse_attached_to_ctrl:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        roll_command = math_helpers.lerp((cursor_ctrl_box_x, cursor_ctrl_box_x+cursor_ctrl_side_length), (-1 * cursor_ctrl_boost_factor, 1 * cursor_ctrl_boost_factor), mouse_x)
        roll_command = math_helpers.clamper(roll_command, -1, 1)
        pitch_command = math_helpers.lerp((cursor_ctrl_box_y, cursor_ctrl_box_y+cursor_ctrl_side_length), (-1 * cursor_ctrl_boost_factor , 1 * cursor_ctrl_boost_factor), mouse_y)
        pitch_command = math_helpers.clamper(pitch_command, -1, 1)

    input_commands['elevator'] = elevator_damper.smooth_damp(input_commands['elevator'], pitch_command, 0.07, 1000000, DELTA_TIME)
    input_commands['aileron'] = aileron_damper.smooth_damp(input_commands['aileron'], roll_command, 0.07, 1000000, DELTA_TIME)

## Below are the update loop and draw loop, they should always be at the bottom

def draw_buttons():
    for button in Button.instances:
        button.draw()

def pygame_functions():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # stuff related to the control cursor
            if math_helpers.within(mouse_x, cursor_ctrl_box_x, cursor_ctrl_box_x+cursor_ctrl_side_length) and math_helpers.within(mouse_y, cursor_ctrl_box_y, cursor_ctrl_box_y+cursor_ctrl_side_length) :
                attach_control()
            
            #stuff about the buttons
            for button in Button.instances:
                if button.check_hot(mouse_x, mouse_y):
                    button.actuate()

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

    #print(input_commands['elevator'], input_commands['aileron'])
    print(input_commands['ap_on'])
    draw_control_square()
    draw_control_handle()
    draw_adi()
    draw_menu()
    draw_buttons()
  
    pygame.display.update()