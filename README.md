# Smart Building Management System using Raspberry Pi 5

This project implements a Smart Building Management System (BMS) on a Raspberry Pi 5 using Python and GPIO peripherals. It controls HVAC systems, detects motion, displays sensor data on an LCD, and provides fire alarm alerts based on temperature and humidity.

## Demo Video

[Watch the Demo on YouTube](https://YOUTUBE_LINK_HERE)

## Features

- **HVAC Control**: Automatically activates heating or cooling based on a calculated Weather Index (WI).
- **Fire Alarm**: Triggers emergency actions when WI exceeds a safety threshold.
- **Motion Detection**: Uses PIR sensor to control ambient lighting.
- **LCD Display**: Continuously shows temperature, HVAC status, motion, and door state.
- **Temperature Adjustment**: Users can increase/decrease the desired temperature using physical buttons.
- **Door/Window Simulation**: Physical button toggles simulated door state with automatic HVAC adjustment.
- **Logging**: Logs all key events with timestamps to `log.txt`.

## Hardware Components

- Raspberry Pi 5
- DHT11 Temperature/Humidity Sensor
- PIR Motion Sensor
- 3x LEDs (Red, Blue, Green)
- 3x Buttons (Increase Temp, Decrease Temp, Toggle Door)
- LCD1602 Display (I2C)
- Breadboard and jumper wires

## GPIO Pin Mapping

| Component       | GPIO Pin |
|----------------|----------|
| DHT11 Sensor    | GPIO4    |
| PIR Sensor      | GPIO17   |
| Blue Button     | GPIO25   |
| Red Button      | GPIO18   |
| Door Button     | GPIO27   |
| Blue LED (AC)   | GPIO5    |
| Red LED (Heat)  | GPIO6    |
| Green LED       | GPIO12   |

## Software

- Python 3
- `gpiozero` for GPIO control
- `Freenove_DHT` for DHT11 readings
- `LCD1602` for LCD display
- `requests` for weather API humidity
- `threading` for concurrent tasks

## Setup Instructions

1. Wire all components as per the GPIO map above.
2. Install required Python libraries:
   ```bash
   pip3 install gpiozero requests
   ```
   *(Make sure `Freenove_DHT.py` and `LCD1602.py` are in your project directory.)*
3. Run the main script:
   ```bash
   python3 assignment5.py
   ```

## Project Structure

- `assignment5.py` – Main program file
- `log.txt` – Event log with timestamps
- `Freenove_DHT.py` – DHT sensor module
- `LCD1602.py` – LCD display module
- `README.md` – Project overview

## Weather Index Formula

```
WI = Temperature (°F) + 0.05 × Humidity (%)
```

## Fire Alarm Logic

- Triggered if `WI > 90`
- Automatically opens door, turns off HVAC, flashes LEDs, and displays evacuation message
- Deactivates once `WI <= 90`

## License

This project is for academic demonstration purposes. Feel free to use or adapt the code with attribution.
