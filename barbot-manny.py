import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

#### SETUP MODE CLASS:
#### SETUP MODE TAB FRAME AND
#### SETUP RELAY + PUMP CONTROL FRAME WITHIN TAB

class ModeControl:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.relay_buttons = []
        self.relay_menus = []

        self.image_labels = [None] * 6

        self.stepper_enabled = False
        self.stepper_direction = GPIO.LOW
        self.step_rate = 10

        self.setup_ui()

    ### Relay functions

    def toggle_all_relays(self):
        for pin in self.app.relay_pins[:8]:
            GPIO.output(pin, not GPIO.input(pin))

    def toggle_relay(self, pin, state_var):
        if state_var.get() == "Momentary":
            GPIO.output(pin, GPIO.HIGH)
            self.app.root.after(100, lambda p=pin: GPIO.output(pin, GPIO.LOW))
        else:
            GPIO.output(pin, not GPIO.input(pin))

    ### Pump functions

    def prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        GPIO.output(channel, GPIO.HIGH)
        self.update_image_visibility()
        self.app.root.after(3000, lambda: self.stop_prime_pump(pump_number))

    def stop_prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        GPIO.output(channel, GPIO.LOW)
        self.update_image_visibility()

    def toggle_purge_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        if GPIO.input(channel) == GPIO.LOW:
            GPIO.output(channel, GPIO.HIGH)
        else:
            GPIO.output(channel, GPIO.LOW)
        self.update_image_visibility()

    def update_image_visibility(self):
        active_pumps = [i + 1 for i, channel in enumerate(self.app.pump_channels) if GPIO.input(channel) == GPIO.HIGH]

        # Remove existing image labels
        for i in range(6):
            if self.image_labels[i]:
                self.image_labels[i].grid_forget()

        # Create image labels next to active buttons
        for pump_number in active_pumps:
            image_label = tk.Label(self.pump_frame, image=self.app.pump_photo)
            image_label.grid(row = pump_number - 1, column = 2)
            self.image_labels[pump_number - 1] = image_label

    ### Stepper Motor Functions
    def update_status_label(self):
        if self.stepper_direction == GPIO.LOW:
            self.status_label.config(text="Direction: Right")
        else:
            self.status_label.config(text="Direction: Left")

    def toggle_stepper_direction(self):
        if self.stepper_enabled:
            self.stepper_direction = not self.stepper_direction
            GPIO.output(dir_pin, self.stepper_direction)
            self.update_status_label()

    def toggle_stepper_motor(self): #< ----- I THINK THESE COMMANDS SHOULD GO SOMEWHERE ELSE NOT IN THE GUI STEP
        if self.stepper_enabled:
            GPIO.output(enable_pin, GPIO.HIGH)
            self.stepper_enabled = False


    def setup_ui(self):
        # Set up Test or Bar mode tabs
        mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(mode_tab, text = self.name)

        # Estabilish Modes as Notebook
        sub_notebook = ttk.Notebook(mode_tab)
        sub_notebook.pack(fill = 'both', expand = True)

        # Set up Relay Control tab for mode
        relay_frame = ttk.Frame(sub_notebook)
        sub_notebook.add(relay_frame, text = 'Relay Control')

        # Toggle all Relay Buttons
        all_relay_buttons = tk.Button(
            relay_frame,
            text = "Toggle All Relays 1-8",
            command = self.toggle_all_relays ### Might be wrong
        )

        # Place relay buttons on grid
        all_relay_buttons.grid(
            row = len(self.app.relay_pins),
            column = 0,
            columnspan = 2,
            sticky = 'w'
        )

        # Set up Momentary/Permanent drop down menus
        for i, pin in enumerate(reversed(self.app.relay_pins)):
            relay_button = tk.Button(relay_frame, text = f"Relay {i + 1}")

            state_var = tk.StringVar()
            state_var.set("Momentary")
            state_menu = tk.OptionMenu(relay_frame, state_var, "Momentary", "Permanent")

            relay_button.grid(row=i, column=0, sticky = 'w')
            state_menu.grid(row=i, column=1, sticky='w')

            relay_button.config(command = lambda p=pin, s=state_var: self.toggle_relay(p, s))

            self.relay_buttons.append(relay_button)
            self.relay_menus.append(state_menu)

        # Set up Pump Control tab
        self.pump_frame = tk.Frame(sub_notebook)
        sub_notebook.add(self.pump_frame, text = 'Pump Control')
        self.image_label = tk.Label(self.pump_frame, image = self.app.pump_photo)

        for i in range(1,7):
            prime_button = tk.Button(self.pump_frame, text=f"Prime {i}", command=lambda num=i: self.prime_pump(num))
            prime_button.grid(row = i-1, column = 0, padx = 10, sticky = 'w')

            purge_button = tk.Button(self.pump_frame, text=f"Purge {i}", command=lambda num=i: self.toggle_purge_pump(num))
            purge_button.grid(row = i-1, column = 1, padx = 10, sticky = 'w')

        # Set up Stepper Motor Control tab
        stepper_frame = ttk.Frame(sub_notebook)
        sub_notebook.add(stepper_frame, text = 'Stepper Motor Control')

        # Create status label for stepper motor direction
        self.status_label = tk.Label(stepper_frame, text="Direction: STOPPED")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky='w')

        # Create buttons for stepper motor control in the stepper frame
        stepper_direction_button = tk.Button(stepper_frame, text = "Toggle Stepper Direction", command=toggle_stepper_direction, state="disabled")
        stepper_direction_button.grid(row=2, column=0, columnspan=2, sticky='w')
        stepper_enable_button = tk.Button(self.stepper_frame, text="Toggle Stepper Enable", command=toggle_stepper_motor, state="normal")
        stepper_enable_button.grid(row = 0, column = 0, columnspan = 2, sticky = 'w')
        stepper_move_button = tk.Button(stepper_frame, text = "Move Stepper", command = move_stepper_motor, state = "normal")
        stepper_move_button.grid(row=6, column=0, columnspan=2, sticky='w')

        # Create an exit button in stepper frame
        exit_stepper_button = tk.Button(stepper_frame, text="Exit", command=self.app.exit_program)
        exit_stepper_button.grid(row=7, column=0, columnspan=2, sticky='w')



