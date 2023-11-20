#Elmo Extracting and filtering data from cube

from pymavlink import mavutil
import numpy as np
import time
import pygame

pygame.init()
SCREEN_WIDTH = 1920
SREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SREEN_HEIGHT), pygame.RESIZABLE)
default_font = pygame.font.Font('freesansbold.ttf', 32)

airplane = {
    'pitch': '',
    'roll': '',
    'yaw': '',
    'aoa': '',
}

def pygame_functions():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
            
def draw_text(text, font, colour, x, y):
    img = font.render(text, True, colour)
    screen.blit(img, (x, y))

def pygame_drawing(): #loop
    pygame.draw.rect(screen, (255,255,255), (0,0,1920,1080))
    print(airplane['pitch'])
    draw_text(airplane['pitch'], default_font, (0,0,0), 1920/2, 1080/2)
    draw_text(airplane['roll'], default_font, (0,0,0), 1920/2, 1080/2-30*1)
    draw_text(airplane['yaw'], default_font, (0,0,0), 1920/2, 1080/2-30*2)
    draw_text(airplane['aoa'], default_font, (0,0,0), 1920/2, 1080/2-30*3)
    pygame.display.update()

port='tcp:127.0.0.1:5762' # simulator 'tcp:127.0.0.1:5762' , cube com#

connection = mavutil.mavlink_connection(port) #connect to local simulator, change to com'number' 

connection.wait_heartbeat() #heartbeat so make sure it's connected to the flight controller


print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

mav_commands = [mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 
                mavutil.mavlink.MAVLINK_MSG_ID_AOA_SSA]

# Refresh rate request
for i in range(len(mav_commands)):
    message = connection.mav.command_long_send(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
            0,  # Confirmation
            mav_commands[i],  # param1: Message ID to be streamed
            0.2*10**6, # param2: Interval in microseconds
            0, 0, 0, 0, 
            0  # target address
            )

while True:

    msg=connection.recv_match()

    if not msg:
        continue
    if msg.get_type() == 'ATTITUDE': #get type of message , check mavlink inspector on missionplanner to get type.
        attitude=msg.to_dict() #extract message to dictionary
        #print(attitude)
        
        yaw=attitude['yaw'] #extract value from dictionary : so 'roll', 'pitch', 'yawspeed'
        airplane['yaw'] = 'yaw :' + str(yaw*180/np.pi) +' deg'
        pitch=attitude['pitch']
        airplane['pitch'] = 'pitch :' + str(pitch*180/np.pi) +' deg'
        roll=attitude['roll']
        airplane['roll'] = 'roll :' + str(roll*180/np.pi) +' deg'

    if msg.get_type() == 'AOA_SSA': #get type of message , check mavlink inspector on missionplanner to get type.
        aoa_ssa=msg.to_dict()
        airplane['aoa'] = 'AOA :' + str(aoa_ssa['AOA'])

    pygame_functions()
    pygame_drawing()
    time.sleep(0.001)
