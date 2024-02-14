import pygame
import time
import os
import math

from math_helpers import *
from global_var import *

root_path = os.path.abspath(os.path.dirname(__file__))

pygame.init()
SCREEN_WIDTH = 1920
SREEN_HEIGHT = 1080
MONITOR_SIZE = (pygame.display.Info().current_w*0.6, pygame.display.Info().current_h*0.6)
display = pygame.display.set_mode(MONITOR_SIZE, pygame.RESIZABLE, vsync=1)
screen = pygame.Surface((SCREEN_WIDTH, SREEN_HEIGHT))
pygame.display.set_caption('Company B Avionics Suite')
# Can set pygame.FULLSCREEN later if a quit button is made.

MOUSE_X = 0
MOUSE_Y = 0

fonts = {
    'default': pygame.font.Font('freesansbold.ttf', 32),
    'helvetica': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 25),
    'helvetica_big': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 30),
    'helvetica_massive': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 36),
    'helvetica_small': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 22),
    'helvetica_supersmall': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 12),
    'helvetica_bold': pygame.font.Font(os.path.join(root_path, 'fonts', 'helvetica.ttf'), 25),
    'dbxl': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 32),
    'dbxl_title': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 20),
    'dbxl_massive': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 60),
    'dbxl_small': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 15),
    'dbxl_supersmall': pygame.font.Font(os.path.join(root_path, 'fonts', 'dbxl.ttf'), 13),


}
fonts['helvetica_bold'].set_bold(True)
fonts['helvetica_supersmall'].set_bold(True)

textures = {
    'horizon': pygame.image.load(os.path.join(root_path, 'textures', 'horizon.png')).convert_alpha(),
    'wing': pygame.image.load(os.path.join(root_path, 'textures', 'wing.png')).convert_alpha(),
    'icon': pygame.image.load(os.path.join(root_path, 'textures', 'company_b_logo.png')).convert_alpha(),
    'shader' : pygame.image.load(os.path.join(root_path, 'textures', 'shader.png')).convert_alpha(),
    'servo' : pygame.image.load(os.path.join(root_path, 'textures', 'servo.png')).convert_alpha(),
    'servo_arm' : pygame.image.load(os.path.join(root_path, 'textures', 'servo_arm.png')).convert_alpha(),
    'surface' : pygame.image.load(os.path.join(root_path, 'textures', 'surface.png')).convert_alpha(),
}

pygame.display.set_icon(textures['icon'])

colours = {
    'white' : (255,255,255),
    'light_grey'  : (255/1.3,255/1.3,255/1.3),
    'grey'  : (255/2,255/2,255/2),
    'dark_grey'  : (255/4,255/4,255/4),
    'black' : (0  ,0  ,0  ),
    'bgd'   : (1  ,17 ,21 ),
    'pearl' : (247,255,228),
    'pearl_grey' : (247/2,255/2,228/2),
    'red'   : (255,102,95 ),
    'amber'   : (254,158,90 ),
    'green'   : (130,245,174 ),
    'light_blue'   : (154,255,255 ),
    'green_blue'   : (0  ,201,186 ),
    'dark_blue'   : (0  ,98,114 ),
}

class Button:
    instances = []
    def __init__(self, x, y, width, height, colour, font, text_row1, text_row2=None, callback = None):
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
        self.font = font
    
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, self.colour, 3)
        if self.text_row2:
            draw_text_centered(self.text_row1, self.font, self.colour, self.x + self.width/2, self.y + self.height/2 - 10)
            draw_text_centered(self.text_row2, self.font, self.colour, self.x + self.width/2, self.y + self.height/2 + 10)
        else:
            draw_text_centered(self.text_row1, self.font, self.colour, self.x + self.width/2, self.y + self.height/2)
        if self.is_hovered:
            draw_rectangle(self.x-4, self.y-4, self.width+7, self.height+7, self.colour, 2)
    
    def check_hot(self, MOUSE_X, MOUSE_Y):
        self.is_hovered = (
            self.x < MOUSE_X < self.x + self.width and
            self.y < MOUSE_Y < self.y + self.height
        )
    
    def actuate(self):
        if self.is_hovered:
            if not self.callback:
                print("WARNING! Button " + str(self.text_row1) + " has no callback!")
                return
            self.callback()

class ToggleButton(Button):
    def __init__(self, x, y, width, height, colour, font, text_row1, text_row2=None, callback = None):
        super().__init__( x, y, width, height, colour, font, text_row1, text_row2, callback)
        self.state = False
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, self.colour, 3)
        text_colour = colours['pearl'] # essentially overriding whatever colour argument. All toggle buttons should be of same colour
        if self.state:
            text_colour = colours['dark_blue']
            pygame.draw.rect(screen, colours['green_blue'], (self.x + 3 ,self.y + 3, self.width - 5, self.height - 5))
    
        if self.text_row2:
            draw_text_centered(self.text_row1, self.font, text_colour, self.x + self.width/2, self.y + self.height/2 - 10+3)
            draw_text_centered(self.text_row2, self.font, text_colour, self.x + self.width/2, self.y + self.height/2 + 10+3)
        else:
            draw_text_centered(self.text_row1, self.font, text_colour, self.x + self.width/2, self.y + self.height/2+3)
            
        if self.is_hovered:
            draw_rectangle(self.x-4, self.y-4, self.width+7, self.height+7, self.colour, 2)

    def actuate(self):
        if self.is_hovered:
            self.state = not self.state # change the status of the button
            super().actuate() # at the same time toggle a function
    def force_state(self, state):
        self.state = state

class SetFlaps():
    def __init__(self):
        pass
    def to(self):
        input_commands['flap_setting'] = 1
        flaps_up_button.force_state(False)
        flaps_to_button.force_state(True)
        flaps_ld_button.force_state(False)
    def ldg(self):
        input_commands['flap_setting'] = 2
        flaps_up_button.force_state(False)
        flaps_to_button.force_state(False)
        flaps_ld_button.force_state(True)
    def up(self):
        input_commands['flap_setting'] = 0
        flaps_up_button.force_state(True)
        flaps_to_button.force_state(False)
        flaps_ld_button.force_state(False)