##### SETUP THE GUI

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Control Panel")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill = 'both', expand = True)

        self.relay_pins = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
        self.pump_channels = [12, 16, 20, 21, 22, 27]

        # Pump function values
        self.pump_photo = PhotoImage(file = "/home/JakeH/Pictures/pump.png")

        GPIO.setmode(GPIO.BCM)
        self.setup_pins()
        self.create_modes()

    def setup_pins(self):
        for pin in self.pump_channels + self.relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def create_modes(self):
        modes = ["Test Mode", "Bar Mode", "Mixer Options", "Bottle Options"]

        for mode_name in modes:
            if mode_name in ["Test Mode", "Bar Mode"]:
                ModeControl(self, mode_name)

        exit_button = tk.Button(self.root, text="Exit", command=lambda: self.exit_program())        
        exit_button.grid(row = len(self.relay_pins) + 1, column = 0, columnspan = 2, sticky = 'w')

    def exit_program(self):
        GPIO.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    app = App()
    app.root.mainloop()



###### SAFETIES

# Safety flag to prevent motor control actions
stepper_enabled = False
stepper_direction = GPIO.LOW
step_rate = 10

###### GLOBAL VARIABLES

global relay_pins
global pump_channels

relay_pins = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
pump_channels = [12, 16, 20, 21, 22, 27]

###### DEFINE PIN CONFORMATIONS
def setup_pins():
    
    # Initialize GPIO channels for the 6 pumps as outputs
    # Initialize pump channels as pin outputs and set to LOW
    def initialize_pump_pins():
        for pin in pump_channels:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
    
    # Initialize relay pins as outputs and set to LOW
    def initialize_relay_pins():
        for pin in relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    # Set up stepper pins
    def initialize_stepper_pins():
        step_pin = 23
        dir_pin = 18
        enable_pin = 24

        for pin in [step_pin, dir_pin, enable_pin]:
            GPIO.setup(pin, GPIO.OUT)
        
        GPIO.output(enable_pin)

    #### duplicate?
    def initialize_pump_control_gpio():
        for channel in pump_channels:
            GPIO.setup(channel, GPIO.OUT)
            GPIO.setup(channel, GPIO.LOW)

    initialize_pump_pins()
    initialize_relay_pins()
    initialize_stepper_pins()
    initialize_pump_control_gpio()


##### SETUP GUI

def exit_program(current_root):
    GPIO.cleanup()
    current_root.destroy()

def initialize_gpio(): 
    # Set GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)
    setup_pins()

