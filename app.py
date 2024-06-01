import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import time
import os
import webbrowser
import threading

# Initialize the serial port variable
ser = None

# Function to scan for available serial ports
def scan_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return ports

# Function to update the port list dropdown
def update_ports():
    ports = scan_ports()
    port_menu['values'] = ports
    if ports:
        port_menu.current(0)

# Function to open or close the selected serial port
def toggle_port():
    global ser
    if ser and ser.is_open:
        # Close the port
        ser.close()
        log_message(f"Closed port: {ser.port}")
        open_port_button.config(text="Open Port", bg="#ffffff")
    else:
        # Open the port
        selected_port = port_menu.get()
        baudrate = baudrate_entry.get()
        try:
            ser = serial.Serial(selected_port, int(baudrate), timeout=1)
            log_message(f"Opened port: {selected_port} at {baudrate} baud.")
            open_port_button.config(text="Close Port", bg="green")
            start_reading_serial()  # Start reading serial input
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open serial port: {e}")

# Function to send command to ESP32
def send_command(command):
    global ser
    if ser and ser.is_open:
        try:
            ser.write((command + "\r\n").encode())
            log_message(f"Sent command: {command}")
            time.sleep(0.1)  # Allow time for the command to be sent
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    else:
        messagebox.showerror("Error", "Serial port is not open")

# Function to log messages to the serial monitor
def log_message(message, color="black"):
    serial_monitor.tag_configure("red", foreground="red")
    serial_monitor.tag_configure("green", foreground="green")
    serial_monitor.insert(tk.END, message + "\n", color)
    serial_monitor.see(tk.END)

# Function to toggle Motor 1 On/Off
def toggle_motor1():
    global motor1_on
    motor1_on = not motor1_on
    command = 'MOTOR1_ON' if motor1_on else 'MOTOR1_OFF'
    send_command(command)
    btn_motor1.config(text=f"Motor 1 {'ON' if motor1_on else 'OFF'}", bg="green" if motor1_on else "#ffffff")

# Function to toggle Motor 2 On/Off
def toggle_motor2():
    global motor2_on
    motor2_on = not motor2_on
    command = 'MOTOR2_ON' if motor2_on else 'MOTOR2_OFF'
    send_command(command)
    btn_motor2.config(text=f"Motor 2 {'ON' if motor2_on else 'OFF'}", bg="green" if motor2_on else "#ffffff")

# Function to run/stop Motor 1
def run_motor1():
    global motor1_run
    motor1_run = not motor1_run
    command = 'MOTOR1_RUN' if motor1_run else 'MOTOR1_STOP'
    send_command(command)
    btn_run_motor1.config(text=f"Motor 1 {'RUN' if motor1_run else 'STOP'}", bg="green" if motor1_run else "#ffffff")

# Function to run/stop Motor 2
def run_motor2():
    global motor2_run
    motor2_run = not motor2_run
    command = 'MOTOR2_RUN' if motor2_run else 'MOTOR2_STOP'
    send_command(command)
    btn_run_motor2.config(text=f"Motor 2 {'RUN' if motor2_run else 'STOP'}", bg="green" if motor2_run else "#ffffff")

# Function to toggle Solenoid
def toggle_solenoid():
    global solenoid_on
    solenoid_on = not solenoid_on
    command = 'SOLENOID_ON' if solenoid_on else 'SOLENOID_OFF'
    send_command(command)
    btn_solenoid.config(text=f"Solenoid {'ON' if solenoid_on else 'OFF'}", bg="green" if solenoid_on else "#ffffff")

# Function to cycle RGB state
def cycle_rgb():
    global rgb_state
    rgb_state = (rgb_state + 1) % 4
    states = ["RGB OFF", "RGB RED", "RGB GREEN", "RGB BLUE"]
    colors = ["#ffffff", "red", "green", "#5d94b0"]
    commands = ["RGB_OFF", "RGB_RED", "RGB_GREEN", "RGB_BLUE"]
    
    btn_rgb.config(text=states[rgb_state], bg=colors[rgb_state])
    send_command(commands[rgb_state])

# Function to cycle LED1 state
def cycle_led1():
    global led1_state
    led1_state = (led1_state + 1) % 3
    states = ["LED1 OFF", "LED1 GREEN", "LED1 RED"]
    colors = ["#ffffff", "green", "red"]
    commands = ["LED1_OFF", "LED1_GREEN", "LED1_RED"]
    
    btn_led1.config(text=states[led1_state], bg=colors[led1_state])
    send_command(commands[led1_state])

# Function to cycle LED2 state
def cycle_led2():
    global led2_state
    led2_state = (led2_state + 1) % 3
    states = ["LED2 OFF", "LED2 GREEN", "LED2 RED"]
    colors = ["#ffffff", "green", "red"]
    commands = ["LED2_OFF", "LED2_GREEN", "LED2_RED"]
    
    btn_led2.config(text=states[led2_state], bg=colors[led2_state])
    send_command(commands[led2_state])

