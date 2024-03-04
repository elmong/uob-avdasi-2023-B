#=======================PLEASE READ=======================#

#Place all csv files which you wish to plot in a folder called logdata
#Place this file in another folder
#Place both of these folders inside the same folder

#read the rest of this script for more instructions on how to use it

"""
Created on Sun Mar  3 22:31:35 2024

@authors: Henrick & Ivan 
"""

import csv
import matplotlib.pyplot as plt
import glob
import os
import sys
import subprocess

#Flags
#Change to True if you want to plot this
PLOT_PITCH = False
PLOT_ROLL = False
PLOT_YAW = False
PLOT_AIRSPEED = False
PLOT_ELEVATOR_SERVO_ACTUAL = False # this is just a rate plotted
PLOT_ELEVATOR_ANGLE = False


def openImage(path):
    imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
    subprocess.run([imageViewerFromCommandLine, path])

def plot_the_csv_output():
    print('######################################## INSTANT PLOTTER CALLED ########################################')
    root_path = os.path.abspath(os.path.dirname(__file__))
    logged_data_path = os.path.join(root_path, 'logdata')
    csv_file_path = os.path.join(logged_data_path, '*.csv')  # Join root path with the pattern to match CSV files
    csv_files = glob.glob(csv_file_path)
    if len(csv_files) == 0:
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NO CSV FILES EXIST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        return
    
    csv_file_path = max(csv_files, key=os.path.getmtime) # get the newest
    #csv_file_path = "put your path here" #use this if you want to read off of a specific file
    
    #bad code but it works

    '''columns:     time since start, 
                    time since epoch, 
                    pitch, 
                    roll, 
                    yaw, 
                    airspeed, 
                    port aileron servo demand,
                    port aileron servo actual,
                    port aileron angle,
                    port flap servo demand,
                    port flap servo actual,
                    port flap angle,
                    starboard aileron servo demand,
                    starboard aileron servo actual,
                    starboard aileron angle,
                    starboard flap servo demand,
                    starboard flap servo actual,
                    starboard flap angle,
                    elevator servo demand,
                    elevator servo actual,
                    elevator angle,
                    rudder servo demand,
                    rudder servo actual,
                    rudder angle,
    '''

    column = []
    
    if PLOT_PITCH:
        column.append(["Pitch",3])
    if PLOT_ROLL:
        column.append(["Roll",4])
    if PLOT_YAW:
        column.append(["Yaw",5])
    if PLOT_AIRSPEED:
        column.append(["Airspeed",6])
    if PLOT_ELEVATOR_SERVO_ACTUAL:
        column.append(["Elevator Actual Rate",20])
    if PLOT_ELEVATOR_ANGLE:
        column.append(["Elevator Angle",21])
    
    #if you want to plot any particular column, use the following code, changing the name and column number
    #column.append(["Name goes here", Column Number goes here])
        
    #file name of the output image is just the name, so if doing multiple plots, rename files manually to avoid overwriting

    for c in column:
        
        col_num = c[1]
        
        column1 = []
        column2 = []
        
        with open(csv_file_path, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                # Assuming column 1 is at index 0 and column 2 is at index 1
                column1.append(float(row[0]))
                column2.append(float(row[col_num - 1]))
        
        plt.figure(figsize=(10, 3))
        # Plotting column 2 vs column 1 as a red line graph with higher DPI
        plt.plot(column1, column2, color='blue', linestyle='-', linewidth = 1.5)
        plt.xlabel('Time Elapsed (s)')
        plt.ylabel(c[0])
        plt.title(c[0])
        plt.grid(True)
        image_save_path = os.path.join(root_path, 'temp_plots', c[0]+'.png')
        plt.savefig(image_save_path, dpi=200)  # Save the figure with higher DPI
        plt.show()
        print("********* FILE SAVED AT: "+image_save_path + ' *********')
    
        openImage(image_save_path)

plot_the_csv_output()