##### SETUP GUI
def create_gui():

    root = tk.Tk()
    root.title("Control Panel")

    # Notebook setup
    notebook = ttk.Notebook(root)
    notebook.pack(fill = 'both', expand = True)

    main_tabs = ["Test Mode", "Bar Mode", "Mixer Options", "Bottle Options"]

    #for tab_name in main_tabs:
    #    tab = ttk.Frame(notebook)
    #    notebook.add(tab, text = tab_name)

    # Setup Test Mode tab
    test_mode_tab = ttk.Frame(notebook)
    notebook.add(test_mode_tab, text = 'Test Mode')

    # Setup Bar Mode tab
    bar_mode_tab = ttk.Frame(notebook)
    notebook.add(bar_mode_tab, text = "Bar Mode")

    # Setup Mixer Options tab
    mixer_options_tab = ttk.Frame(notebook)
    notebook.add(mixer_options_tab, text = 'Mixer Options')

    # Setup Bottle Options tab
    bottle_options_tab = ttk.Frame(notebook)
    notebook.add(bottle_options_tab, text = 'Bottle Options')

    sub_tabs = ["Relay Control", "Pump Control", "Stepper Motor Control"]

    ## Set up sub-tabs for each mode

    sub_tabs = ["Relay Control", "Pump Control", "Stepper Motor Control"]

    ## Test Mode
    test_notebook = ttk.Notebook(test_mode_tab)
    test_notebook.pack(fill = 'both', expand = True)

    test_relay_frame = ttk.Frame(test_notebook)
    test_notebook.add(test_relay_frame, text = 'Relay Control')

    test_pump_frame = ttk.Frame(test_notebook)
    test_notebook.add(test_pump_frame, text = 'Pump Control')

    test_stepper_frame = ttk.Frame(test_notebook)
    test_notebook.add(test_stepper_frame, text = 'Stepper Motor Control')

    # Test Relay Buttons
    test_relay_buttons = []
    test_relay_menus = []

    # Toggle all Test Relay Buttons
    test_all_relay_buttons = tk.Button(
                                    test_relay_frame, 
                                    text = "Toggle All Relays 1-8",
                                    command = toggle_all_relays
                                )

    # Place Test Relay Buttons on grid
    test_all_relay_buttons.grid(row = len(relay_pins),
                                column = 0,
                                columnspan = 2,
                                sticky= 'w')

    # Set up Momentary/Permanent drop down menus for test relay buttons
    for i, pin in enumerate(reversed(relay_pins)):
        test_relay_button = tk.Button(test_relay_frame, text = f"Relay {i+1}")

        test_state_var = tk.StringVar()
        test_state_var.set("Momentary")
        test_state_menu = tk.OptionMenu(test_relay_frame, test_state_var, "Momentary", "Permanent")
        
        test_relay_buttons.append(test_relay_button)
        test_relay_menus.append(test_state_menu)

        test_relay_button.grid(row = i, column = 0, sticky = 'w')
        test_state_menu.grid(row = i, column = 1, sticky = 'w')

        test_relay_button.config(command = lambda p=pin, s=test_state_var: toggle_relay(p, s))

    ## Bar Mode
    bar_notebook = ttk.Notebook(bar_mode_tab)
    bar_notebook.pack(fill = 'both', expand = True)

    bar_relay_frame = ttk.Frame(bar_notebook)
    bar_notebook.add(bar_relay_frame, text = 'Relay Control')

    bar_pump_frame = ttk.Frame(bar_notebook)
    bar_notebook.add(bar_pump_frame, text = 'Pump Control')

    bar_stepper_frame = ttk.Frame(bar_notebook)
    bar_notebook.add(bar_stepper_frame, text = 'Stepper Motor Control')

    # Bar Mode Relay Buttons
    bar_relay_buttons = []
    bar_relay_menus = []

    # Toggle all Bar Mode Relay Buttons
    bar_all_relay_buttons = tk.Button(
                                    bar_relay_frame, 
                                    text = "Toggle All Relays 1-8",
                                    command = toggle_all_relays
                                )

    # Place Test Relay Buttons on grid
    bar_all_relay_buttons.grid(row = len(relay_pins),
                                column = 0,
                                columnspan = 2,
                                sticky= 'w')

    # Set up Momentary/Permanent drop down menus for Bar Mode relay buttons
    for i, pin in enumerate(reversed(relay_pins)):
        bar_relay_button = tk.Button(bar_relay_frame, text = f"Relay {i+1}")

        bar_state_var = tk.StringVar()
        bar_state_var.set("Momentary")
        bar_state_menu = tk.OptionMenu(bar_relay_frame, bar_state_var, "Momentary", "Permanent")
        
        bar_relay_buttons.append(bar_relay_button)
        bar_relay_menus.append(bar_state_menu)

        bar_relay_button.grid(row = i, column = 0, sticky = 'w')
        bar_state_menu.grid(row = i, column = 1, sticky = 'w')

        bar_relay_button.config(command = lambda p=pin, s=bar_state_var: toggle_relay(p, s))

    def toggle_relay(pin, state_var):
        if state_var.get() == "Momentary":
            GPIO.output(pin, GPIO.HIGH)
            root.after(100, lambda p = pin: GPIO.output(p, GPIO.LOW))
        else:
            GPIO.output(pin, not GPIO.input(pin))

    # Generate exit buttons for each mode
    # This might not work and might need to duplicate code for each mode
    for frame in [test_relay_frame, bar_relay_frame]:
        exit_button = tk.Button(frame, text = "Exit", command=exit_program(root))








