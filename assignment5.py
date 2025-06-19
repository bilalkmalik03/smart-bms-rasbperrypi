# import necessary libraries for hardware control, http, and threading  
from gpiozero import LED, Button, MotionSensor  # for gpio devices
from Freenove_DHT import DHT                   # for dht11 sensor readings
from LCD1602 import CharLCD1602                 # for lcd display
from collections import deque                   # for averaging temperature
from threading import Thread                    # for running parallel processes
import time                                     # time delays
import requests                                 # for api calls
from datetime import datetime                   # for logging timestamps
import os
from dotenv import load_dotenv
load_dotenv()

# ----------------------------
# gpio pin configuration
# ----------------------------
blue_button = Button(25)       # button to increase desired temperature
red_button = Button(18)        # button to decrease desired temperature
door_button = Button(27)       # button to simulate door/window toggle

blue_led = LED(5)              # cooling system led
red_led = LED(6)               # heating system led
green_led = LED(12)            # ambient light (motion-activated) led
pir = MotionSensor(17)         # pir motion sensor

dht_sensor = DHT(4)            # dht11 sensor for temperature
lcd = CharLCD1602()            # lcd1602 display object
lcd.init_lcd(addr=None, bl=1)  # initialize lcd with backlight

# ----------------------------
# globals and states
# ----------------------------
temperature_readings = deque(maxlen=3)  # rolling list of last 3 temperatures
desired_temp = 72                       # initial desired temperature
ambient_light_on = False               # tracks ambient light status
door_open = False                      # tracks door/window state
last_motion_time = 0                   # time of last detected motion
fire_alarm_active = False              # fire alarm trigger flag
hvac_state = "OFF"                     # tracks current hvac status

# ----------------------------
# logging
# ----------------------------
def log_event(message):
    # appends a timestamped event to log.txt
    now = datetime.now().strftime('%H:%M:%S')
    with open("log.txt", "a") as f:
        f.write(f"{now} {message}\n")

# ----------------------------
# initialization
# ----------------------------
def initialize_system():
    # prepares system at startup by clearing lcd, turning off leds, and binding button actions
    lcd.clear()
    lcd.write(0, 0, "BMS Initializing")
    red_led.off()
    blue_led.off()
    green_led.off()
    time.sleep(2)
    lcd.clear()
    lcd.write(0, 0, "System Ready")
    time.sleep(2)
    lcd.clear()

    # assign button actions to temperature control and door toggle
    blue_button.when_pressed = increase_desired_temp
    red_button.when_pressed = decrease_desired_temp
    door_button.when_pressed = toggle_door_state

# ----------------------------
# motion detection thread
# ----------------------------
def motion_monitor():
    # monitors pir sensor to toggle ambient light and logs motion activity
    global ambient_light_on, last_motion_time
    while True:
        if not fire_alarm_active:
            if pir.motion_detected:
                if not ambient_light_on:
                    green_led.on()
                    ambient_light_on = True
                    log_event("LIGHTS ON")
                last_motion_time = time.time()
            elif ambient_light_on and (time.time() - last_motion_time > 10):
                green_led.off()
                ambient_light_on = False
                log_event("LIGHTS OFF")
        time.sleep(0.2)

# ----------------------------
# fire alarm thread
# ----------------------------
def fire_alarm_loop():
    # displays fire alert and flashes leds while alarm is active
    while True:
        if fire_alarm_active:
            green_led.toggle()
            red_led.toggle()
            blue_led.toggle()
            lcd.clear()
            lcd.write(0, 0, "!!! FIRE ALERT !!!")
            lcd.write(0, 1, "DOOR: OPEN - EVAC")
        time.sleep(1)

# ----------------------------
# door/window handler
# ----------------------------
def toggle_door_state():
    # toggles simulated door/window state and updates lcd/hvac
    global door_open, hvac_state
    door_open = not door_open

    lcd.clear()
    if door_open:
        lcd.write(0, 0, "DOOR: OPEN")
        lcd.write(0, 1, f"HVAC: {hvac_state}")
        red_led.off()
        blue_led.off()
        log_event("DOOR OPEN")
        log_event("HVAC OFF")
    else:
        lcd.write(0, 0, "DOOR: CLOSED")
        lcd.write(0, 1, f"HVAC: {hvac_state}")
        log_event("DOOR CLOSED")

    # display door status message temporarily then clear lcd
    time.sleep(3)
    lcd.clear()

