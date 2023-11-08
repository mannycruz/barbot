import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

# Manuela's Version

#SAFETIES / INIT

# Safety flag to prevent motor control actions
stepper_enabled = False
stepper_direction = GPIO.LOW
step_rate = 10  # Initialize step rate



#Mapping

# Create a dictionary to map bottle options to relay numbers
bottle_relay_mapping = {}


# GPIO Setup
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    initialize_pump_channels()
    initialize_relay_pins()
    initialize_stepper_pins()
    initialize_pump_control_gpio()
    

# Initialize GPIO channels for pumps 1 to 6 as outputs
# Initialize the pump channels as outputs and set them to LOW
def initialize_pump_channels():
    pump_channels = [12, 16, 20, 21, 22, 27]
    for channel in pump_channels:
        GPIO.setup(channel, GPIO.OUT)
        GPIO.output(channel, GPIO.LOW)

# Initialize relay pins as outputs and set them low
def initialize_relay_pins():
    global relay_pins
    relay_pins = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
    for pin in relay_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def initialize_stepper_pins():
    step_pin = 23
    dir_pin = 18
    enable_pin = 24
    for pin in step_pin,  dir_pin, enable_pin:
        GPIO.setup(step_pin, GPIO.OUT)
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(enable_pin, GPIO.OUT)
        GPIO.output(enable_pin, GPIO.LOW)

# Pump Control
def initialize_pump_control_gpio():
    global pump_channels
    pump_channels = [12, 16, 20, 21, 22, 27]
    for channel in pump_channels:
        GPIO.setup(channel, GPIO.OUT)
        GPIO.output(channel, GPIO.LOW)

######def update_image_visibility():
######    # ...

# Function to prime a specific pump
def prime_pump(pump_number):
    channel = pump_channels[pump_number - 1]
    GPIO.output(channel, GPIO.HIGH)
    update_image_visibility()
    root.after(3000, lambda: stop_prime_pump(pump_number))

# Function to stop priming a specific pump
def stop_prime_pump(pump_number):
    channel = pump_channels[pump_number - 1]
    GPIO.output(channel, GPIO.LOW)
    update_image_visibility()

# Function to toggle the purge state of a specific pump
def toggle_purge_pump(pump_number):
    channel = pump_channels[pump_number - 1]
    if GPIO.input(channel) == GPIO.LOW:
        GPIO.output(channel, GPIO.HIGH)
    else:
        GPIO.output(channel, GPIO.LOW)
    update_image_visibility()

# Function to enable/disable the stepper motor
def toggle_stepper_motor():
    global stepper_enabled
    if stepper_enabled:
        GPIO.output(enable_pin, GPIO.HIGH)
        stepper_enabled = False  # Disable the stepper motor
        stepper_direction_button.config(state="disabled")
        step_rate_combobox.config(state="disabled")
        step_rate_button.config(state="disabled")
        stepper_move_button.config(state="disabled")
        update_status_label()
    else:
        GPIO.output(enable_pin, GPIO.LOW)
        stepper_enabled = True  # Enable the stepper motor
        stepper_direction_button.config(state="normal")
        step_rate_combobox.config(state="normal")
        step_rate_button.config(state="normal")
        stepper_move_button.config(state="normal")
        update_status_label()

# Function to toggle the stepper motor direction
def toggle_stepper_direction():
    if stepper_enabled:
        global stepper_direction
        stepper_direction = not stepper_direction
        GPIO.output(dir_pin, stepper_direction)
        update_status_label()  # Call the update_status_label function to update the status label.

########def change_step_rate():
########    # ...

# Function to move the stepper motor
def move_stepper_motor():
    if stepper_enabled:
        GPIO.output(step_pin, GPIO.HIGH)
        root.after(step_rate, move_stepper_motor)
        GPIO.output(step_pin, GPIO.LOW)

# Function to exit and clean up the stepper motor control
def exit_stepper_program():
    GPIO.cleanup()
    root.destroy()

# Function to exit and clean up
def exit_program():
    GPIO.cleanup()
    root.destroy()


# Function to toggle the first 8 relays on or off
def toggle_all_relays():
    for pin in relay_pins[:8]:
        GPIO.output(pin, not GPIO.input(pin))



#Main GUI
def create_gui():
    root = tk.Tk()
    root.title("Control Panel")

    # Notebook Setup
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)






#Main Tabs

    # Test Mode Tab
    test_mode_tab = ttk.Frame(notebook)
    notebook.add(test_mode_tab, text='Test Mode')

    # Create a main tab for "Mixer Options"
    mixer_options_tab = ttk.Frame(notebook)
    notebook.add(mixer_options_tab, text='Mixer Options')

    # Create a main tab for "Bottle Options"
    bottle_options_tab = ttk.Frame(notebook)
    notebook.add(bottle_options_tab, text='Bottle Options')