setflaps = SetFlaps()

def ap_on():
    input_commands.update(ap_on=not input_commands['ap_on'])
    if input_commands['ap_on']:
        input_commands.update(fd_on=True)
        fd_button.force_state(True)

class ServoDisplay:
    def __init__(self):
        self.page_number = 1
    def increase(self):
        self.page_number += 1
        self.page_number = min(self.page_number, 6)
    def decrease(self):
        self.page_number -= 1
        self.page_number = max(self.page_number, 1)
servo_display = ServoDisplay()

class PicoDisplay:
    def __init__(self):
        self.page_number = 1
    def increase(self):
        self.page_number += 1
        self.page_number = min(self.page_number, 6)
    def decrease(self):
        self.page_number -= 1
        self.page_number = max(self.page_number, 1)
    def increase_com(self):
        pico_number = str(self.page_number-1)
        pico_com = coms_ports['pico'+pico_number]
        pico_com_num = int(pico_com.lstrip('COM')) +1
        coms_ports['pico'+pico_number] = 'COM' + str(pico_com_num)
    def decrease_com(self):
        pico_number = str(self.page_number-1)
        pico_com = coms_ports['pico'+pico_number]
        pico_com_num = int(pico_com.lstrip('COM')) -1
        pico_com_num = max(0, pico_com_num)
        coms_ports['pico'+pico_number] = 'COM' + str(pico_com_num)
        


pico_display = PicoDisplay()

############ The land of button creation
quit_button = Button(1704, 0, 122, 64, colours['red'], fonts['dbxl_title'], "QUIT", callback=lambda: os._exit(os.EX_OK))
pid_tuning_button = Button(865, 0, 1920-865*2, 64, colours['pearl'], fonts['dbxl_title'], "PID TUNING")
arm_button = Button(865 - 208 * 1, 0, 1920-865*2, 64, colours['pearl'], fonts['dbxl_title'], "ARM ACFT")
button_1 = Button(865 - 208 * 2, 0, 1920-865*2, 64, colours['pearl'], fonts['dbxl_title'], "FORCE RFSH", callback = lambda: ui_commands.update(force_refresh=1))
button_4 = Button(865 + 208 * 1, 0, 1920-865*2, 64, colours['pearl'], fonts['dbxl_title'], "GRAPH DSP")
pico_com_refresh_button = Button(865 + 208 * 2, 0, 1920-865*2, 64, colours['pearl'], fonts['dbxl_title'], "PICO RFSH", callback = lambda: ui_commands.update(pico_refresh_com=1))
fd_button = ToggleButton(100, 835, 120, 68, colours['pearl'], fonts['dbxl_title'], "FLT", "DIR", callback = lambda: input_commands.update(fd_on=not input_commands['fd_on'])) # This code is so dirty I hate it
ap_button = ToggleButton(100, 835+90, 120, 68, colours['pearl'], fonts['dbxl_title'], "AUTO", "FLT", callback = ap_on) 

data_button = ToggleButton(250, 835+90, 230, 68, colours['pearl'], fonts['dbxl_title'], "DATA", "LOGGING", callback = lambda: ui_commands.update(logging=not ui_commands['logging'])) 

flaps_up_button = ToggleButton(250, 835, 70, 68, colours['pearl'], fonts['dbxl_title'], "FLP", "UP", callback = setflaps.up) 
flaps_to_button = ToggleButton(250 + 75 + 5, 835, 70, 68, colours['pearl'], fonts['dbxl_title'], "FLP", "TO", callback = setflaps.to) 
flaps_ld_button = ToggleButton(250 + 75 * 2 + 10, 835, 70, 68, colours['pearl'], fonts['dbxl_title'], "FLP", "LG", callback = setflaps.ldg) 
flaps_up_button.force_state(True) # by default is up

step_button = ToggleButton(747, 716, 120, 68, colours['pearl'], fonts['dbxl_title'], "STEP", callback = lambda: stepper.send_command()) 

page_fwd_button_logging = Button(1092, 826, 90, 29, colours['pearl'], fonts['helvetica_bold'], " >> ", callback = pico_display.increase) 
page_back_button_logging = Button(1002, 826, 90, 29, colours['pearl'], fonts['helvetica_bold'], " << ", callback = pico_display.decrease) 

pico_up_button = Button(1002, 900, 60, 29, colours['pearl'], fonts['dbxl_title'], "up", callback = pico_display.increase_com) 
pico_dn_button = Button(1002, 900+29, 60, 29, colours['pearl'], fonts['dbxl_title'], "dn", callback = pico_display.decrease_com) 

page_fwd_button_servo = Button(1739-345, 216, 90, 29, colours['pearl'], fonts['helvetica_bold'], " >> ", callback = servo_display.increase) 
page_back_button_servo = Button(1649-345, 216, 90, 29, colours['pearl'], fonts['helvetica_bold'], " << ", callback = servo_display.decrease) 

############  I love OOP

def draw_line(coord_1, coord_2, width, colour):
    pygame.draw.line(screen, colour, coord_1, coord_2, width)

################

def draw_text(text, font, colour, x, y): # TODO The alignment should be grouped into a param
    text = str(text)
    text = text.replace('-', '\u2212') # Unicodes of negative sign is not handled properly
    img = font.render(text, True, colour)
    screen.blit(img, (x, y))

def draw_text_right(text, font, colour, x, y):
    text = str(text)
    text = text.replace('-', '\u2212') # Unicodes of negative sign is not handled properly
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width(), y))
    
def draw_text_right_ycentered(text, font, colour, x, y):
    text = str(text)
    text = text.replace('-', '\u2212') # Unicodes of negative sign is not handled properly
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width(), y - img.get_height()/2))
                