# Function to cycle LED3 state
def cycle_led3():
    global led3_state
    led3_state = (led3_state + 1) % 3
    states = ["LED3 OFF", "LED3 GREEN", "LED3 RED"]
    colors = ["#ffffff", "green", "red"]
    commands = ["LED3_OFF", "LED3_GREEN", "LED3_RED"]
    
    btn_led3.config(text=states[led3_state], bg=colors[led3_state])
    send_command(commands[led3_state])

# Function to open URL
def open_url(url):
    webbrowser.open_new(url)

# Function to read serial data from ESP32
def read_serial():
    global ser
    while ser and ser.is_open:
        try:
            data = ser.readline().decode().strip()
            if data:
                log_message(f"Received: {data}")
                update_input_section(int(data))
        except Exception as e:
            log_message(f"Error reading serial data: {e}")

def start_reading_serial():
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()

# Function to update the input section based on received data
def update_input_section(value):
    # Assuming value is a uint8_t with the first 3 bits representing the circles
    bit1 = value & 0x01
    bit2 = (value >> 1) & 0x01
    bit3 = (value >> 2) & 0x01

    circle1_color = "green" if bit1 else "red"
    circle2_color = "green" if bit2 else "red"
    circle3_color = "green" if bit3 else "red"

    canvas.itemconfig(circle1, fill=circle1_color)
    canvas.itemconfig(circle2, fill=circle2_color)
    canvas.itemconfig(circle3, fill=circle3_color)

# NFC read tag function
def read_tag():
    log_message("Place tag on NFC reader - Timeout 5 Seconds", "green")
    root.after(5000, handle_read_tag_timeout)

def handle_read_tag_timeout():
    global ser
    if ser and ser.is_open:
        try:
            data = ser.readline().decode().strip()
            if data:
                if data.startswith("ERROR"):
                    log_message(f"Tags Data: {data}", "red")
                else:
                    log_message(f"Tags Data: {data}", "green")
            else:
                log_message("[NFC] Error: Read Timed out", "red")
        except Exception as e:
            log_message(f"Error reading NFC tag: {e}", "red")

# NFC write tag function
def write_tag():
    data = entry_write_tag.get().strip()
    if data:
        command = f"NFC_WRITE, {data}"
        log_message(f"Sent command: {command}", "green")
        send_command(command)
    else:
        log_message("[NFC] Error: No input data", "red")

# Initialize Tkinter window with a white background
root = tk.Tk()
root.title("MD Test Reg Tool")

# Set the custom icon
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
icon_image = Image.open(icon_path)
icon_image = icon_image.resize((64, 64), Image.LANCZOS)
icon_photo = ImageTk.PhotoImage(icon_image)
root.iconphoto(False, icon_photo)

root.configure(bg='#ffffff')

motor1_on = False
motor2_on = False
motor1_run = False
motor2_run = False
solenoid_on = False
rgb_state = 0  # 0: OFF, 1: RED, 2: GREEN, 3: BLUE
led1_state = 0  # 0: OFF, 1: GREEN, 2: RED
led2_state = 0  # 0: OFF, 1: GREEN, 2: RED
led3_state = 0  # 0: OFF, 1: GREEN, 2: RED

# Add logo to the upper right corner
logo_frame = tk.Frame(root, bg='#ffffff')
logo_frame.grid(row=0, column=1, padx=10, pady=10, sticky='ne')

# Load logo image using relative path
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, 'logo.png')
logo_image = Image.open(logo_path)
logo_image = logo_image.resize((150, 50), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(logo_frame, image=logo_photo, bg='#ffffff')
logo_label.pack()

# Port selection frame
frame_port = tk.LabelFrame(root, text="Port Configuration", bg='#ffffff')
frame_port.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

tk.Label(frame_port, text="Select Port:", bg='#ffffff').grid(row=0, column=0, padx=5, pady=5, sticky='e')
port_menu = ttk.Combobox(frame_port, values=scan_ports())
port_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')
update_ports_button = tk.Button(frame_port, text="Refresh Ports", command=update_ports, bg='#ffffff')
update_ports_button.grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame_port, text="Baudrate:", bg='#ffffff').grid(row=1, column=0, padx=5, pady=5, sticky='e')
baudrate_entry = tk.Entry(frame_port, bg='#ffffff')
baudrate_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
baudrate_entry.insert(0, "115200")

open_port_button = tk.Button(frame_port, text="Open Port", command=toggle_port, bg='#ffffff')
open_port_button.grid(row=1, column=2, padx=5, pady=5)