#Sub Tabs within "TestMode"

    # Sub-Notebook for Test Mode Sections
    sub_notebook = ttk.Notebook(test_mode_tab)
    sub_notebook.pack(fill='both', expand=True)

    # Relay Control Frame
    relay_frame = ttk.Frame(sub_notebook)
    sub_notebook.add(relay_frame, text='Relay Control')

    # Pump Control Frame
    pump_frame = ttk.Frame(sub_notebook)
    sub_notebook.add(pump_frame, text='Pump Control')

    # Stepper Motor Control Frame
    stepper_frame = ttk.Frame(sub_notebook)
    sub_notebook.add(stepper_frame, text='Stepper Motor Control')





#GUI related code for "Relay Control" Tab

    # Create buttons for each relay with momentary/permanent options in the relay frame
    relay_buttons = []
    relay_menus = []

    #Toggle all relays button
    all_relays_button = tk.Button(relay_frame, text="Toggle All Relays 1-8", command=toggle_all_relays)
    all_relays_button.grid(row=len(relay_pins), column=0, columnspan=2, sticky='w')  # Place the button in the grid

    #Momentary/Permanent drop down menu
    for i, pin in enumerate(reversed(relay_pins)):
        relay_button = tk.Button(relay_frame, text=f"Relay {i+1}")
        state_var = tk.StringVar()
        state_var.set("Momentary")
        state_menu = tk.OptionMenu(relay_frame, state_var, "Momentary", "Permanent")
        relay_buttons.append(relay_button)
        relay_menus.append(state_menu)

        relay_button.grid(row=i, column=0, sticky='w')  # Place the button in a grid
        state_menu.grid(row=i, column=1, sticky='w')  # Place the drop-down menu in a grid

        relay_button.config(command=lambda p=pin, s=state_var: toggle_relay(p, s))

    # Function to toggle the state of a relay
    def toggle_relay(pin, state_var):
        if state_var.get() == "Momentary":
            GPIO.output(pin, GPIO.HIGH)
            root.after(100, lambda p=pin: GPIO.output(p, GPIO.LOW))
        else:
            GPIO.output(pin, not GPIO.input(pin))

    # Create a function to update relay names based on the mapping
    def update_relay_names():
        for i, relay_button in enumerate(relay_buttons[:8]):
            option = bottle_relay_mapping.get(i + 1, f"Relay {i + 1}")
            relay_button.config(text=option)    
        

    #Exit button
    exit_button = tk.Button(relay_frame, text="Exit", command=exit_program)
    exit_button.grid(row=len(relay_pins) + 1, column=0, columnspan=2, sticky='w')  # Place the button in the grid
  





#GUI related code for "Pump Control" Tab

    # Update the "prime" buttons to call the "prime_pump" function
    for i in range(1, 7):
        prime_button = tk.Button(pump_frame, text=f"Prime {i}", command=lambda num=i: prime_pump(num))
        prime_button.grid(row=i-1, column=0, padx=10, sticky='w')  # Place the "Prime" button in the grid
    
    # Update the "purge" buttons to call the "toggle_purge_pump" function
    for i in range(1, 7):
        purge_button = tk.Button(pump_frame, text=f"Purge {i}", command=lambda num=i: toggle_purge_pump(num))
        purge_button.grid(row=i-1, column=1, padx=10, sticky='w')  # Place the "Purge" button in the grid





#GUI related code for "Stepper Motor" Tab

    # Create a status label for stepper motor direction
    status_label = tk.Label(stepper_frame, text="Direction: STOPPED")
    status_label.grid(row=1, column=0, columnspan=2, sticky='w')  # Add this line to place the label in the grid

    # Function to update the status label for stepper motor direction
    def update_status_label():
        if stepper_direction == GPIO.LOW:
            status_label.config(text="Direction: Right")
        else:
            status_label.config(text="Direction: Left")

    # Create buttons for stepper motor control in the stepper frame
    stepper_direction_button = tk.Button(stepper_frame, text="Toggle Stepper Direction", command=toggle_stepper_direction, state="disabled")
    stepper_direction_button.grid(row=2, column=0, columnspan=2, sticky='w')  # Place the button in the grid
    stepper_enable_button = tk.Button(stepper_frame, text="Toggle Stepper Enable", command=toggle_stepper_motor, state="normal")
    stepper_enable_button.grid(row=0, column=0, columnspan=2, sticky='w')  # Place the button in the grid
    stepper_move_button = tk.Button(stepper_frame, text="Move Stepper", command=move_stepper_motor, state="normal")
    stepper_move_button.grid(row=6, column=0, columnspan=2, sticky='w')  # Place the button in the grid

    # Create an exit button in the stepper frame
    exit_stepper_button = tk.Button(stepper_frame, text="Exit", command=exit_stepper_program)
    exit_stepper_button.grid(row=7, column=0, columnspan=2, sticky='w')  # Place the button in the grid

    # Function to change the step rate
    def change_step_rate():
        if stepper_enabled:
            global step_rate
            step_rate = int(step_rate_combobox.get())

    step_rate_label = tk.Label(stepper_frame, text="Step Rate (ms):")
    step_rate_label.grid(row=3, column=0, columnspan=2, sticky='w')  # Place the label in the grid

    # Create a Combobox widget for step rate selection
    step_rate_combobox = ttk.Combobox(stepper_frame, values=[str(i) for i in range(1, 11)], state="normal")
    step_rate_combobox.set(str(step_rate))  # Set the initial value
    step_rate_combobox.grid(row=4, column=0, columnspan=2, sticky='w')  # Place the Combobox in the grid

    step_rate_button = tk.Button(stepper_frame, text="Set Step Rate", command=change_step_rate, state="normal")
    step_rate_button.grid(row=5, column=0, columnspan=2, sticky='w')  # Place the button in the grid