def draw_text_xcentered(text, font, colour, x, y):
    text = str(text)
    text = text.replace('-', '\u2212')
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width()/2, y))

def draw_text_ycentered(text, font, colour, x, y):
    text = str(text)
    text = text.replace('-', '\u2212')
    img = font.render(text, True, colour)
    screen.blit(img, (x , y - img.get_height()/2))

def draw_text_centered(text, font, colour, x, y):
    text = str(text)
    text = text.replace('-', '\u2212')
    img = font.render(text, True, colour)
    screen.blit(img, (x - img.get_width()/2, y - img.get_height()/2))

################

def draw_rectangle(x, y, width, height, colour, line_width):
    pygame.draw.line(screen, colour, (x, y), (x+width, y), line_width)
    pygame.draw.line(screen, colour, (x, y+height), (x+width, y+height), line_width)
    pygame.draw.line(screen, colour, (x, y), (x, y+height), line_width)
    pygame.draw.line(screen, colour, (x+width, y), (x+width, y+height), line_width)

def draw_image_centered(img, x, y):
    screen.blit(img, (x - img.get_width()/2, y - img.get_height()/2))

def draw_image_centered_rotated(img, x, y, angle_deg):
    img = pygame.transform.rotate(img,-angle_deg)
    screen.blit(img, (x - img.get_width()/2, y - img.get_height()/2))

def draw_background_colour():
    # w, h = pygame.display.get_surface().get_size()
    # pygame.draw.rect(screen, colours['bgd'], (0,0,w,h))
    screen.fill(colours['bgd'])

def draw_bad_screen():
    draw_background_colour()
    pygame.draw.line(screen, colours['red'], (102, 978), (709, 627), 4)
    pygame.draw.line(screen, colours['red'], (102, 1080-978), (709, 1080-627), 4)
    pygame.draw.line(screen, colours['red'], (1920-102, 978), (1920-709, 627), 4)
    pygame.draw.line(screen, colours['red'], (1920-102, 1080-978), (1920-709, 1080-627), 4)
    draw_text_xcentered( 'NO   ACTIVE', fonts['dbxl_massive'], colours['red'], 1920/2, 1080/2 - 70)
    draw_text_xcentered( 'CONNECTION', fonts['dbxl_massive'], colours['red'], 1920/2, 1080/2)

    pygame.display.update() # called once only

def draw_init_screen():
    draw_background_colour()
    pygame.draw.line(screen, colours['green_blue'], (102, 978), (709, 627), 4)
    pygame.draw.line(screen, colours['green_blue'], (102, 1080-978), (709, 1080-627), 4)
    pygame.draw.line(screen, colours['green_blue'], (1920-102, 978), (1920-709, 627), 4)
    pygame.draw.line(screen, colours['green_blue'], (1920-102, 1080-978), (1920-709, 1080-627), 4)
    draw_text_xcentered( 'WAITING   FOR', fonts['dbxl_massive'], colours['pearl'], 1920/2, 1080/2 - 70)
    draw_text_xcentered( 'INITIALISATION', fonts['dbxl_massive'], colours['pearl'], 1920/2, 1080/2)

    pygame.display.update() # called once only

def draw_adi(roll, pitch, pitch_bar):
    draw_rectangle(220, 319, 464, 464, colours['light_blue'], 2)
    pitch_px_per_deg = 507/80 # 503 px for 80 degrees pitch
    x = 220+464/2
    y = 319+464/2
    pitch_offset = pitch_px_per_deg * pitch
    horizon_x = x + pitch_offset * math.sin(math.radians(roll))
    horizon_y = y + pitch_offset * math.cos(math.radians(roll))
    img = pygame.transform.rotate(textures['horizon'],roll)
    screen.set_clip((220, 319), (464, 464))
    screen.blit(img, (horizon_x - img.get_width()/2, horizon_y - img.get_height()/2))
    screen.set_clip(None)
    draw_image_centered(textures['wing'], x, y+6)

    if input_commands['fd_on']:
        fd_size = 132
        fd_y = clamper( y - pitch_bar * pitch_px_per_deg, y-210, y+210)
        pygame.draw.line(screen, colours['bgd'], (x-fd_size-1, fd_y), (x+fd_size+1, fd_y), 5)
        pygame.draw.line(screen, colours['green'], (x-fd_size, fd_y), (x+fd_size, fd_y), 3)

def draw_log_sys():
    draw_rectangle(510, 825, 1182-510, 1000-825, colours['light_blue'], 2)
    draw_line((510, 825+30), (1182, 825+30), 2, colours['light_blue'])
    pygame.draw.rect(screen, colours['light_blue'], (510,825,30,30))
    draw_text("PICO CONFIG - PICO "+str(pico_display.page_number-1), fonts['helvetica_small'], colours['pearl'], 550, 827)
    
    buff = coms_ports['pico'+str(pico_display.page_number-1)]

    draw_text(buff, fonts['dbxl'],  colours['pearl'],800, 900)
    # draw_text("// MESSAGE LOG AND WARNINGS", fonts['helvetica_supersmall'], colours['pearl'], 515, 860)

def draw_control_bar_vert(x, y, arrow_side, arrow_ratio, text, value): # arrow ratio 0-1, value is the typed number, will be auto formatted
    draw_line((x, y+60), (x, y-60), 2, colours['pearl'])
    draw_line((x-10, y+60), (x+10, y+60), 2, colours['pearl'])
    draw_line((x-10, y-60), (x+10, y-60), 2, colours['pearl'])
    draw_text_xcentered(text, fonts['dbxl_small'], colours['pearl'], x, y+70)

    number = '{:.2f}'.format(value)
    y = y - arrow_ratio * 60
    if arrow_side == 'left':
        x = x - 4
        draw_line((x, y), (x-20, y-11), 3, colours['green'])
        draw_line((x, y), (x-20, y+11), 3, colours['green'])
        draw_line((x-20, y-11), (x-20, y+11), 3, colours['green'])
        draw_text_right_ycentered(number, fonts['dbxl_small'], colours['green'], x - 25, y)
    elif arrow_side == 'right':
        x = x + 4
        draw_line((x, y), (x+20, y-11), 3, colours['green'])
        draw_line((x, y), (x+20, y+11), 3, colours['green'])
        draw_line((x+20, y-11), (x+20, y+11), 3, colours['green'])
        draw_text_ycentered(number, fonts['dbxl_small'], colours['green'], x + 25, y)

