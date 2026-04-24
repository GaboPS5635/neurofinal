# neurofinal
# how to make the aux work 
# To test it:

# Checklist
# 1. Plug Focusrite into laptop, guitar into Input 2
# 2. Plug Arduino into laptop via USB
# 3. Find your Arduino's serial port (/dev/ttyACM0 on Linux/Mac) and update SERIAL_PORT in the Python script
# 4. Upload the Arduino sketch via Arduino IDE
# 5. Run the Python script — strum a note and watch the terminal


# Finding your serial port:
# Mac: ls/dev/tty.* in terminal
# batch run: python3 /Users/gabopage/Documents/GitHub/neurofinal/main/guitar_pitch.py
#python3 /Users/gabopage/Documents/GitHub/neurofinal/main/guitar_pitch.py

import sounddevice as sd
import numpy as np
import crepe
import serial
import time

# --- CONFIG ---
SERIAL_PORT = "/dev/tty.usbmodem1101"  #this is the serial port for the arduino
BAUD_RATE = 9600
SAMPLE_RATE = 16000
BUFFER_SIZE = 8192 
FOCUSRITE_INPUT_CHANNEL = 1  # Input 2 = index 1
SILENCE_THRESHOLD = 0.0008
CONFIDENCE_THRESHOLD = 0.5   # 0.0 to 1.0, higher = stricter, will have to edit this

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def hz_to_note(freq): # converts frequency to note name and octave, will have to tweak this
    if freq <= 0:
        return None
    midi = 69 + 12 * np.log2(freq / 440.0)
    note = NOTE_NAMES[int(round(midi)) % 12]
    octave = (int(round(midi)) // 12) - 1
    return f"{note}{octave}"

def find_focusrite(): #finds the audio interface
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if "scarlett" in d['name'].lower() or "focusrite" in d['name'].lower():
            if d['max_input_channels'] > 0:
                print(f"Found Focusrite: [{i}] {d['name']}")
                return i
    print("Focusrite not found. Available input devices:")
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            print(f"  [{i}] {d['name']}")
    raise RuntimeError("Plug in your Focusrite and try again.")

# Connect to Arduino
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Arduino connected on {SERIAL_PORT}")
except Exception as e:
    print(f"Could not connect to Arduino: {e}")
    print("Check your SERIAL_PORT setting in the script.")
    exit()

last_note = None

def audio_callback(indata, frames, time_info, status):
    global last_note
    channel_data = indata[:, FOCUSRITE_INPUT_CHANNEL].astype(np.float32)

    if np.max(np.abs(channel_data)) < SILENCE_THRESHOLD:
        return

    _, frequency, confidence, _ = crepe.predict(
        channel_data, SAMPLE_RATE, viterbi=True, verbose=0, model_capacity='medium'
    )
    freq = float(frequency[0])
    conf = float(confidence[0])

    if conf >= CONFIDENCE_THRESHOLD:
        note = hz_to_note(freq)
        if note and note != last_note:
            print(f"  Note: {note}  ({freq:.1f} Hz, confidence: {conf:.2f})")
            ser.write(f"{note}\n".encode())
            last_note = note

# --- Start ---
device_index = find_focusrite()
print("\nListening on Input 2... Strum something! (Ctrl+C to stop)\n")

with sd.InputStream(
    device=device_index,
    channels=2,
    samplerate=SAMPLE_RATE,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
):
    while True:
        time.sleep(0.1)