# Motors Control section
frame_motors = tk.LabelFrame(root, text="Motors Control", bg='#ffffff')
frame_motors.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# Motor 1 On/Off button
btn_motor1 = tk.Button(frame_motors, text="Motor 1 OFF", command=toggle_motor1, bg='#ffffff')
btn_motor1.grid(row=0, column=0, padx=10, pady=10)

# Motor 2 On/Off button
btn_motor2 = tk.Button(frame_motors, text="Motor 2 OFF", command=toggle_motor2, bg='#ffffff')
btn_motor2.grid(row=0, column=1, padx=10, pady=10)

# Motor 1 Run/Stop button
btn_run_motor1 = tk.Button(frame_motors, text="Motor 1 STOP", command=run_motor1, bg='#ffffff')
btn_run_motor1.grid(row=1, column=0, padx=10, pady=10)

# Motor 2 Run/Stop button
btn_run_motor2 = tk.Button(frame_motors, text="Motor 2 STOP", command=run_motor2, bg='#ffffff')
btn_run_motor2.grid(row=1, column=1, padx=10, pady=10)

# Outputs Control section
frame_outputs = tk.LabelFrame(root, text="Outputs Control", bg='#ffffff')
frame_outputs.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# RGB button
btn_rgb = tk.Button(frame_outputs, text="RGB OFF", command=cycle_rgb, bg='#ffffff')
btn_rgb.grid(row=0, column=0, padx=10, pady=10)

# LED1 button
btn_led1 = tk.Button(frame_outputs, text="LED1 OFF", command=cycle_led1, bg='#ffffff')
btn_led1.grid(row=0, column=1, padx=10, pady=10)

# LED2 button
btn_led2 = tk.Button(frame_outputs, text="LED2 OFF", command=cycle_led2, bg='#ffffff')
btn_led2.grid(row=0, column=2, padx=10, pady=10)

# LED3 button
btn_led3 = tk.Button(frame_outputs, text="LED3 OFF", command=cycle_led3, bg='#ffffff')
btn_led3.grid(row=0, column=3, padx=10, pady=10)

# Solenoid button
btn_solenoid = tk.Button(frame_outputs, text="Solenoid OFF", command=toggle_solenoid, bg='#ffffff')
btn_solenoid.grid(row=0, column=4, padx=10, pady=10)

# Inputs section
frame_inputs = tk.LabelFrame(root, text="Inputs", bg='#ffffff')
frame_inputs.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

canvas = tk.Canvas(frame_inputs, width=300, height=100, bg='#ffffff')
canvas.grid(row=1, column=0, padx=10, pady=10)

circle1 = canvas.create_oval(50, 40, 80, 70, fill='red')
circle2 = canvas.create_oval(130, 40, 160, 70, fill='red')
circle3 = canvas.create_oval(210, 40, 240, 70, fill='red')

canvas.create_text(65, 20, text="button1", fill="black")
canvas.create_text(145, 20, text="button2", fill="black")
canvas.create_text(225, 20, text="limit switch", fill="black")

# NFC section
frame_nfc = tk.LabelFrame(root, text="NFC", bg='#ffffff')
frame_nfc.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# Read Tag button
btn_read_tag = tk.Button(frame_nfc, text="Read Tag", command=read_tag, bg='#ffffff')
btn_read_tag.grid(row=0, column=0, padx=10, pady=10)

# Write Tag entry and button
entry_write_tag = tk.Entry(frame_nfc, bg='#ffffff')
entry_write_tag.grid(row=0, column=1, padx=10, pady=10)
btn_write_tag = tk.Button(frame_nfc, text="Write Tag", command=write_tag, bg='#ffffff')
btn_write_tag.grid(row=0, column=2, padx=10, pady=10)

# Serial monitor frame
frame_monitor = tk.LabelFrame(root, text="Serial Monitor", bg='#ffffff')
frame_monitor.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

serial_monitor = scrolledtext.ScrolledText(frame_monitor, wrap=tk.WORD, height=10, state='normal', bg='#ffffff', fg='#000000')
serial_monitor.pack(fill="both", expand=True)

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(5, weight=1)

# Developed by section
developed_by_frame = tk.Frame(root, bg='#ffffff')
developed_by_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='s')
developed_by_label = tk.Label(developed_by_frame, text="Developed by", font=('TkDefaultFont', 10, 'bold'), bg='#ffffff')
developed_by_label.pack()
developed_by_link = tk.Label(developed_by_frame, text="www.infinitytech.ltd", fg="blue", cursor="hand2", bg='#ffffff')
developed_by_link.pack()
developed_by_link.bind("<Button-1>", lambda e: open_url("http://www.infinitytech.ltd"))

# Run the GUI event loop
root.mainloop()

# Close serial port when GUI is closed
if ser:
    ser.close()
