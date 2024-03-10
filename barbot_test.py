#import RPi.GPIO as GPIO
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
        self.stepper_direction = "GPIO.LOW"
        self.step_rate = 10

    # Relay Functions

    def toggle_all_relays(self):
        for pin in self.app.relay_pins[:8]:
            print(f"GPIO.output({pin}, not GPIO.input(pin))")

    def toggle_relay(self, pin, state_var):
        if state_var.get() == "Momentary":
            print("GPIO.output(pin, GPIO.HIGH)")
            print("self.app.root.after(100, lambda p=pin: GPIO.output(p, GPIO.LOW))")
        else:
            print("GPIO.output(pin, not GPIO.input(pin))")

    # Pump functions

    def prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        print("GPIO.output(channel, GPIO.HIGH)")
        self.update_image_visibility()
        self.app.root.after(3000, lambda: self.stop_prime_pump(pump_number))

    def stop_prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        print("GPIO.output(channel, GPIO.LOW)")
        self.update_image_visibility()

    def toggle_purge_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        print("if GPIO.input(channel) == GPIO.LOW: GPIO.output(channel, GPIO.HIGH)else: GPIO.output(channel, GPIO.LOW)")
        self.update_image_visibility()

    def update_image_visibility(self):
        #active_pumps = [i + 1 for i, channel in enumerate(self.app.pump_channels)] 
        #print("if GPIO.input(channel) == GPIO.HIGH]")

        # Remove existing image labels
        for i in range(6):
            if self.image_labels[i]:
                self.image_labels[i].grid_forget()

        # Create image labels next to active buttons
        for pump_number in active_pumps:
            image_label = tk.Label(self.pump_frame)
            image_label.grid(row = pump_number - 1, column = 2)
            self.image_labels[pump_number - 1] = image_label
    
    ### Stepper Motor Functions
    def update_status_label(self):
        if self.stepper_direction == "GPIO.LOW":
            self.status_label.config(text="Direction: Right")
        else:
            self.status_label.config(text="Direction: Left")

    def toggle_stepper_direction(self):
        if self.stepper_enabled:
            stepper_dict = {"GPIO.LOW" : "GPIO.HIGH", "GPIO.HIGH": "GPIO.LOW"}
            self.stepper_direction = stepper_dict(self.stepper_direction)
            print("GPIO.output(self.app.dir_pin, self.stepper_direction)")
            self.update_status_label()

    def toggle_stepper_motor(self):
        if self.stepper_enabled:
            print("GPIO.output(self.app.enable_pin, GPIO.HIGH)")
            self.stepper_enabled = False
            self.stepper_direction_button.config(state="disabled")
            self.step_rate_combobox.config(state="disabled")
            self.step_rate_button.config(state="disabled")
            self.stepper_move_button.config(state="disabled")
            self.update_status_label()
        else:
            print("GPIO.output(self.app.enable_pin, GPIO.LOW)")
            self.stepper_enabled = True
            self.stepper_direction_button.config(state="normal")
            self.step_rate_combobox.config(state="normal")
            self.step_rate_button.config(state="normal")
            self.stepper_move_button.config(state="normal")
            self.update_status_label()

    def change_step_rate(self):
        if self.stepper_enabled:
            self.step_rate = int(self.step_rate.combobox.get())

    def move_stepper_motor(self):
        if self.stepper_enaled:
            print("GPIO.output(step_pin, GPIO.HIGH)")
            #root.after(self.step_rate, move_stepper_motor)
            print("GPIO.output(step_pin, GPIO.LOW)")

    def setup_ui(self):
        # Set up tabs
        print("set up tabs")
        self.mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.mode_tab, text = self.name)

        print("set up sub notebook")
        # Estabilish Modes as Notebook
        self.sub_notebook = ttk.Notebook(self.mode_tab)
        self.sub_notebook.pack(fill = 'both', expand = True)

        print("set up relay control tab")
        # Set up Relay Control tab for mode
        self.relay_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.relay_frame, text = 'Relay Control')

        print("toggle relay buttons")
        # Toggle all Relay Buttons
        self.all_relay_buttons = tk.Button(
            self.relay_frame,
            text = "Toggle All Relays 1-8",
            command = self.toggle_all_relays ### Might be wrong
        )

        print("place relay buttons on grid")
        # Place relay buttons on grid
        self.all_relay_buttons.grid(
            row = len(self.app.relay_pins),
            column = 0,
            columnspan = 2,
            sticky = 'w'
        )

        print("set up drop down menus")
        # Set up Momentary/Permanent drop down menus
        for i, pin in enumerate(reversed(self.app.relay_pins)):
            self.relay_button = tk.Button(self.relay_frame, text = f"Relay {i + 1}")

            self.state_var = tk.StringVar()
            self.state_var.set("Momentary")
            self.state_menu = tk.OptionMenu(self.relay_frame, self.state_var, "Momentary", "Permanent")

            self.relay_button.grid(row=i, column=0, sticky = 'w')
            self.state_menu.grid(row=i, column=1, sticky='w')

            self.relay_button.config(command = lambda p=pin, s=self.state_var: self.toggle_relay(p, s))

            self.relay_buttons.append(self.relay_button)
            self.relay_menus.append(self.state_menu)

        print("set up pump control tab")
        # Set up Pump Control tab
        self.pump_frame = tk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.pump_frame, text = 'Pump Control')
        self.image_label = tk.Label(self.pump_frame)

        print("Update prime buttons")
        for i in range(1,7):
            prime_button = tk.Button(self.pump_frame, text=f"Prime {i}", command=lambda num=i: self.prime_pump(num))
            prime_button.grid(row = i-1, column = 0, padx = 10, sticky = 'w')

            purge_button = tk.Button(self.pump_frame, text=f"Purge {i}", command=lambda num=i: self.toggle_purge_pump(num))
            purge_button.grid(row = i-1, column = 1, padx = 10, sticky = 'w')

        # Set up Stepper Motor Control tab
        print("Set up stepper motor tab")
        self.stepper_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.stepper_frame, text = 'Stepper Motor Control')

        print("create status labels for stepper motor direction")
        # Create status label for stepper motor direction
        self.status_label = tk.Label(self.stepper_frame, text="Direction: STOPPED")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky='w')

        print("create buttons for stepper motor control")
        # Create buttons for stepper motor control in the stepper frame
        self.stepper_direction_button = tk.Button(self.stepper_frame, text = "Toggle Stepper Direction", command=self.toggle_stepper_direction, state="disabled")
        self.stepper_direction_button.grid(row=2, column=0, columnspan=2, sticky='w')
        self.stepper_enable_button = tk.Button(self.stepper_frame, text="Toggle Stepper Enable", command=self.toggle_stepper_motor, state="normal")
        self.stepper_enable_button.grid(row = 0, column = 0, columnspan = 2, sticky = 'w')
        self.stepper_move_button = tk.Button(self.stepper_frame, text = "Move Stepper", command = self.move_stepper_motor, state = "normal")
        self.stepper_move_button.grid(row=6, column=0, columnspan=2, sticky='w')

        print("Create an exit button")
        # Create an exit button in stepper frame
        self.exit_stepper_button = tk.Button(self.stepper_frame, text="Exit", command=self.app.exit_program)
        self.exit_stepper_button.grid(row=7, column=0, columnspan=2, sticky='w')

        print("Create step rate label")
        # Create step rate label
        self.step_rate_label = tk.Label(self.stepper_frame, text = "Step rate (ms):")
        self.step_rate_label.grid(row=3, column=0, columnspan=2, sticky='w') # Place label in the grid

        print("Create combobox widget")
        # Create a Combobox widget for step rate selection
        self.step_rate_combobox = ttk.Combobox(self.stepper_frame, values = [str(i) for i in range(1,11)], state="normal")
        self.step_rate_combobox.set(str(self.step_rate))
        self.step_rate_combobox.grid(row=4, column=0, columnspan=2, sticky='w') # Place the combobox in the grid

        print("Create step rate button")
        # Create step rate button
        self.step_rate_button = tk.Button(self.stepper_frame, text = "Set Step Rate", command = self.change_step_rate, state = "normal")
        self.step_rate_button.grid(row=5, column=0, columnspan=2, sticky='w')

        print("Finished setting up ui for current mode")

