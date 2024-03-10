#import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import PhotoImage

##### SETUP THE GUI

class ModeControl:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        #self.relay_buttons = []
        #self.relay_menus = []

        self.image_labels = [None] * 6

        self.stepper_enabled = False
        self.stepper_direction = "GPIO.LOW"
        self.step_rate = 10


    def setup_ui(self):
        # Set up frames, subnotebooks and tabs
        # Mode tab
        self.mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.mode_tab, text=self.name)
        self.sub_notebook = ttk.Notebook(self.mode_tab)
        self.sub_notebook.pack(fill = 'both', expand = True)

        # Relay tab
        self.relay_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.relay_frame, text = 'Relay Control')

        # Pump Control tab
        self.pump_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.pump_frame, text = 'Pump Control')
        #self.image_label = tk.Label(self.pump_frame, image = self.app.pump_photo)

        # Stepper Motor Control tab
        self.stepper_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.stepper_frame, text = 'Stepper Motor Control')

        # Toggle all Relay Buttons
        all_relay_buttons = ttk.Button(
            self.relay_frame,
            text = "Toggle All Relays 1-8",
            command = self.toggle_all_relays
        )

        all_relay_buttons.grid(
            row = len(self.app.relay_pins),
            column = 0,
            columnspan = 2,
            sticky = 'w'
        )

        # Set up Momentary/Permanent drop down menus
        for i, pin in enumerate(reversed(self.app.relay_pins)):
            relay_button = ttk.Button(self.relay_frame, text = f"Relay {i + 1}")
            
            state_var = tk.StringVar()
            state_var.set("Momentary")

            state_menu = ttk.OptionMenu(self.relay_frame, state_var, "Momentary", "Permanent")

            relay_button.grid(row=i, column=0, sticky='w')
            state_menu.grid(row=i, column = 1, sticky = 'w')

            relay_button.config(command = lambda p=pin, s=state_var: self.toggle_relay(p,s))

            self.app.relay_buttons.append(relay_button)
            self.app.relay_menus.append(state_menu)

        # Set up pump buttons
        for i in range(1,7):
            prime_button = ttk.Button(self.pump_frame, text=f"Prime {i}", command=lambda num=i: self.prime_pump(num))
            prime_button.grid(row = i-1, column = 0, padx = 10, sticky = 'w')

            purge_button = ttk.Button(self.pump_frame, text=f"Purge {i}", command=lambda num=i: self.toggle_purge_pump(num))
            purge_button.grid(row = i-1, column = 1, padx = 10, sticky = 'w')

        # Set up stepper motor labels and buttons
        self.status_label = ttk.Label(self.stepper_frame, text="Direction: STOPPED")
        self.status_label.grid(row = 1, column = 0, columnspan = 2, sticky = 'w')
        
        self.stepper_direction_button = ttk.Button(self.stepper_frame, text = 'Toggle Stepper Direction', command = self.toggle_stepper_direction, state="disabled")
        self.stepper_direction_button.grid(row=2, column=0, columnspan=2, sticky='w')
        self.stepper_enable_button = ttk.Button(self.stepper_frame, text="Toggle Stepper Enable", command=self.toggle_stepper_motor, state="normal")
        self.stepper_enable_button.grid(row = 0, column = 0, columnspan = 2, sticky='w')
        self.stepper_move_button = ttk.Button(self.stepper_frame, text = "Move Stepper", command = self.move_stepper_motor, state = "normal")
        self.stepper_move_button.grid(row=6, column=0, columnspan=2, sticky='w')

        # Create an exit button in stepper frame
        ### TODO
        self.exit_stepper_button = ttk.Button(self.stepper_frame, text = "Exit", command = self.app.exit_program)
        self.exit_stepper_button.grid(row=7, column=0, columnspan=2, sticky='w')

        # Create step rate label
        self.step_rate_label = ttk.Label(self.stepper_frame, text = f"Step rate (ms): {self.step_rate}")
        self.step_rate_label.grid(row=3, column=0, columnspan=2, sticky='w')

        # Create a Combobox widget for step rate selection
        self.step_rate_combobox = ttk.Combobox(self.stepper_frame, values = [str(i) for i in range(1,11)], state="normal")
        self.step_rate_combobox.set(str(self.step_rate))
        self.step_rate_combobox.grid(row=4, column=0, columnspan=2, sticky='w')

        # Create step rate button
        self.step_rate_button = ttk.Button(self.stepper_frame, text = "Set Step Rate", command = self.change_step_rate, state="normal")
        self.step_rate_button.grid(row=5, column = 0, columnspan = 2, sticky = 'w')

    # Relay functions

    def toggle_all_relays(self):
        for pin in self.app.relay_pins[:8]:
            print(f"GPIO.output({pin}, not GPIO.input({pin})")

    def toggle_relay(self, pin, state_var):
        if state_var.get() == "Momentary":
            print(f"GPIO.output({pin}, GPIO.HIGH")
            self.app.root.after(100, lambda p=pin: print(f"GPIO.output({p}, GPIO.LOW"))
        else:
            print(f"GPIO.output({pin}, not GPIO.input({pin})")

    # Img function

    # TODO update
    def update_image_visibility(self):
        active_pumps = [i + 1 for i, channel in enumerate(self.app.pump_channels)]

        for i in range(6):
            if self.image_labels[i]:
                self.image_labels[i].grid_forget()

        # Create image labels next to active buttons
        for pump_number in active_pumps:
            image_label = tk.Label(self.pump_frame)
            image_label.grid(row = pump_number - 1, column = 2)
            self.image_labels[pump_number - 1] = image_label

    # Pump functions

    def prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        print(f"GPIO.output({channel}, GPIO.HIGH")
        self.update_image_visibility()
        self.app.root.after(3000, lambda: self.stop_prime_pump(pump_number))

    def stop_prime_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        print(f"GPIO.output({channel}, GPIO.LOW")
        self.update_image_visibility()

    def toggle_purge_pump(self, pump_number):
        channel = self.app.pump_channels[pump_number - 1]
        # GPIO stuff
        self.update_image_visibility()

    # Stepper Motor Functions

    def update_status_label(self):
        if self.stepper_direction == "GPIO.LOW":
            self.status_label.config(text="Direction: Right")
        else:
            self.status_label.config(text="Direction: Left")

    def toggle_stepper_direction(self):
        if self.stepper_enabled:
            stepper_direction_dict = {"GPIO.LOW": "GPIO.HIGH", "GPIO.HIGH":"GPIO.LOW"}
            self.stepper_direction = stepper_direction_dict[self.stepper_direction]
            print(f"GPIO.output({self.app.dir_pin, self.stepper_direction})")
            self.update_status_label()

    def toggle_stepper_motor(self):
        if self.stepper_enabled:
            print(f"GPIO.output({self.app.enable_pin}, GPIO.HIGH")
            self.stepper_enabled = False
            self.stepper_direction_button.config(state="disabled")
            self.step_rate_combobox.config(state="disabled")
            self.stepper_move_button.config(state="disabled")
            self.update_status_label()
        else:
            print(f"GPIO.output({self.app.enable_pin}, GPIO.LOW")
            self.stepper_enabled = True
            self.stepper_direction_button.config(state="normal")
            self.step_rate_combobox.config(state="normal")
            self.step_rate_button.config(state="normal")
            self.stepper_move_button.config(state="normal")
            self.update_status_label()

    def move_stepper_motor(self):
        if self.stepper_enabled:
            print(f"GPIO.output({self.app.step_pin}, GPIO.HIGH")
            self.app.root.after(self.step_rate, self.move_stepper_motor)
            print(f"GPIO.output({self.app.step_pin}, GPIO.LOW")

    def update_rate_label(self):
        self.step_rate_label.config(text = f"Step rate (ms): {self.step_rate}")

    def change_step_rate(self):
        if self.stepper_enabled:
            self.step_rate = int(self.step_rate_combobox.get())
            self.update_rate_label()

    def setup(self):
        self.setup_ui()        

