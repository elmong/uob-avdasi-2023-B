#------GCS Serial Reader------#
#this file was created by IMS14

#---Import Libraries---#
from asyncio.windows_events import NULL
from global_var import control_surfaces , serial_reader_msg_size , file_path
import serial
import control_surface_map_class

#declare control surface maps, for mapping rate and adc to angle
ELEVATOR_HALL_EFFECT = control_surface_map_class.Control_Surface("elevator_hall_effect",[[0],[0],[0]])
ELEVATOR_POTENTIOMETER = control_surface_map_class.Control_Surface("elevator_hall_effect",[[0],[0],[0]])
RUDDER = control_surface_map_class.Control_Surface("rudder",[[0],[0],[0]])
PORT_AILERON = control_surface_map_class.Control_Surface("port_aileron",[[-0.26,-0.18,-0.16,-0.1,0,0.01,0.06,0.11,0.17,0.24,0.31,0.36],[18500,17100,15800,13700,12300,14000,20400,29000,31950,29150,25000,22600],[40,31,25,11,0,-2,-7,-14-20,-28,-36,-50]])
PORT_FLAP = control_surface_map_class.Control_Surface("port_flap",[[0.04,0.07,0.17,0.21,0.27],[9500,6200,17200,21950,23800],[0,-5,-19,-21,-32]])
STARBOARD_AILERON = control_surface_map_class.Control_Surface("starboard_aileron",[[0],[0],[0]])
STARBOARD_FLAP = control_surface_map_class.Control_Surface("starboard_flap",[[0],[0],[0]])

#---Functions---#

def full_rate_adc_to_angle():
    #comment out if not using linear interpolation
    
    #use either hall effect sensor or potentiometer for now
    control_surfaces['elevator']['angle'] = ELEVATOR_HALL_EFFECT.rate_adc_to_angle(control_surfaces['elevator']['servo_actual'], ELEVATOR_HALL_EFFECT.adc_now)
    #control_surfaces['elevator']['angle'] = ELEVATOR_POTENTIOMETER.rate_adc_to_angle(control_surfaces['elevator']['servo_actual'], ELEVATOR_POTENTIOMETER.adc_now)

    #control_surfaces['rudder']['angle'] = RUDDER.rate_adc_to_angle(control_surfaces['rudder']['servo_actual'], RUDDER.adc_now)
    
    control_surfaces['port_aileron']['angle']= PORT_AILERON.rate_adc_to_angle(control_surfaces['port_aileron']['servo_actual'], PORT_AILERON.adc_now)
    control_surfaces['port_flap']['angle'] = PORT_FLAP.rate_adc_to_angle(control_surfaces['port_flap']['servo_actual'], PORT_FLAP.adc_now)

    #control_surfaces['starboard_aileron']['angle']= STARBOARD_AILERON.rate_adc_to_angle(control_surfaces['starboard_aileron']['servo_actual'], STARBOARD_AILERON.adc_now)
    #control_surfaces['starboard_flap']['angle'] = STARBOARD_FLAP.rate_adc_to_angle(control_surfaces['starboard_flap']['servo_actual'], STARBOARD_FLAP.adc_now)
    return None

#decoding function: want to convert messages received from pico to data
def Unpacker(msg):

    #_______________________________________________________#
    #data packets are structured, 
    #[0] is the ID of the Sensor, where 
    #   0 is the sensor connected to Elevator (ADC1) & Rudder (ADC2)
    #   1 is the sensor connected to PAileron (ADC1) & PFlap (ADC2)
    #   2 is the sensor connected to SAileron (ADC1) & SFlap (ADC2)
    #   3 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   4 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   5 is the sensor connected to --- (ADC1) & --- (ADC2)
    
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
    
    #write sensor data to file
    #with open(file_path, 'a') as file:
        #file.write(msgArray[0] + "," + msgArray[1] + "," + msgArray[2] + "," + msgArray[3] + "\n")

    

    #update values in global variables
    match msgArray[0]: 
        case '0':
            #either comment out control surfaces or ___.adc_now, depending on the mode of operation
            #control_surfaces['elevator']['angle'] = float(msgArray[2])
            #control_surfaces['rudder']['angle'] = float(msgArray[3])

            ELEVATOR_HALL_EFFECT.adc_now = float(msgArray[2])
            RUDDER.adc_now = float(msgArray[3])
            ELEVATOR_POTENTIOMETER.adc_now = float(msgArray[4])
        case '1':
            #control_surfaces['port_aileron']['angle'] = float(msgArray[2])
            #control_surfaces['port_flap']['angle'] = float(msgArray[3])
            
            PORT_AILERON.adc_now = float(msgArray[2])
            PORT_FLAP.adc_now = float(msgArray[3])
        case '2':
            control_surfaces['starboard_aileron']['angle'] = float(msgArray[2])
            control_surfaces['starboard_flap']['angle'] = float(msgArray[3])

            #STARBOARD_AILERON.adc_now = float(msgArray[2])
            #STARBOARD_FLAP.adc_now = float(msgArray[3])
        case '3':
            control_surfaces['elevator']['servo_pos'] = float(msgArray[2])
            control_surfaces['rudder']['servo_pos'] = float(msgArray[3])
        case '4':
            control_surfaces['port_aileron']['servo_pos'] = float(msgArray[2])
            control_surfaces['port_flap']['servo_pos'] = float(msgArray[3])
        case '5':
            control_surfaces['starboard_aileron']['servo_pos'] = float(msgArray[2])
            control_surfaces['starboard_flap']['servo_pos'] = float(msgArray[3])

    full_rate_adc_to_angle()
    return msgArray
    

#reads new line sent by pico
def ReadSerialMessage(serial_connection):
    message = serial_connection.readline(serial_reader_msg_size).strip()
    msg = Unpacker(message)
    #print(msg)
    return msg[0]