def draw_control_bar_hori(x, y, arrow_side, arrow_ratio, text, value):
    draw_line((x-60, y), (x+60, y), 2, colours['pearl'])
    draw_line((x-60, y-10), (x-60, y+10), 2, colours['pearl'])
    draw_line((x+60, y-10), (x+60, y+10), 2, colours['pearl'])
    draw_text_xcentered(text, fonts['dbxl_small'], colours['pearl'], x, y+55)

    number = '{:.2f}'.format(value)
    x = x + arrow_ratio * 60
    if arrow_side == 'up':
        y = y - 4
        draw_line((x, y), (x-11, y-20), 3, colours['green'])
        draw_line((x, y), (x+11, y-20), 3, colours['green'])
        draw_line((x-11, y-20), (x+11, y-20), 3, colours['green'])
        draw_text_xcentered(number, fonts['dbxl_small'], colours['green'], x , y-25)
    elif arrow_side == 'down':
        y = y + 4
        draw_line((x, y), (x-11, y+20), 3, colours['green'])
        draw_line((x, y), (x+11, y+20), 3, colours['green'])
        draw_line((x-11, y+20), (x+11, y+20), 3, colours['green'])
        draw_text_xcentered(number, fonts['dbxl_small'], colours['green'], x , y+25)
    
def draw_ctrl_diag():
    draw_rectangle(1225, 540, 1860-1225, 1000-540, colours['light_blue'], 2)
    draw_rectangle(1323, 569, 465, 65, colours['pearl'], 2) # wings

    center_x = 1323+465/2

    draw_rectangle(1335, 610, 105, 24, colours['green_blue'], 2)
    draw_rectangle(1460, 610, 82, 24, colours['green_blue'], 2)

    draw_rectangle(2*center_x-1335-105, 610, 105, 24, colours['green_blue'], 2)
    draw_rectangle(2*center_x-1460-82, 610, 82, 24, colours['green_blue'], 2)
    draw_line((center_x, 635), (center_x, 800), 3, colours['grey'])

    draw_rectangle(1460, 800, (center_x-1460)*2, 50, colours['pearl'], 2)

    draw_rectangle(1460, 830, (center_x-1460)-15, 20, colours['green_blue'], 2)
    draw_rectangle((center_x)+15, 830, (center_x-1460)-15, 20, colours['green_blue'], 2)

    draw_line((center_x, 800), (center_x, 825), 3, colours['pearl'])

    draw_line((center_x, 825), (center_x, 855), 5, colours['green_blue'])

    test_val = 0

    draw_control_bar_vert(1353, 735, 'left', test_val, 'L AIL', test_val)
    draw_control_bar_vert(2*center_x-1353, 735, 'right', test_val, 'R AIL', test_val)
    draw_control_bar_vert(1415, 895, 'left', test_val, 'L ELEV', test_val)
    draw_control_bar_vert(2*center_x-1415, 895, 'right', test_val, 'R ELEV', test_val)

    draw_control_bar_hori(center_x, 900, 'down', test_val, 'RUD', test_val)

spd_damper = SmoothDamp()
prev_spd = 0
def draw_spd_tape(spd):
    # the frame
    draw_line((80, 320), (180, 320), 2, colours['light_blue'])
    draw_line((157, 320), (157, 783), 2, colours['light_blue'])
    draw_line((80, 783), (180, 783), 2, colours['light_blue'])

    global prev_spd
    spd = spd_damper.smooth_damp(spd, 0.5, 50, pygame_loop_timer.DELTA_TIME)
    spd_trend = (spd - prev_spd)/pygame_loop_timer.DELTA_TIME
    prev_spd = spd

    # the tape
    screen.set_clip((80, 322), (180-80, 783-322))
    center_y = (320 + 783)/2
    px_per_ms = 50
    spd_offset = spd * px_per_ms
    loop_start = -7 + int(spd)
    loop_end = 7 + int(spd)
    for i in range(loop_start, loop_end):
        y_coord = center_y - i * px_per_ms + spd_offset - 1
        if i%2 == 0:
            if i >= 0:
                draw_text_right(str(i).zfill(2), fonts['helvetica'], colours['pearl'], 125, y_coord - 15)
            else:
                draw_text_right(str(i).zfill(3), fonts['helvetica'], colours['pearl'], 125, y_coord - 15)
        pygame.draw.rect(screen, colours['pearl'], (140,y_coord-1,17,2))
        for j in range(4):
            pygame.draw.rect(screen, colours['pearl_grey'], (145,y_coord-1 - (j+1) * px_per_ms/5,12,2))
    draw_line((145, center_y-2), (180, center_y-2), 5, colours['green_blue'])
    screen.set_clip(None)

    #speed trend
    if abs(spd_trend) > 0.2:
        trend_tip_y = center_y - 30 * spd_trend
        trend_tip_y = clamper(trend_tip_y, 320, 783)
        draw_line((169, center_y), (169, trend_tip_y), 2, colours['green'])
        if spd_trend < 0:
            draw_line((169, trend_tip_y), (169-6, trend_tip_y-12), 2, colours['green'])
            draw_line((169, trend_tip_y), (169+6, trend_tip_y-12), 2, colours['green'])
        else:
            draw_line((169, trend_tip_y), (169-6, trend_tip_y+12), 2, colours['green'])
            draw_line((169, trend_tip_y), (169+6, trend_tip_y+12), 2, colours['green'])


    pygame.draw.polygon(screen, colours['bgd'], ((63, 527),(133, 527),(155, 550), (133, 573),(63, 573) ))   
    draw_line((63, 527), (133, 527), 2, colours['pearl'])
    draw_line((155, 550), (133, 527), 3, colours['pearl'])
    draw_line((155, 550), (133, 573), 3, colours['pearl'])
    draw_line((133, 573), (63, 573), 2, colours['pearl'])
    draw_line((63, 527), (63, 573), 2, colours['pearl'])

    screen.set_clip((64, 528), (133-64, 573-528))
    roll_px = 26
    scrolling_start = 0.9

    for i in range(-2, 12):
        y_decimal = i * roll_px - (spd%1*10) * roll_px

        y_units = 0
        if spd%1 < scrolling_start:
            y_units = i * roll_px - math.floor(spd%10) * roll_px
        else:
            y_units = i * roll_px - math.floor(spd%10) * roll_px - lerp(((spd-spd%1)+scrolling_start, spd-spd%1+1), (0,1), spd)*roll_px
        
        y_tens = 0
        if spd%10 < 9+scrolling_start:
            y_tens = i * roll_px - math.floor(spd%100/10) * roll_px
        else:
            y_tens = i * roll_px - math.floor(spd%100/10) * roll_px - lerp(((spd-spd%10)+9+scrolling_start, spd-spd%10+10), (0,1), spd)*roll_px

        y_decimal = clamper(y_decimal, -235, 235)
        y_units = clamper(y_units, -235, 235)
        y_tens = clamper(y_tens, -235, 235)
        draw_text_centered(str(i%10), fonts['helvetica_big'], colours['green'], 125, 550 - y_decimal)
        draw_text_centered(str(i%10), fonts['helvetica_big'], colours['green'], 101, 550 - y_units)
        draw_text_centered(str(i%10), fonts['helvetica_big'], colours['green'], 85, 550 - y_tens)

    pygame.draw.rect(screen, colours['green'], (110,558,3,3))
    screen.set_clip(None)
    draw_image_centered(textures['shader'], (63+133)/2+2, (527+573)/2+1)
    # pygame.draw.rect(screen, colours['bgd'], (63+2, 527+2,133-63-2,573-527-2))

