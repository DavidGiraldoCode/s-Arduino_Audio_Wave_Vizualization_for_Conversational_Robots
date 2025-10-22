# Arduino Audio Wave Vizualization for Conversational Robots

This repository has simple examples showing how Arduino C++ code communicates with Java Processing code to visualize audio waves. Currently, it only displays a sine wave created in Processing.

This program controls an LED array based on data received through the serial port. The Java Processing application sends integers from 0 to 255. These numbers represent the state of a Furhat robot, indicating when the robot is listening ('A') or speaking (values from 0 to 255). The Arduino processes these inputs accordingly.

![circuit](s_HRI_audio_wave_circuit.png)

## Bill of materials

| Name         | Quantity | Component                     |
|---------------|-----------|-------------------------------|
| U1            | 1         | Arduino Uno R3                |
| D1, D2, D3, D4, D5, D6 | 6 | Red LED                      |
| R1, R2, R3, R4 | 4        | 220 Ω Resistor                |
| S1            | 1         | Pushbutton                    |
| R5, R6        | 2         | 10 kΩ Resistor                |
| PIEZO1        | 1         | Piezo                         |
| T1            | 1         | NPN Transistor (BJT)          |


## TODO:
- [ ] Read an audio filke encoded as signed, 16 bit, little-endian linear PCM format, 16KHz, stereo (same format as WAV-files are encoded).
    - [ ] Upload and play the audio in Processing
    - [ ] Send the samples to Arduino
    - [ ] Visualized the data