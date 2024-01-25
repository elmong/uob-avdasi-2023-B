#------GCS Serial Reader------#
#this file was created by IMS14

#---Import Libraries---#
from asyncio.windows_events import NULL
from global_var import angle_sensor_data_live , serial_reader_msg_size , file_path
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
            angle_sensor_data_live['sensor1'] = msgArray[2]
            angle_sensor_data_live['sensor2'] = msgArray[3]
        case '1':
            angle_sensor_data_live['sensor3'] = msgArray[2]
            angle_sensor_data_live['sensor4'] = msgArray[3]
        case '2':
            angle_sensor_data_live['sensor5'] = msgArray[2]
            angle_sensor_data_live['sensor6'] = msgArray[3]
        case '3':
            angle_sensor_data_live['sensor7'] = msgArray[2]
            angle_sensor_data_live['sensor8'] = msgArray[3]
        case '4':
            angle_sensor_data_live['sensor9'] = msgArray[2]
            angle_sensor_data_live['sensor10'] = msgArray[3]
        case '5':
            angle_sensor_data_live['sensor11'] = msgArray[2]
            angle_sensor_data_live['sensor12'] = msgArray[3]   

    return msgArray
    

#reads new line sent by pico
def ReadSerialMessage(serial_connection):
    message = serial_connection.readline(serial_reader_msg_size).strip()
    msg = Unpacker(message)
    #print(msg)
    return msg[0]
