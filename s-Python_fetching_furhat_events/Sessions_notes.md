# Session notes

# Settup

Create
```bash
python3 -m venv venv
```

Activate
```bash
source venv/bin/activate
```

Install
```bash
pip install numpy scipy os matplotlib numpy pyserial PySide6
```

Deactivate
```bash
deactivate
```

To run it
```
python3 myApp.py
```

# Real-Time Audio-Serial MV Architecture

This table explains the separation of concerns for implementing real-time serial communication within the Model-View-Controller (MVC) pattern used in the PySide6 application.

| Component | Responsibility | New Feature Implementation |
| :--- | :--- | :--- |
| **Model** (`AppModel`) | Manages application state, data, and business logic, **including external resources**. | Now manages the **Serial Connection object** (`pyserial.Serial`). It handles listing available ports (`get_available_ports`), establishing the connection (`connect_serial`/`disconnect_serial`), and the low-level data transmission (`send_data`). |
| **View** (`AudioIntensityCanvas`) | Handles presentation and visualization. | No change to the visualization logic, as it only consumes the intensity data (normalized value) provided by the Controller/timer loop. |
| **Controller** (`MainWindow` methods) | Handles user input and orchestration. | Populates the `QComboBox` with ports provided by the Model. On port selection, it tells the Model to establish a connection (`handle_dropdown_change`). In the live loop (`update_live_bar`), it takes the calculated `normalized_value` and asks the Model to **send that data** over the active connection. |

# Refs

Metadata:
npc-arnold-greetings
    date            : 2024
    genre           : Sound Effect
    artist          : SoundBiter
    comment         : Discover more sound effects at www.voicebosch.com/soundbiter


# Session notes Oct 31 - 2025

An example of the output
```bash
python3 web_socket_client.py
Connected and stored persistent WebSocket client.
Waiting 0.1 second...
Updating data point (0, 0)
GUI Render Loop (50ms): Polling Latest Data L/R: (0, 0)

Updating data point (0, 0)
GUI Render Loop (50ms): Polling Latest Data L/R: (0, 0)

Starting 0.05 data reception burst using loop.create_task()...
Emptying queue!
Queue data point: (11043, 11043)
Emptying queue!
Queue data point: (6083, 6083)
Emptying queue!
.
.
Emptying queue!
Queue data point: (-27893, -27893)
Updating data point (-27893, -27893)
GUI Render Loop (50ms): Polling Latest Data L/R: (-27893, -27893)

Emptying queue!
Queue data point: (-29376, -29376)
.
.
Emptying queue!
Queue data point: (-23115, -23115)
Listener: Task received cancellation signal.
Finished data test (Tasks stopped).
Disconnected WebSocket client.
```