# ----------------------------
# temperature sensor
# ----------------------------
def get_average_temperature():
    # reads dht sensor and averages last 3 temperature values
    chk = dht_sensor.readDHT11()
    if chk == 0:
        temp_c = dht_sensor.getTemperature()
        temp_f = temp_c * 9 / 5 + 32
        temperature_readings.append(temp_f)

        # return average when 3 readings are available
        if len(temperature_readings) == 3:
            return round(sum(temperature_readings) / 3)
    return None

# ----------------------------
# humidity via api
# ----------------------------
def get_humidity():
    # retrieves humidity from openweathermap api (fallback to 55%)
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        city = "Irvine"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()['main']['humidity']
    except:
        pass
    return 55

# ----------------------------
# temperature adjustment
# ----------------------------
def increase_desired_temp():
    # raises the desired temperature by 1 degree (max 99)
    global desired_temp
    if desired_temp < 99:
        desired_temp += 1

def decrease_desired_temp():
    # lowers the desired temperature by 1 degree (min 65)
    global desired_temp
    if desired_temp > 65:
        desired_temp -= 1

# ----------------------------
# hvac main loop
# ----------------------------
def monitor_environment():
    # monitors temperature and humidity, updates lcd and controls hvac system
    global fire_alarm_active, door_open, hvac_state
    humidity = get_humidity()
    hvac_state = "OFF"

    while True:
        avg_temp = get_average_temperature()
        if avg_temp is not None:
            wi = round(avg_temp + 0.05 * humidity)  # weather index = temp + 0.05*humidity

            # trigger fire alarm if wi exceeds 90
            if wi > 90:
                if not fire_alarm_active:
                    fire_alarm_active = True
                    door_open = True
                    red_led.off()
                    blue_led.off()
                    log_event("FIRE ALARM ON")
                    log_event("HVAC OFF")
            elif fire_alarm_active and wi <= 90:
                fire_alarm_active = False
                green_led.off()
                log_event("FIRE ALARM OFF")
                lcd.clear()
                lcd.write(0, 0, "Fire Over")
                lcd.write(0, 1, "Resuming...")
                time.sleep(3)

            # if not in fire alarm state, display system status and control hvac
            if not fire_alarm_active:
                lcd.clear()
                lcd.write(0, 0, f"WI:{wi} T:{avg_temp} H:{hvac_state}")  # top line with wi, temp, hvac
                lcd.write(0, 1, f"Set:{desired_temp} L:{'ON' if ambient_light_on else 'OFF'} D:{'OPEN' if door_open else 'CLOSED'}")  # bottom line with setpoint, light, and door

                prev_state = hvac_state

                # determine hvac action based on wi and desired temp
                if door_open:
                    hvac_state = "OFF"
                    red_led.off()
                    blue_led.off()
                elif wi < desired_temp - 3:
                    hvac_state = "HEAT"
                    red_led.on()
                    blue_led.off()
                elif wi > desired_temp + 3:
                    hvac_state = "AC"
                    blue_led.on()
                    red_led.off()
                else:
                    hvac_state = "OFF"
                    red_led.off()
                    blue_led.off()

                # log any change in hvac state
                if hvac_state != prev_state:
                    log_event(f"HVAC {hvac_state}")

        time.sleep(1)

# ----------------------------
# start program
# ----------------------------
if __name__ == '__main__':
    try:
        initialize_system()  # show startup message and bind buttons
        Thread(target=motion_monitor, daemon=True).start()   # motion detection thread
        Thread(target=fire_alarm_loop, daemon=True).start()  # fire alert display thread
        monitor_environment()  # run hvac and display loop
    except KeyboardInterrupt:
        # on ctrl+c shutdown: clear lcd and turn off all leds
        lcd.clear()
        red_led.off()
        blue_led.off()
        green_led.off()
        print("System stopped.")