class MixerOptions:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.mixer_options = ["Soda Water", "Tonic Water", "Coke", "Orange Juice", "Pineapple Juice", "Marg Mix"]
        self.mixer_buttons = {}

        self.setup_ui()

    def setup_ui(self):
        # Create the tab for Mixer Options
        mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(mode_tab, text="Mixer Options")

        # Create buttons for each mixer option in the mixer options tab
        for option in self.mixer_options:
            mixer_button = tk.Button(mode_tab, text=option, state="normal", bg="red")
            mixer_button.pack()
            self.mixer_buttons.append(mixer_button)

            # Bind single-click to toggle red color, and double-click to toggle green color
            mixer_button.bind("<Button-1>", lambda event, button=mixer_button: self.toggle_opion_color(button))
            mixer_button.bind("<Double-1>", lambda event, button=mixer_button: self.toggle_option_color(button))

class BottleOptions:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.bottle_options = ["Vodka", "Rum", "White Rum", "Tequila", "Gin", "Whiskey", "Triple Sec", "Surpuss", "Peach Schnapps", "Amaretto", "Chambord", "Lemoncello", "Grenadine"]
        self.bottle_buttons = {}

        self.bottle_relay_mapping = {}

        self.setup_ui()

    def toggle_option_color(self, option):
        label, _ = self.bottle_buttons[option]
        if label.cget("bg") == "red":
            label.config(bg="green")
        else:
            label.config(bg="red")

    def assign_bottle_to_relay(self, option, relay_number, label):
        if relay_number == 0:
            for i in range(1, len(self.bottle_options) + 1):
                bottle_relay_

    def setup_ui(self):
        # Create the tab for Bottle options
        mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(mode_tab, text = "Bottle Options")

        # Create buttons for each mixer option in the mixer options tab


