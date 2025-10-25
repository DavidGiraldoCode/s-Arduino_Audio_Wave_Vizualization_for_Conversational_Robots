# python3 matplotlib_button_state_example.py
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import random

# Global state variable (like a simple data model)
# We use a mutable list/array to allow the function to change the state
# In Python, this is often simpler than using the 'global' keyword.
#current_color = ['red','blue'] 
colors = ['red','blue'] 
current_color = colors[0];
#current_state = ['OFF']
states = ['OFF']
current_state = ['OFF']

# -------------------------------
# 1. Setup Figure and Initial Elements (The View)
# -------------------------------
# Create the figure (the window) and the axes (the drawing area)
fig, ax = plt.subplots(figsize=(6, 4))
plt.subplots_adjust(bottom=0.25) # Make space at the bottom for the button

# Hide the standard axes lines and ticks for a cleaner GUI look
ax.axis('off')

# Add a text element, which we will modify when the button is pressed.
status_text = ax.text(
    0.5, 0.7, # Position (normalized from 0 to 1)
    f"Status: {current_state[0]}", 
    fontsize=24, 
    #color=current_color[0], 
    color=current_color, 
    ha='center', 
    va='center'
)

# -------------------------------
# 2. Define the Event Handler / Callback
# -------------------------------
# This function defines the application's core logic: how to react to the button event.
def toggle_state(event):
    """
    Toggles the internal state and updates the status_text object.
    This function is executed ONLY when the button is clicked.
    """
    # Mutate the global state based on the current value
    if current_state[0] == 'OFF':
        current_state[0] = 'ON'
        current_color = colors[1]
        #current_color[0] = 'green'
    else:
        current_state[0] = 'OFF'
        current_color = colors[0]
        #current_color[0] = 'red'

    # Update the visual element (The Text)
    status_text.set_text(f"Status: {current_state[0]}")
    status_text.set_color(current_color)
    
    # 3. Force a redraw of the canvas to see the change immediately
    # Without this, the change wouldn't appear until the next system event.
    fig.canvas.draw_idle() 
    
    # Update the button's text label as well
    if current_state[0] == 'ON':
        btn_control.label.set_text("Turn OFF")
    else:
        btn_control.label.set_text("Turn ON")
    
    print(f"State changed to: {current_state[0]}")


# -------------------------------
# 3. Setup the Button and Hook the Event
# -------------------------------
# Define the area (axes) where the button will sit: [left, bottom, width, height] (normalized)
ax_button = plt.axes([0.35, 0.08, 0.3, 0.1])
btn_control = Button(ax_button, "Turn ON", color='#DDDDDD', hovercolor='lightblue')

# Hook the event: When the button is clicked, call the toggle_state function.
# This is the key to event-driven programming in matplotlib.
btn_control.on_clicked(toggle_state)


# -------------------------------
# 4. Start the Application Loop
# -------------------------------
# plt.show() starts the internal, blocking event loop of the GUI backend.
# This keeps the window open and continuously listens for mouse clicks and other OS events.
plt.show() 

print("\nApplication closed.")