class Stepper:
    def __init__(self):
        self.attached_to_ctrl = False
        self.max_pitch = 30
        self.handle_x_coord = (760+853)/2
        self.handle_y_coord = (321+696)/2
        self.handle_height = 10
        self.handle_width = 62
        self.displayed_pitch = 0
        self.region_min_x = 760
        self.region_max_x = 853
        self.region_min_y = 321
        self.region_max_y = 696
        self.click_start_time = time.time()

    def draw(self):
        draw_line(((760+853)/2-20, 321), ((760+853)/2-20, 696), 3, colours['grey'])
        draw_line((760+10-20, 696), (853-10-20, 696), 3, colours['pearl'])
        draw_line((760+10-20, 321), (853-10-20, 321), 3, colours['pearl'])
        draw_line((760+30-20, (321+696)/2), (853-30-20, (321+696)/2), 3, colours['pearl'])

        pch_cmd = self.displayed_pitch
        half_length = 188 # how high in px from 0 to max pch bar

        for i in range(-5, 5 + 1):
            if i != 0:
                draw_line((760+30-20, (321+696)/2 + (i/6) * half_length), (853-30-20, (321+696)/2 + (i/6) * half_length), 3, colours['grey'])

        handle_y_offset = -pch_cmd * (half_length/self.max_pitch)
        self.handle_y_coord = (321+696)/2 + handle_y_offset
        pygame.draw.rect(screen, colours['green_blue'], (self.handle_x_coord-self.handle_width/2-20, self.handle_y_coord-self.handle_height/2, self.handle_width, self.handle_height))
        pygame.draw.rect(screen, colours['light_blue'], (self.handle_x_coord-self.handle_width/2-20+2, self.handle_y_coord-self.handle_height/2+2, self.handle_width-4, self.handle_height-4))

        draw_text_ycentered(int(pch_cmd), fonts['dbxl'], colours['green'] if input_commands['fd_pitch'] == pch_cmd else colours['amber'], (760+853)/2+20, (321+696)/2)

    def attach(self):
        self.attached_to_ctrl = True

    def detach(self):
        self.attached_to_ctrl = False

    def match_handle(self):
        buff = -(MOUSE_Y-(321+696)/2) / (12.2*15/self.max_pitch)
        buff = clamper(int(buff), -self.max_pitch, self.max_pitch)
        self.displayed_pitch = buff
        self.attach()

    def update(self):
        if time.time() - self.click_start_time > 0.5:
            step_button.force_state(False)
        if self.attached_to_ctrl:
            self.match_handle()

    def send_command(self):
        input_commands['fd_pitch'] = self.displayed_pitch
        self.click_start_time = time.time()

stepper = Stepper()


def draw_menu():
    w, h = screen.get_size()
    draw_line((0, 112), (w, 112), 3, colours['pearl'])
    draw_text_xcentered('SYSTEM MENU ACCESS', fonts['dbxl_small'], colours['pearl'], 1920/2, 92)

def draw_refresh_rate():
    rate = airplane_data['mavlink_refresh_rate']
    if rate > 25:
        pygame.draw.rect(screen, colours['green_blue'], (20,96,min(rate, 133),7))
        draw_text( 'MAVLINK : ' + str(int(rate)), fonts['dbxl_small'], colours['green_blue'], 20, 80)
    else:
        pygame.draw.rect(screen, colours['red'], (20,96,min(rate, 133),7))
        draw_text( 'MAVLINK : ' + str(int(rate)), fonts['dbxl_small'], colours['red'], 20, 80)
    
    rate2 = airplane_data['pico_refresh_rate']
    if rate2 > 25:
        pygame.draw.rect(screen, colours['green_blue'], (210,96,min(rate2, 133),7))
        draw_text( 'PICO DATA : ' + str(int(rate2)), fonts['dbxl_small'], colours['green_blue'], 210, 80)
    else:
        pygame.draw.rect(screen, colours['red'], (210,96,min(rate2, 133),7))
        draw_text( 'PICO DATA : ' + str(int(rate2)), fonts['dbxl_small'], colours['red'], 210, 80)

