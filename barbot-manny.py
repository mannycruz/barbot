from barbot import toggle_all_relays
import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

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






if __name__ == "__main__":
    initialize_gpio()
    create_gui()



 





