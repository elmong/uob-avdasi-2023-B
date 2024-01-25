import csv
import matplotlib.pyplot as plt

# Assuming your CSV file has two columns, and the file is named 'data.csv'
csv_file_path = '2024-01-25_11-02-04.csv'

# Lists to store the data from each column

WHICH_COLUMN_TO_PLOT = 4

column1 = []
column2 = []

# Read the CSV file and extract data
with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # Assuming column 1 is at index 0 and column 2 is at index 1
        column1.append(float(row[0]))
        column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))

plt.figure(figsize=(20, 6))
# Plotting column 2 vs column 1 as a red line graph with higher DPI
plt.plot(column1, column2, color='red', linestyle='-', linewidth = 2)
plt.xlabel('Time Elapsed (s)')
plt.ylabel('Yaw (deg)')
plt.title('Yaw')
plt.grid(True)
plt.savefig('Yaw.png', dpi=1000)  # Save the figure with higher DPI
plt.show()



WHICH_COLUMN_TO_PLOT = 2

column1 = []
column2 = []

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # Assuming column 1 is at index 0 and column 2 is at index 1
        column1.append(float(row[0]))
        column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))

plt.figure(figsize=(20, 6))
# Plotting column 2 vs column 1 as a red line graph with higher DPI
plt.plot(column1, column2, color='blue', linestyle='-', linewidth = 2)
plt.xlabel('Time Elapsed (s)')
plt.ylabel('Pitch (deg)')
plt.title('Pitch')
plt.grid(True)
plt.savefig('Pitch.png', dpi=1000)  # Save the figure with higher DPI
plt.show()


WHICH_COLUMN_TO_PLOT = 3

column1 = []
column2 = []

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        # Assuming column 1 is at index 0 and column 2 is at index 1
        column1.append(float(row[0]))
        column2.append(float(row[WHICH_COLUMN_TO_PLOT - 1]))

plt.figure(figsize=(20, 6))
# Plotting column 2 vs column 1 as a red line graph with higher DPI
plt.plot(column1, column2, color='green', linestyle='-', linewidth = 2)
plt.xlabel('Time Elapsed (s)')
plt.ylabel('Roll (deg)')
plt.title('Roll')
plt.grid(True)
plt.savefig('Roll.png', dpi=1000)  # Save the figure with higher DPI
plt.show()