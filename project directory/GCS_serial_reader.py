#------GCS Serial Reader------#
#this file was created by IMS14

#---Import Libraries---#
from asyncio.windows_events import NULL
from global_var import control_surfaces , serial_reader_msg_size , file_path
import serial
import control_surface_map_class

#declare control surface maps, for mapping rate and adc to angle
ELEVATOR_HALL_EFFECT = control_surface_map_class.Control_Surface("elevator_hall_effect",
                                                                 [[-0.69,-0.64,-0.55,-0.46,-0.39,-0.31,-0.21,-0.12,0.03,0.15,0.26,0.36],
                                                                  [11800,14400,17300,19300,20500,22000,25100,28950,36200,40300,32000,27500],
                                                                  [45,40,34,27,22,14,6,0,-9,-20,-31,-45]])
'''ELEVATOR_POTENTIOMETER = control_surface_map_class.Control_Surface("elevator_potentiometer",
                                                                   [[0],
                                                                    [0],
                                                                    [0]])'''
RUDDER = control_surface_map_class.Control_Surface("rudder",
                                                   [[-0.68,-0.58,-0.46,-0.29,-0.18,-0.09,0,0.08,0.21,0.3,0.45,0.59,0.63,0.69],
                                                    [0],
                                                    [-40,-33,-30,-20,-8,-5,0,5,13,20,30,37,40,42]])
PORT_AILERON = control_surface_map_class.Control_Surface("port_aileron",
                                                         [[-0.27,-0.21,-0.14,-0.08,-0.04,0.05,0.16,0.19,0.23,0.29,0.38],
                                                          [17800,16800,15300,15100,14200,22750,30400,25200,24800,22600,21000],
                                                          [-40,-32,-26,-24,-20,0,12,24,28,34,51]])
PORT_FLAP = control_surface_map_class.Control_Surface("port_flap",
                                                      [[-0.23,-0.2,-0.14,-0.06,-0.04,0],
                                                       [22000,20800,19800,19400,19450,19500],
                                                       [0,7,15,23,28,31]])
STARBOARD_AILERON = control_surface_map_class.Control_Surface("starboard_aileron",
                                                              [[-1,-0.94,-0.86,-0.8,-0.73,-0.67,-0.6,-0.54,-0.46,-0.38,-0.32,-0.2,-0.06,0.01],
                                                               [0],
                                                               [30,25,16,5,0,-8,-14,-17,24,-28,-30,-32,-38,-41]])
STARBOARD_FLAP = control_surface_map_class.Control_Surface("starboard_flap",
                                                           [[-1, -0.85,-0.74,-0.5,-0.36,-0.24],
                                                            [0],
                                                            [0,6,15,18,24,30]])

#---Functions---#

def full_rate_adc_to_angle():
    #comment out if not using linear interpolation
    
    #use either hall effect sensor or potentiometer for now
    control_surfaces['elevator']['angle'] = ELEVATOR_HALL_EFFECT.rate_adc_to_angle(control_surfaces['elevator']['servo_actual'], ELEVATOR_HALL_EFFECT.adc_now)
    #control_surfaces['elevator']['angle'] = ELEVATOR_POTENTIOMETER.rate_adc_to_angle(control_surfaces['elevator']['servo_actual'], ELEVATOR_POTENTIOMETER.adc_now)

    control_surfaces['rudder']['angle'] = RUDDER.rate_to_angle(control_surfaces['rudder']['servo_actual'])
    
    control_surfaces['port_aileron']['angle']= PORT_AILERON.rate_adc_to_angle(control_surfaces['port_aileron']['servo_actual'], PORT_AILERON.adc_now)
    control_surfaces['port_flap']['angle'] = PORT_FLAP.rate_adc_to_angle(control_surfaces['port_flap']['servo_actual'], PORT_FLAP.adc_now)

    control_surfaces['starboard_aileron']['angle']= STARBOARD_AILERON.rate_to_angle(control_surfaces['starboard_aileron']['servo_actual'], STARBOARD_AILERON.adc_now)
    control_surfaces['starboard_flap']['angle'] = STARBOARD_FLAP.rate_to_angle(control_surfaces['starboard_flap']['servo_actual'])
    return None

#decoding function: want to convert messages received from pico to data
def Unpacker(msg):

    #_______________________________________________________#
    #data packets are structured, 
    #[0] is the ID of the Sensor, where 
    #   0 is the sensor connected to Elevator (ADC1) & Rudder (ADC2)
    #   1 is the sensor connected to PAileron (ADC1) & PFlap (ADC2)
    #   2 is the sensor connected to SAileron (ADC1) & SFlap (ADC2)
    
    #[1] is the time from start, 
    
    #[2] is the Angle of ADC1 (or ADC value),

    #[3] is the Angle of ADC2 (or ADC value),

    #[4] is the Angle of ADC3 (or ADC value)

    #_______________________________________________________#

    #split message into components    
    msgArray = msg.split(b"/")
       
    #clean up data obtained from serial
    for i , n in enumerate(msgArray):
        m = str(n).replace("b","")
        msgArray[i] = m.replace("'", "")

    #update values in global variables
    match msgArray[0]: 
        case '0':
            #either comment out control surfaces or ___.adc_now, or both, depending on the mode of operation
            #control_surfaces['elevator']['angle'] = float(msgArray[2])
            #control_surfaces['rudder']['angle'] = float(msgArray[3])

            ELEVATOR_HALL_EFFECT.adc_now = float(msgArray[2])
            #RUDDER.adc_now = float(msgArray[3])  #not using adc from rudder as it is not currently working
            #ELEVATOR_POTENTIOMETER.adc_now = float(msgArray[4])
        case '1':
            #control_surfaces['port_aileron']['angle'] = float(msgArray[2])
            #control_surfaces['port_flap']['angle'] = float(msgArray[3])
            
            PORT_AILERON.adc_now = float(msgArray[2])
            PORT_FLAP.adc_now = float(msgArray[3])
        case '2':
            #control_surfaces['starboard_aileron']['angle'] = float(msgArray[2])
            #control_surfaces['starboard_flap']['angle'] = float(msgArray[3])
            
            #neither starboard angle sensors are working

            #STARBOARD_AILERON.adc_now = float(msgArray[2])
            #STARBOARD_FLAP.adc_now = float(msgArray[3])
            pass
    return msgArray
    

#reads new line sent by pico
def ReadSerialMessage(serial_connection):
    message = serial_connection.readline(serial_reader_msg_size).strip()
    msg = Unpacker(message)
    #print(msg)
    return msg[0]
