"""
@file    live_plot_position.py
@brief   Real-time XY position visualization from Arduino via serial.

This script reads position data streamed over USB serial from an Arduino
calculating XY coordinates using two string-driven encoders. The data is
expected in the format:

    x,y,L1,L2

Where:
- x, y = calculated position coordinates
- L1, L2 = string lengths from each encoder

The script:
- Connects to a serial port (default: COM8 at 9600 baud)
- Reads and parses the incoming CSV-formatted data
- Plots the live (x, y) position on a 2D matplotlib scatter plot
- Updates continuously, refreshing the point in-place

Usage:
- Ensure the Arduino is running and connected to COM8 (or change as needed)
- Run the script in a Python environment with `matplotlib` installed
"""

import serial
import time
import matplotlib.pyplot as plt

ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)

# Turn on interactive mode
plt.ion()
fig, ax = plt.subplots()

scat = ax.scatter([], [])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Real-Time Position from Arduino')

ax.set_xlim([-300, 300])  
ax.set_ylim([0, 500])  
counter = 0
while True:
    print(ser.in_waiting)
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip('\r\n')
        values = line.split(',')

        if len(values) == 4:
            try:
                x = float(values[0])
                y = float(values[1])
                l1 = float(values[2])
                l2 = float(values[3])
                print(l1, l2)
                # Remove the old scatter and draw the new one
                scat.remove()
                scat = ax.scatter(x, y, color='blue')

                plt.pause(0.001)
            except ValueError:
                pass  # if something went wrong in conversion