##### SETUP THE GUI

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Control Panel")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill = 'both', expand = True)

        self.relay_pins = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
        self.pump_channels = [12, 16, 20, 21, 22, 27]
        self.step_pin = 23
        self.dir_pin = 18
        self.enable_pin = 24

        # Pump function values
        #self.pump_photo = PhotoImage(file = "~/Desktop/MarkedObjectsIconRollover.png")

    # GPIO setup
    def initialize_gpio(self):
        #GPIO.setmode(GPIO.BCM)
        self.setup_pins()

    def initialize_gui(self):
        print("create modes")
        self.create_modes()

    def setup_pins(self):
        for pin in self.pump_channels + self.relay_pins + [self.enable_pin]:
            print("GPIO.setup(pin, GPIO.OUT)")
            print("GPIO.output(pin, GPIO.LOW)")

        for pin in self.step_pin + self.dir_pin:
            print("GPIO.setup(pin, GPIO.OUT)")

    def create_modes(self):
        modes = ["Test Mode", "Bar Mode", "Mixer Options", "Bottle Options"]

        print("setting up test mode")
        # Set up Test and Bar Mode
        test_mode = ModeControl(self, "Test Mode")
        print("setting up bar mode")
        bar_mode = ModeControl(self, "Bar Mode")

        print("setting up uis for test mode")
        test_mode.setup_ui()
        print("setting up ui for bar mode")
        bar_mode.setup_ui()

        #for mode_name in modes:
        #    if mode_name in ["Test Mode", "Bar Mode"]:
        #        ModeControl(self, mode_name)

        exit_button = tk.Button(self.root, text="Exit", command=lambda: self.exit_program)        
        exit_button.grid(row = len(self.relay_pins) + 1, column = 0, columnspan = 2, sticky = 'w')

    def exit_program(self):
        print("GPIO.cleanup()")
        self.root.destroy()

if __name__ == "__main__":
    # Initialize app
    app = App()
    print("initialize_gui")
    app.initialize_gui()
    print("finished initializing gui for app")
    app.root.mainloop()