class MouseControl():
    def __init__(self):
        self.mouse_attached_to_ctrl = False
        self.elevator_damper = SmoothDamp() #init the instances
        self.aileron_damper = SmoothDamp()
        self.cursor_ctrl_box_x = 939
        self.cursor_ctrl_box_y = 540
        self.cursor_ctrl_side_length = 244
        self.cursor_ctrl_boost_factor = 1.05 # self.cursor_ctrl_boost_factor for aesthetics, so that the cross don't stick to the edge

    def attach(self): # if x and y is in range, attach the mouse control
        self.mouse_attached_to_ctrl = True
    
    def detach(self):
        self.mouse_attached_to_ctrl = False
    
    def update(self):
        pitch_command = 0
        roll_command = 0
    
        if self.mouse_attached_to_ctrl:
            global MOUSE_X
            global MOUSE_Y
            roll_command = lerp((self.cursor_ctrl_box_x, self.cursor_ctrl_box_x+self.cursor_ctrl_side_length), (-1 * self.cursor_ctrl_boost_factor, 1 * self.cursor_ctrl_boost_factor), MOUSE_X)
            roll_command = clamper(roll_command, -1, 1)
            pitch_command = lerp((self.cursor_ctrl_box_y, self.cursor_ctrl_box_y+self.cursor_ctrl_side_length), (-1 * self.cursor_ctrl_boost_factor , 1 * self.cursor_ctrl_boost_factor), MOUSE_Y)
            pitch_command = clamper(pitch_command, -1, 1)
    
        input_commands['elevator'] = self.elevator_damper.smooth_damp(pitch_command, 0.07, 1000000, pygame_loop_timer.DELTA_TIME)
        input_commands['aileron'] = self.aileron_damper.smooth_damp(roll_command, 0.07, 1000000, pygame_loop_timer.DELTA_TIME)
    
    def draw(self):
        draw_rectangle(self.cursor_ctrl_box_x, self.cursor_ctrl_box_y, self.cursor_ctrl_side_length, self.cursor_ctrl_side_length, colours['grey'], 4)
        draw_rectangle(self.cursor_ctrl_box_x, self.cursor_ctrl_box_y, self.cursor_ctrl_side_length, self.cursor_ctrl_side_length, colours['pearl'], 2)

        x = lerp( (-1, 1) , (self.cursor_ctrl_box_x, self.cursor_ctrl_box_x+self.cursor_ctrl_side_length), input_commands['aileron']/self.cursor_ctrl_boost_factor)
        y = lerp( (-1, 1) , (self.cursor_ctrl_box_y, self.cursor_ctrl_box_y+self.cursor_ctrl_side_length), input_commands['elevator']/self.cursor_ctrl_boost_factor)
        offsets = 3
        line_length = 14
        pygame.draw.line(screen, colours['pearl'], (x + offsets, y + offsets) , (x + offsets + line_length, y + offsets), 2)
        pygame.draw.line(screen, colours['pearl'], (x + offsets, y + offsets) , (x + offsets , y + offsets + line_length), 2)

        pygame.draw.line(screen, colours['pearl'], (x - offsets, y + offsets) , (x - offsets - line_length, y + offsets), 2)
        pygame.draw.line(screen, colours['pearl'], (x - offsets, y + offsets) , (x - offsets , y + offsets + line_length), 2)

        pygame.draw.line(screen, colours['pearl'], (x + offsets, y - offsets) , (x + offsets + line_length, y - offsets), 2)
        pygame.draw.line(screen, colours['pearl'], (x + offsets, y - offsets) , (x + offsets , y - offsets - line_length), 2)

        pygame.draw.line(screen, colours['pearl'], (x - offsets, y - offsets) , (x - offsets - line_length, y - offsets), 2)
        pygame.draw.line(screen, colours['pearl'], (x - offsets, y - offsets) , (x - offsets , y - offsets - line_length), 2)


mouse_control = MouseControl()

