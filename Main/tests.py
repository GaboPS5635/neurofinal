# code to write
# figure out how to send data from an audio interface into a python script, 
# and then use that data to signal a note into a uno r3.

# Checklist
# 1. Plug Focusrite into laptop, guitar into Input 2
# 2. Plug Arduino into laptop via USB
# 3. Find your Arduino's serial port (COM3 on Windows, /dev/ttyACM0 on Linux/Mac) and update SERIAL_PORT in the Python script
# 4. Upload the Arduino sketch via Arduino IDE
# 5. Run the Python script — strum a note and watch the terminal

# Finding your serial port:
# Mac: ls/dev/tty.* in terminal