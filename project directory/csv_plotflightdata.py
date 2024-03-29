import csv
import matplotlib.pyplot as plt
import glob
import os
import sys
import subprocess

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

    # Assuming your CSV file has two columns, and the file is named 'data.csv'
    
    # Lists to store the data from each column
    
    # WHICH_COLUMN_TO_PLOT = 4
    # 
    # column1 = []
    # column2 = []
    # 
    # # Read the CSV file and extract data
    # with open(csv_file_path, 'r') as csvfile:
    #     csv_reader = csv.reader(csvfile)
    #     for row in csv_reader:
    #         # Assuming column 1 is at index 0 and column 2 is at index 1
    #         column1.append(float(row[0]))
    #         column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))
    # 
    # plt.figure(figsize=(20, 6))
    # # Plotting column 2 vs column 1 as a red line graph with higher DPI
    # plt.plot(column1, column2, color='red', linestyle='-', linewidth = 2)
    # plt.xlabel('Time Elapsed (s)')
    # plt.ylabel('Yaw (deg)')
    # plt.title('Yaw')
    # plt.grid(True)
    # plt.savefig('Yaw.png', dpi=200)  # Save the figure with higher DPI
    # plt.show()
    
    
    
    WHICH_COLUMN_TO_PLOT = 2
    
    column1 = []
    column2 = []
    
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            # Assuming column 1 is at index 0 and column 2 is at index 1
            column1.append(float(row[0]))
            column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))
    
    plt.figure(figsize=(10, 3))
    # Plotting column 2 vs column 1 as a red line graph with higher DPI
    plt.plot(column1, column2, color='blue', linestyle='-', linewidth = 1.5)
    plt.xlabel('Time Elapsed (s)')
    plt.ylabel('Pitch (deg)')
    plt.title('Pitch')
    plt.grid(True)
    image_save_path = os.path.join(root_path, 'temp_plots', 'Pitch.png')
    plt.savefig(image_save_path, dpi=200)  # Save the figure with higher DPI
    plt.show()
    print("********* FILE SAVED AT: "+image_save_path + ' *********')

    openImage(image_save_path)

    # WHICH_COLUMN_TO_PLOT = 3
    # 
    # column1 = []
    # column2 = []
    # 
    # with open(csv_file_path, 'r') as csvfile:
    #     csv_reader = csv.reader(csvfile)
    #     for row in csv_reader:
    #         # Assuming column 1 is at index 0 and column 2 is at index 1
    #         column1.append(float(row[0]))
    #         column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))
    # 
    # plt.figure(figsize=(20, 6))
    # # Plotting column 2 vs column 1 as a red line graph with higher DPI
    # plt.plot(column1, column2, color='green', linestyle='-', linewidth = 2)
    # plt.xlabel('Time Elapsed (s)')
    # plt.ylabel('Roll (deg)')
    # plt.title('Roll')
    # plt.grid(True)
    # plt.savefig('Roll.png', dpi=200)  # Save the figure with higher DPI
    # plt.show()