#GUI related code for "Mixer Options" Tab

    # Create a list of mixer options
    mixer_options = ["Soda Water", "Tonic Water", "Coke", "Orange Juice", "Pineapple Juice", "Marg Mix"]
    mixer_buttons = []

    # Create buttons for each mixer option in the mixer options tab
    for option in mixer_options:
        mixer_button = tk.Button(mixer_options_tab, text=option, state="normal", bg="red")
        mixer_button.pack()
        mixer_buttons.append(mixer_button)

        # Bind single-click to toggle red color, and double-click to toggle green color
        mixer_button.bind("<Button-1>", lambda event, button=mixer_button: toggle_option_color(button))
        mixer_button.bind("<Double-1>", lambda event, button=mixer_button: toggle_option_color(button))





#GUI related code for "Bottle Options" Tab

    # Create a list of bottle options
    bottle_options = ["Vodka", "Rum", "White Rum", "Tequila", "Gin", "Whiskey", "Triple Sec", "Sourpuss", "Peach Schnapps", "Amaretto", "Chambord", "Lemoncello", "Grenadine"]
    bottle_buttons = []

    # Create buttons for each bottle option with relay assignment in the bottle options tab
    bottle_buttons = {}  # Create a dictionary to store the buttons

    def toggle_option_color(option):
        label, _ = bottle_buttons[option]
        if label.cget("bg") == "red":
            label.config(bg="green")
        else:
            label.config(bg="red")

    def assign_bottle_to_relay(option, relay_number, label):
        if relay_number == 0:
            for i in range(1, len(bottle_options) + 1):
                bottle_relay_mapping[i] = f"Relay {i}"
        else:
            bottle_relay_mapping[relay_number] = option
        update_relay_names()

    for option in bottle_options:
        bottle_frame = tk.Frame(bottle_options_tab)
        bottle_frame.pack(fill='both')
        label = tk.Label(bottle_frame, text=option, width=20, bg="red")
        label.pack(side=tk.LEFT)
    
        # Make the label itself a button to toggle color
        label.bind("<Button-1>", lambda event, o=option: toggle_option_color(o))

        entry = tk.Entry(bottle_frame, width=3)
        entry.insert(0, "1")
        entry.pack(side=tk.LEFT)
        assign_button = tk.Button(bottle_frame, text="Assign", command=lambda o=option, e=entry, l=label: assign_bottle_to_relay(o, int(e.get()), l))
        assign_button.pack(side=tk.LEFT)
        bottle_buttons[option] = (label, assign_button)  # Store the label and assign button in the dictionary

    # Function to toggle the color of an option to red or green on click/double-click
    def toggle_option_color(button):
        if button.cget("bg") == "red":
            button.config(bg="green")
        else:
            button.config(bg="red")





#GUI related code for placing images in the Pump tab

    # Create a PhotoImage object to display the image
    photo = PhotoImage(file="/home/JakeH/Pictures/pump.png")

    # Create a Label widget to display the image
    image_label = tk.Label(pump_frame, image=photo)

    # Create a list to store image labels for active pumps
    image_labels = [None] * 6

    # Function to update the image visibility based on pump status
    def update_image_visibility():
        active_pumps = [i + 1 for i, channel in enumerate(pump_channels) if GPIO.input(channel) == GPIO.HIGH]

        # Remove existing image labels
        for i in range(6):
            if image_labels[i]:
                image_labels[i].grid_forget()

        # Create image labels next to active buttons
        for pump_number in active_pumps:
            image_label = tk.Label(pump_frame, image=photo)
            image_label.grid(row=pump_number - 1, column=2)
            image_labels[pump_number - 1] = image_label



    root.mainloop()


#Call for the GUI to start, and the entry point of the script
if __name__ == "__main__":
    initialize_gpio()
    create_gui()