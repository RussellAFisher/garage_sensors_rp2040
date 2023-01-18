import time
import busio
import digitalio
import board
from adafruit_debouncer import Debouncer

# Import temp/humidity i2c sensor
import adafruit_sht4x
import adafruit_ahtx0

# Import LoRa Library
import adafruit_rfm9x

# Import pm2.5
from adafruit_pm25.i2c import PM25_I2C
pm2_reset_pin = None

# Delay between sending radio data, in seconds. 300 = 5 minutes
SENSOR_SEND_DELAY = 150

i2c = board.I2C()  # uses board.SCL and board.SDA
sht = adafruit_sht4x.SHT4x(i2c) # Garage sensor
aht = adafruit_ahtx0.AHTx0(i2c) # Outdoor sensor
pm25 = PM25_I2C(i2c, pm2_reset_pin)

# Define radio frequency, MUST match gateway frequency.
RADIO_FREQ_MHZ = 905.5

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D11)

# Set up garage door sensor
door_sensor = digitalio.DigitalInOut(board.D5)
door_sensor.direction = digitalio.Direction.INPUT
door_sensor.pull = digitalio.Pull.UP
garageOpen = False
previousGarageDoorState = False

# Set up rain gauge sensor
rain_gauge_pin = digitalio.DigitalInOut(board.A1)
rain_gauge_pin.direction = digitalio.Direction.INPUT
rain_gauge_pin.pull = digitalio.Pull.UP
rain_gauge = Debouncer(rain_gauge_pin)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Define the external garage sensor LED
garage_led = digitalio.DigitalInOut(board.D10)
garage_led.direction = digitalio.Direction.OUTPUT

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ)

# Set transmit power (5-23)
rfm9x.tx_power = 8

# sensor data
garage_sensor_data = bytearray(4)
garage_sensor_id = 1

outdoor_sensor_data = bytearray(4)
outdoor_sensor_id = 2

air_quality_data = bytearray(4)
air_quality_sensor_id = 3

garage_door_data = bytearray(2)
garage_door_id = 4

rain_gauge_data = bytearray(2)
rain_gauge_id = 5
rain_gauge_data[0] = rain_gauge_id

initialTime = time.monotonic()

print("Starting")

while True:
    now = time.monotonic()

    # Sensor data sends every SENSOR_SEND_DELAY, door state and rain gauge send immediately
    if now - initialTime > SENSOR_SEND_DELAY:
        garage_temperature, garage_relative_humidity = sht.measurements
        #print("Garage temperature: %0.1f C" % garage_temperature)
        #print("Garage humidity: %0.1f %%" % garage_relative_humidity)

        outdoor_temperature = aht.temperature
        outdoor_relative_humidity = aht.relative_humidity
        #print("Outdoor temperature: %0.1f C" % outdoor_temperature)
        #print("Outdoor humidity: %0.1f %%" % outdoor_relative_humidity)

        # GARAGE SENSOR
        garage_temp_rounded = round(garage_temperature)

        # Use data[3] as boolean indication of positive or negative temp
        if garage_temp_rounded >= 0:
            garage_sensor_data[3] = 0
        else:
            garage_sensor_data[3] = 1
            garage_temp_rounded = garage_temp_rounded * -1

        garage_sensor_data[0] = garage_sensor_id
        garage_sensor_data[1] = garage_temp_rounded
        garage_sensor_data[2] = round(garage_relative_humidity)
        #print('Sending garage data...')
        #print(garage_sensor_data)
        LED.value = True
        rfm9x.send(garage_sensor_data)
        #print('Sent data!')
        LED.value = False

        time.sleep(1)

        #print(outdoor_temperature)

        # OUTDOOR SENSOR
        outdoor_temp_rounded = round(outdoor_temperature)

        # Use data[3] as boolean indication of positive or negative temp
        if outdoor_temp_rounded >= 0:
            outdoor_sensor_data[3] = 0
        else:
            outdoor_sensor_data[3] = 1
            outdoor_temp_rounded = outdoor_temp_rounded * -1

        outdoor_sensor_data[0] = outdoor_sensor_id
        outdoor_sensor_data[1] = outdoor_temp_rounded
        outdoor_sensor_data[2] = round(outdoor_relative_humidity)
        #print('Sending outdoor data...')
        #print(outdoor_sensor_data)
        LED.value = True
        rfm9x.send(outdoor_sensor_data)
        #print('Sent data!')
        LED.value = False

        time.sleep(1)

        # pm2.5 sensor is squirrely, wrap to prevent system crash
        try:
            air_quality = pm25.read()
            air_quality_data[0] = air_quality_sensor_id
            air_quality_data[1] = air_quality["pm10 standard"]
            air_quality_data[2] = air_quality["pm25 standard"]
            air_quality_data[3] = air_quality["pm100 standard"]

            #print('Sending air quality data...')
            #print(air_quality_data)
            LED.value = True
            rfm9x.send(air_quality_data)
            #print('Sent data!')
            LED.value = False
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue


        initialTime = now

    if door_sensor.value:
        if not garageOpen:
            #print("GARAGE DOOR OPEN")
            garage_door_data[0] = garage_door_id
            garage_door_data[1] = 1
            #print('Sending data...')
            #print(garage_door_data)
            LED.value = True
            rfm9x.send(garage_door_data)
            #print('Sent data!')
            LED.value = False

            previousGarageDoorState = True
            garageOpen = True
            garage_led.value = True
    else:
        if previousGarageDoorState:
            #print("GARAGE DOOR CLOSED")
            garage_door_data[0] = garage_door_id
            garage_door_data[1] = 0
            #print('Sending data...')
            #print(garage_door_data)
            LED.value = True
            rfm9x.send(garage_door_data)
            #print('Sent data!')
            LED.value = False

            garageOpen = False
            garage_led.value = False
            previousGarageDoorState = False

    rain_gauge.update()

    if rain_gauge.rose:
        #print("Rain gauge bucket change")
        rain_gauge_data[1] = 1
        #print('Sending data...')
        #print(rain_gauge_data)
        LED.value = True
        rfm9x.send(rain_gauge_data)
        #print('Sent data!')
        LED.value = False

    if rain_gauge.fell:
        #print("Rain gauge bucket change")
        rain_gauge_data[1] = 1
        #print('Sending data...')
        #print(rain_gauge_data)
        LED.value = True
        rfm9x.send(rain_gauge_data)
        #print('Sent data!')
        LED.value = False

    time.sleep(1)
