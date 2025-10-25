import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

# -------------------------------
# LOAD AUDIO
# -------------------------------
soundfile_path = "npc-arnold-greetings.wav"
data, samplerate = sf.read(soundfile_path)  # shape = (frames, channels)
num_frames, num_channels = data.shape
current_frame = 0
playing = False

# -------------------------------
# SETUP PLOT
# -------------------------------
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
ax.set_xlim(0, 200)
ax.set_ylim(0, 200)

circle = plt.Circle((100, 100), 50, color='red', alpha=0.6)
ax.add_patch(circle)

# -------------------------------
# BUTTON CALLBACK
# -------------------------------
def toggle_play(event):
    global playing, current_frame
    playing = not playing
    if playing:
        btn.label.set_text("Stop Audio")
    else:
        btn.label.set_text("Play Audio")
        current_frame = 0  # reset

ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])
btn = Button(ax_button, "Play Audio")
btn.on_clicked(toggle_play)

# -------------------------------
# UTILITY
# -------------------------------
def get_sample(frame_idx=0, channel=0):
    """Return normalized sample in [0,1]"""
    sample = data[frame_idx, channel]
    sample = (sample + 1.0) / 2.0
    return min(sample, 1.0)

# -------------------------------
# MAIN LOOP
# -------------------------------
plt.ion()
while True:
    if playing:
        sample = get_sample(current_frame)
        circle.radius = 50 + sample * 100  # radius changes with audio
        current_frame += 1
        if current_frame >= num_frames:
            playing = False
            btn.label.set_text("Play Audio")
            current_frame = 0
    fig.canvas.draw_idle()
    plt.pause(1 / samplerate)  # approximate real-time playback