class MixerOptions:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.mixer_options = ["Soda Water", "Tonic Water", "Coke", "Orange Juice", "Pineapple Juice", "Marg Mix"]
        self.mixer_buttons = []

    def setup_ui(self):
        self.mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.mode_tab, text = self.name)

        # Create buttons for each mixer option in the mixer options tab
        for option in self.mixer_options:
            mixer_button = tk.Button(self.mode_tab, text=option, state="normal", bg="red")
            mixer_button.pack()
            self.mixer_buttons.append(mixer_button)

            # Bind single-click to toggle red color, and double-click to toggle green color
            mixer_button.bind("<Button-1>", lambda event, button=mixer_button: self.toggle_option_color(button))
            mixer_button.bind("<Double-1>", lambda event, button=mixer_button: self.toggle_option_color(button))

    def toggle_option_color(self, button):
        if button.cget("bg") == "red":
            button.config(bg="green")
        else:
            button.config(bg="red")

    def setup(self):
        self.setup_ui()

class BottleOptions:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.bottle_options = ["Vodka", "Rum", "White Rum", "Tequila", "Gin", "Whiskey", "Triple Sec", "Surpuss", "Peach Schnapps", "Amaretto", "Chambord", "Lemoncello", "Grenadine"]
        self.bottle_buttons = {}

        self.bottle_relay_mapping = {}

    def toggle_option_color(self, option):
        label, _ = self.bottle_buttons[option]
        if label.cget("bg") == "red":
            label.config(bg="green")
        else:
            label.config(bg="red")

    def update_relay_names(self):
        for i, relay_button in enumerate(self.app.relay_buttons[:8]):
            option = self.bottle_relay_mapping.get(i + 1, f"Relay: {i + 1}")
            relay_button.config(text=option)

    def assign_bottle_to_relay(self, option, relay_number, label):
        if relay_number == 0:
            for i in range(1, len(self.bottle_options) + 1):
                self.bottle_relay_mapping[i] = f"Relay {i}"
        else:
            self.bottle_relay_mapping[relay_number] = option
        self.update_relay_names()

    def setup_ui(self):
        self.mode_tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.mode_tab, text = self.name)

        for option in self.bottle_options:
            bottle_frame = tk.Frame(self.mode_tab)
            bottle_frame.pack(fill='both')
            label = tk.Label(bottle_frame, text=option, width=20, bg="red")
            label.pack(side=tk.LEFT)

            # Make the label itself a button to toggle color
            label.bind("<Button-1>", lambda event, o=option: self.toggle_option_color(o))

            entry = tk.Entry(bottle_frame, width=3)
            entry.insert(0, "1")
            entry.pack(side=tk.LEFT)
            assign_button = tk.Button(bottle_frame, text="Assign", command=lambda o=option, e=entry, l=label: self.assign_bottle_to_relay(o, int(e.get()), l))
            assign_button.pack(side=tk.LEFT)
            self.bottle_buttons[option] = (label, assign_button)

    def setup(self):
        self.setup_ui()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Panel")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill = 'both', expand = True)

        self.relay_buttons = []
        self.relay_menus = []
        self.relay_pins = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15]
        self.pump_channels = [12, 16, 20, 21, 22, 27]
        self.step_pin = 23
        self.dir_pin = 18
        self.enable_pin = 24

        #self.pump_photo = PhotoImage("/home/JakeH/Pictures/pump.png")

        # TODO: this button doesn't show up
        self.exit_button = ttk.Button(self.root, text="Exit", command=self.exit_program)
        #self.exit_button.grid(row = len(self.relay_pins) + 1, column = 0, columnspan = 2, sticky = 'w')
        print(f"Pin settings: {self.relay_pins}, {self.pump_channels}, {self.step_pin}, {self.dir_pin}, {self.enable_pin}")

    def create_modes(self):
        
        ModeControl(self, "Test Mode").setup()
        ModeControl(self, "Bar Mode").setup()

        MixerOptions(self, "Mixer Options").setup()
        BottleOptions(self, "Bottle Options").setup()
        # Pump function values
        #self.pump_photo = PhotoImage(file = "~/Desktop/MarkedObjectsIconRollover.png")

    # GPIO setup
    def initialize_gpio(self):
        #GPIO.setmode(GPIO.BCM)
        self.setup_pins()

    def initialize_gui(self):
        self.create_modes()

    def setup_pins(self):
        for pin in self.pump_channels + self.relay_pins + [self.enable_pin]:
            print(f"GPIO.setup({pin}, GPIO.OUT)")
            print(f"GPIO.output({pin}, GPIO.LOW)")

        for pin in [self.step_pin, self.dir_pin]:
            print(f"GPIO.setup({pin}, GPIO.OUT)")

    #def create_modes(self):
    #    modes = ["Test Mode", "Bar Mode", "Mixer Options", "Bottle Options"]
#
    #    print("setting up test mode")
    #    # Set up Test and Bar Mode
    #    test_mode = ModeControl(self, "Test Mode")
    #    print("setting up bar mode")
    #    bar_mode = ModeControl(self, "Bar Mode")
#
    #    print("setting up uis for test mode")
    #    test_mode.setup_ui()
    #    print("setting up ui for bar mode")
    #    bar_mode.setup_ui()
#
    #    #for mode_name in modes:
    #    #    if mode_name in ["Test Mode", "Bar Mode"]:
    #    #        ModeControl(self, mode_name)
#
    #    exit_button = tk.Button(self.root, text="Exit", command=lambda: self.exit_program)        
    #    exit_button.grid(row = len(self.relay_pins) + 1, column = 0, columnspan = 2, sticky = 'w')

    def setup(self):
        self.initialize_gpio()
        self.initialize_gui()

    def exit_program(self):
        print("GPIO.cleanup()")
        #root.destroy()

if __name__ == "__main__":
    # Initialize app
    root = tk.Tk()
    app = App(root).setup()
    root.mainloop()

