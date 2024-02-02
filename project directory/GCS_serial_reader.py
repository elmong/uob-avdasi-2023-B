#------GCS Serial Reader------#
#this file was created by IMS14

#---Import Libraries---#
from asyncio.windows_events import NULL
from global_var import control_surfaces , serial_reader_msg_size , file_path
import serial

#---Functions---#

#initialise file
def init_file():
    FileName = file_path

    file = open(FileName, 'w')
    file.close()

#decoding function: want to convert messages received from pico to data
def Unpacker(msg):

    #_______________________________________________________#
    #data packets are structured, 
    #[0] is the ID of the Sensor, where 
    #   0 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   1 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   2 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   3 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   4 is the sensor connected to --- (ADC1) & --- (ADC2)
    #   5 is the sensor connected to --- (ADC1) & --- (ADC2)
    
    #[1] is the time from start, 
    
    #[2] is the Angle of ADC1,

    #[3] is the Angle of ADC2
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
            control_surfaces['elevator']['angle'] = float(msgArray[2])
            control_surfaces['rudder']['angle'] = float(msgArray[3])
        case '1':
            control_surfaces['port_aileron']['angle'] = float(msgArray[2])
            control_surfaces['port_flap']['angle'] = float(msgArray[3])
        case '2':
            control_surfaces['starboard_aileron']['angle'] = float(msgArray[2])
            control_surfaces['starboard_flap']['angle'] = float(msgArray[3])
        case '3':
            control_surfaces['elevator']['servo_pos'] = float(msgArray[2])
            control_surfaces['rudder']['servo_pos'] = float(msgArray[3])
        case '4':
            control_surfaces['port_aileron']['servo_pos'] = float(msgArray[2])
            control_surfaces['port_flap']['servo_pos'] = float(msgArray[3])
        case '5':
            control_surfaces['starboard_aileron']['servo_pos'] = float(msgArray[2])
            control_surfaces['starboard_flap']['servo_pos'] = float(msgArray[3])

    return msgArray
    

#reads new line sent by pico
def ReadSerialMessage(serial_connection):
    message = serial_connection.readline(serial_reader_msg_size).strip()
    msg = Unpacker(message)
    #print(msg)
    return msg[0]
