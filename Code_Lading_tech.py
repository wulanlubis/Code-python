import time
import requests
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT

import RPi.GPIO as GPIO
from hx711 import HX711
# Import the required libraries
from twilio.rest import Client
#import simpleaudio as sa

# gpio 27 untuk sensor PIR
# gpio 16 untuk buzzer
# gpio 20,21 untuk relay



# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# DHT11 configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17

BUZZER_PIN = 16
RELAY1_PIN = 20
RELAY2_PIN = 21
PIR_PIN    = 27


# Setup GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

GPIO.setup(RELAY1_PIN, GPIO.OUT)
GPIO.setup(RELAY2_PIN, GPIO.OUT)

GPIO.output(RELAY1_PIN, GPIO.LOW)
GPIO.output(RELAY2_PIN, GPIO.LOW)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
HX711_DT  = 24
HX711_SCK = 23

# Create an HX711 object
hx = HX711(dout_pin=HX711_DT, pd_sck_pin=HX711_SCK)
hx.zero()

input ('silahkan letakkan beban diatas timbangan & enter:')
reading = hx.get_data_mean(readings=98)

known_weight_grams = input('masukkan nilai berat benda yang diatas timbangan dan enter:')
value = int(known_weight_grams)

ratio = reading/value
hx.set_scale_ratio(ratio)

# Load the warning sound
#wave_obj = sa.WaveObject.from_wave_file('warning_sound.wav')  # Replace 'warning_sound.wav' with your sound file

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC6eff7391b010b05a6bc90f6017036b8e'
TWILIO_AUTH_TOKEN = 'a0aa2a0445e8281366ce9a0fb1dbad99'
TWILIO_PHONE_NUMBER = '+17076575322'

# Define Telegram API parameters
TELEGRAM_TOKEN = "6380534191:AAEax94VpQdJHyLBnejMPlP8ZbpxHPD_3yY"
CHAT_ID = "729173950"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_to_telegram(message):
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(TELEGRAM_URL, json=payload)
    print("Telegram Response:", response.status_code)

# Function to send SMS using Twilio
def send_sms(to, message):
    twilio_client.messages.create(
        to=to,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )
def waktu_tunda():
    while waktu_timer > 0:
        mins, secs = divmod(waktu_timer, 60)
        waktu = f'{mins:02d}:{secs:02d}'
        print(f'Waktu tersisa: {waktu}', end='\r')
        time.sleep(1)
        waktu_timer -= 1

try:
    while True:
        #no hp dan pesan utk dikirim melalui sms
        recipient_phone = '+6282370193130'
        sms_message = 'Telah terjadi kebakaran di lokasi berikut: https://goo.gl/maps/GocYC3mUgpmChdmF7'
        # Read the weight
        weight = hx.get_weight_mean(5)  # Read 5 times and calculate the average
         
        # Read the MCP3008 value from all channel
        mcp_value1 = mcp.read_adc(0)
        mcp_value2 = mcp.read_adc(1)
        mcp_value3 = mcp.read_adc(2)
        mcp_value4 = mcp.read_adc(3)
        # batas nilai flame sensor
        mcp_value5 = mcp.read_adc(4)
        #batas nilai sensor mq5
        mcp_value6 = mcp.read_adc(5)
        mcp_value7 = mcp.read_adc(6)
        mcp_value8 = mcp.read_adc(7)
        
        avrgFlame = (mcp_value1 + mcp_value2 + mcp_value3 + mcp_value4) / 4
        # Read the DHT11 sensor value
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        # Read the PIR sensor value
        pir_value = GPIO.input(PIR_PIN)
        
        
        if avrgFlame > 400:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
            GPIO.output(RELAY1_PIN, GPIO.HIGH)  # Turn on the RELAY
            GPIO.output(RELAY2_PIN, GPIO.HIGH)
            #play_obj = wave_obj.play()  # Play the warning sound
            #play_obj.wait_done()  # Wait for sound to finish playing
            #send_sms(recipient_phone, sms_message) 
            
        elif mcp_value5 > 300:
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
            GPIO.output(RELAY1_PIN, GPIO.HIGH)  # Turn on the RELAY
            GPIO.output(RELAY2_PIN, GPIO.HIGH)
#             time.sleep(5)
            send_to_telegram("Bahaya...Tabung Gas Bocor")
            
        elif pir_value == GPIO.HIGH:
            waktu_timer = 3 * 60
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn on the buzzer
            send_to_telegram("Mohon periksa kompor")
            waktu_tunda()
        else:
            #play_obj.wait_done()
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off the buzzer
        
            GPIO.output(RELAY1_PIN, GPIO.LOW)
            GPIO.output(RELAY2_PIN, GPIO.LOW)
            
            waktu = 0
            waktu_timer = 0
            
        # Print the values
        print('Flame Sensor: {}'.format(avrgFlame))
        print('MQ5   Sensor: {}'.format(mcp_value5))
        print('PIR   Sensor: {}'.format(pir_value))
        print('HX711 Weight: {:.0f} grams'.format(weight))
        
        
        if humidity is not None and temperature is not None:
            print('DHT11 Temperature: {:.2f}°C, Humidity: {:.2f}%'.format(temperature, humidity))
        else:
            print('Failed to read DHT11 sensor data.')
#=====================================================================================================            
        # Send data to Ubidots
        ubidots_token = 'BBFF-83AwrJd4MHdXXQcJuZOWdkjawnNC10'
        device_label = 'ladingtech'
        
        payload = {
            'flame'	: avrgFlame,
            'gas'	: mcp_value5,
            'pir'	: pir_value,
            'weight': ('{:.0f}'.format(weight)),
            'Suhu'	: temperature,
            'lembab': humidity
        }
        
        headers = {
            'X-Auth-Token': ubidots_token,
            'Content-Type': 'application/json'
        }
        
        url = f'https://industrial.api.ubidots.com/api/v1.6/devices/{device_label}'


        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            print("Data sent to Ubidots successfully!")
        else:
            print("Error sending data to Ubidots")
            
        time.sleep(0.5)  # Add a delay to control the reading frequency

except KeyboardInterrupt:
    print("Exiting the program")

finally:
    print("Cleanup")