def draw_servo_diagnostic():
    draw_rectangle(939, 215, 545, 270, colours['light_blue'], 2)
    pygame.draw.line(screen, colours['light_blue'], (939, 215+30) , (939+545, 215+30), 2)
    pygame.draw.rect(screen, colours['light_blue'], (939,215,30,30))

    draw_rectangle( 1513,215,384,105, colours['light_blue'], 2)
    pygame.draw.line(screen, colours['light_blue'], (1513, 215+73) , (1513+384, 215+73), 2)

    draw_rectangle( 1513,337,384,105, colours['light_blue'], 2)
    pygame.draw.line(screen, colours['light_blue'], (1513, 337+73) , (1513+384, 337+73), 2)

    draw_image_centered(textures['servo'], 1070, 371)

    servo_angle = 0
    surface_angle = 0
    servo_demand = 0
    title = "CTRL "

    match servo_display.page_number:
        case 1:
            #surface_angle = angle_sensor_data_live['paileron']#control_surfaces['left_aileron']['angle']
            surface_angle =control_surfaces['port_aileron']['angle']
            servo_demand = control_surfaces['port_aileron']['servo_demand']
            title += "- L AILERON"
        case 2:
            #surface_angle = angle_sensor_data_live['pflap']#control_surfaces['left_flap']['angle']
            surface_angle =control_surfaces['port_flap']['angle']
            servo_demand = control_surfaces['port_flap']['servo_demand']
            title += "- L FLAP"
        case 3:
            #surface_angle = angle_sensor_data_live['saileron']#control_surfaces['right_aileron']['angle']
            surface_angle =control_surfaces['starboard_aileron']['angle']
            servo_demand = control_surfaces['starboard_aileron']['servo_demand']
            title += "- R AILERON"
        case 4:
            #surface_angle = angle_sensor_data_live['sflap']#control_surfaces['right_flap']['angle']
            surface_angle =control_surfaces['starboard_flap']['angle']
            servo_demand = control_surfaces['starboard_flap']['servo_demand']
            title += "- R FLAP"
        case 5:
            #surface_angle = angle_sensor_data_live['elevator']#control_surfaces['elevator']['angle']
            surface_angle =control_surfaces['elevator']['angle']
            servo_demand = control_surfaces['elevator']['servo_demand']
            title += "- ELEVATOR"
        case 6:
            #surface_angle = angle_sensor_data_live['rudder']#control_surfaces['rudder']['angle']
            surface_angle =control_surfaces['rudder']['angle']
            servo_demand = control_surfaces['rudder']['servo_demand']
            title += "- RUDDER"
    
    servo_angle = servo_demand * 45
    servo_demand = clamper(1500 + servo_demand * 500, 1000, 2000)

    draw_text(title, fonts['helvetica_small'], colours['pearl'], 978, 217)

    draw_image_centered_rotated(textures['servo_arm'], 1099, 370, servo_angle)

    draw_image_centered_rotated(textures['surface'], 1280, 370, surface_angle)

    pygame.draw.line(screen, colours['green_blue'], (int(1099 + 83 * math.sin(math.radians(servo_angle))), int(370 - 83*math.cos(math.radians(servo_angle)))) , (int(1280 + 88 * math.sin(math.radians(surface_angle-13.72))), int(370 - 88*math.cos(math.radians(surface_angle-13.72)))), 4)

    draw_text("// TMS CMD POSITION", fonts['dbxl_supersmall'], colours['pearl'], 1520, 218)
    draw_text(("+" if servo_angle >= 0 else "-")+(str(int(abs(servo_angle))).zfill(2) + " DEG"), fonts['helvetica_massive'], colours['pearl'], 1625, 237)
    draw_text_centered("[   <<<     >>>   ]", fonts['helvetica_bold'], colours['pearl'], 1702, 302)

    draw_text("// HALL SENSOR POSITION", fonts['dbxl_supersmall'], colours['pearl'], 1520, 218+122)
    draw_text(("+" if servo_angle >= 0 else "-")+(str(int(abs(surface_angle))).zfill(2) + " DEG"), fonts['helvetica_massive'], colours['pearl'], 1625, 237+122)
    draw_text_centered("[   <<<     >>>   ]", fonts['helvetica_bold'], colours['pearl'], 1702, 302+122)

    draw_text_centered("PWM VAL: "+str(int(servo_demand)).zfill(3), fonts['dbxl_title'], colours['green_blue'], 1070, 420)

def draw_aoa_bar(aoa):
    draw_rectangle(614, 215, 280, 70, colours['light_blue'], 2)
    draw_text_centered("A", fonts['dbxl_title'], colours['pearl'], 610+22, 215+70/2-20+2)
    draw_text_centered("O", fonts['dbxl_title'], colours['pearl'], 610+22, 215+70/2+2)
    draw_text_centered("A", fonts['dbxl_title'], colours['pearl'], 610+22, 215+70/2+20+2)

    aoa = int(aoa)

    for i in range(15):
        pygame.draw.rect(screen, colours['dark_grey'], ( 618+35 + i * 16,215 + 10, 6, 50))
        if i < aoa:
            col = colours['green_blue']
            if i > 9 and i <= 12:
                col = colours['amber']
            elif i > 12:
                col = colours['red']
            pygame.draw.rect(screen, col, ( 618+35 + i * 16,215 + 10, 6, 50))

def draw_hdg_tape(hdg):

    if hdg < 0:
        hdg = hdg + 360
    center_x = (81 + 500+81)/2
    px_per_10_deg = 80

    screen.set_clip((81, 215), (500, 70))
    for i in range(0 - 3, 36 + 3 + 1):
        number_x_pos = center_x + i * px_per_10_deg - (hdg/10) * px_per_10_deg
        if within(number_x_pos, 81 - 50, 500 + 81 + 50):
            pygame.draw.line(screen, colours['pearl'], (number_x_pos, 215) , (number_x_pos, 215+20), 2)
            draw_text_xcentered(str((i%36)*10).zfill(3), fonts['helvetica'], colours['pearl'], number_x_pos, 240)
            for j in range(1,10):
                line_x_pos = number_x_pos + j*px_per_10_deg/10
                if j != 5:
                    pygame.draw.line(screen, colours['grey'], (line_x_pos, 215) , (line_x_pos, 215+10), 2)
                else:
                    pygame.draw.line(screen, colours['pearl'], (line_x_pos, 215) , (line_x_pos, 215+15), 2)

    screen.set_clip(None)   
    pygame.draw.line(screen, colours['light_blue'], (81, 215) , (81, 215+70), 2)
    pygame.draw.line(screen, colours['light_blue'], (500+81, 215) , (500+81, 215+70), 2)
    pygame.draw.line(screen, colours['light_blue'], (81, 215) , (500+81, 215), 2)

    pygame.draw.rect(screen, colours['pearl'], ( center_x - 40-2, 215 + 13-2, 40*2+4, 45+4+4))
    pygame.draw.rect(screen, colours['bgd'], ( center_x - 40, 215 + 13, 40*2, 45+4))
    draw_text_xcentered(str(int(hdg)).zfill(3), fonts['helvetica_big'], colours['green'], center_x, 234)

    compass_center_x = (center_x - 245) + (45+4+4 + 10)/2
    compass_center_y = 221 + (45+4+4 + 10)/2

    triangle_width = 7
    triangle_height = 26

    pygame.draw.circle(screen, colours['light_blue'], (compass_center_x, compass_center_y), 31)
    pygame.draw.circle(screen, colours['bgd'], (compass_center_x, compass_center_y), 29)

    pygame.draw.line(screen, colours['light_grey'], (compass_center_x, compass_center_y + 20), (compass_center_x, compass_center_y + 29) , 2)
    pygame.draw.line(screen, colours['light_grey'], (compass_center_x, compass_center_y - 20), (compass_center_x, compass_center_y - 29) , 2)
    pygame.draw.line(screen, colours['light_grey'], (compass_center_x + 20, compass_center_y), (compass_center_x + 29, compass_center_y) , 2)
    pygame.draw.line(screen, colours['light_grey'], (compass_center_x - 20, compass_center_y), (compass_center_x - 29, compass_center_y) , 2)

    pygame.draw.polygon(screen, colours['red'], (
        (compass_center_x + triangle_width*math.cos(math.radians(-hdg-180)), compass_center_y + triangle_width*math.sin(math.radians(-hdg-180))),
        (compass_center_x + triangle_width*math.cos(math.radians((-hdg+180-180))), compass_center_y + triangle_width*math.sin(math.radians((-hdg+180-180)))),
        (compass_center_x + triangle_height*math.cos(math.radians((-hdg+90-180))), compass_center_y + triangle_height*math.sin(math.radians((-hdg+90-180))))
        )
    )  
    pygame.draw.polygon(screen, colours['light_grey'], (
        (compass_center_x + triangle_width*math.cos(math.radians(-hdg)), compass_center_y + triangle_width*math.sin(math.radians(-hdg))),
        (compass_center_x + triangle_width*math.cos(math.radians((-hdg+180))), compass_center_y + triangle_width*math.sin(math.radians((-hdg+180)))),
        (compass_center_x + triangle_height*math.cos(math.radians((-hdg+90))), compass_center_y + triangle_height*math.sin(math.radians((-hdg+90))))
        )
    ) 

ap_on_time = 0
def draw_ap_status(flag):
    screen_w, screen_h = screen.get_size()
    width = 700
    height = 50
    global ap_on_time
    
    if flag:
        draw_rectangle(screen_w/2 - width/2, 135, width, height, colours['pearl'], 2)
        pygame.draw.rect(screen, colours['green_blue'], ( screen_w/2 - width/2 + 4, 135 + 4, width - 6, height - 6))
        draw_text_xcentered("))))     AP ACTIVE     ((((", fonts['dbxl'], colours['light_blue'], screen_w/2, 145)
        ap_on_time = time.time()
    else:
        if time.time() - ap_on_time < 1:
            draw_rectangle(screen_w/2 - width/2, 135, width, height, colours['pearl'], 2)
            pygame.draw.rect(screen, colours['red'], ( screen_w/2 - width/2 + 4, 135 + 4, width - 6, height - 6))
            draw_text_xcentered("((((    AP DISENGAGE    ))))", fonts['dbxl'], colours['pearl'], screen_w/2, 145)

## Below are the update loop and draw loop, they should always be at the bottom

def draw_buttons():
    for button in Button.instances:
        button.draw()

pygame_loop_timer = Timer()

def pygame_update_loop():
    mouse_beforetransform_x, mouse_beforetransform_y = pygame.mouse.get_pos()
    screen_w, screen_h = screen.get_size()
    display_w, display_h = display.get_size()

    global MOUSE_X
    global MOUSE_Y
    MOUSE_X = mouse_beforetransform_x * (screen_w/display_w)
    MOUSE_Y = mouse_beforetransform_y * (screen_h/display_h)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.VIDEORESIZE:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #stuff about the buttons
            for button in Button.instances:
                # the condition to check if mouse is over is already included in the check_hot step than changes a flag
                button.actuate()



            # stuff related to the control cursor
            if within(MOUSE_X, mouse_control.cursor_ctrl_box_x, mouse_control.cursor_ctrl_box_x+mouse_control.cursor_ctrl_side_length) and within(MOUSE_Y, mouse_control.cursor_ctrl_box_y, mouse_control.cursor_ctrl_box_y+mouse_control.cursor_ctrl_side_length) :
                mouse_control.attach()
            elif within(MOUSE_X, stepper.handle_x_coord - 50, stepper.handle_x_coord + 50) and within(MOUSE_Y, stepper.handle_y_coord - 20, stepper.handle_y_coord + 20):
                stepper.attach()
            elif within(MOUSE_X, stepper.region_min_x, stepper.region_max_x) and within(MOUSE_Y, stepper.region_min_y, stepper.region_max_y):
                stepper.match_handle()

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_control.detach()
            stepper.detach()

    for button in Button.instances:
        button.check_hot(MOUSE_X, MOUSE_Y)

    pygame_loop_timer.update() # should come before anything else
    mouse_control.update()
    stepper.update()
    
def pygame_draw_loop(): #loop
    draw_background_colour()

    # previously for testing
    # draw_text_xcentered( 'YAW : ' + str(round(airplane_data['yaw'], 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2)
    # draw_text_xcentered( 'ROLL : ' + str(round(airplane_data['roll'], 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*1)
    # draw_text_xcentered( 'PITCH : ' + str(round(airplane_data['pitch'], 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*2)
    # draw_text_xcentered( 'AOA : ' + str(round(airplane_data['aoa'], 1)) +' DEG', fonts['dbxl'], colours['pearl'], 1920/2, 1080/2 - 30*3)
    #print(input_commands['elevator'], input_commands['aileron'])

    draw_adi(airplane_data['roll'], airplane_data['pitch'], input_commands['pitch_pid']*10)
    draw_spd_tape(airplane_data['airspeed'])
    #draw_spd_tape(15*math.sin(time.time()/10)**2)
    draw_menu()
    draw_refresh_rate()
    draw_log_sys()
    draw_ctrl_diag()
    draw_aoa_bar(airplane_data['pitch'])
    stepper.draw()
    mouse_control.draw()
    draw_servo_diagnostic()
    draw_hdg_tape(airplane_data['yaw'])
    draw_ap_status(input_commands['ap_on'])
    draw_buttons()

    drawing_surface_center = screen.get_rect().center
    scaled_drawing_surface = pygame.transform.smoothscale(screen, display.get_size())
    display.blit(scaled_drawing_surface, (0, 0))
  
    pygame.display.update()