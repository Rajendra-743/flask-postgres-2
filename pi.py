import RPi.GPIO as GPIO
import time
import socketio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#SERVO
SERVO_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setwarnings(False)
pwm = GPIO.PWM(SERVO_PIN, 50)

#UV SENSOR
UV_SENSOR_PINS = [18, 19, 20, 21, 22, 23]
GPIO.setup(UV_SENSOR_PINS, GPIO.IN)

#Fungsi untuk membuka palang tempat sampah
def open_bin():
    pwm.start(7.5)  
    time.sleep(1)   
    pwm.stop()      

#Fungsi untuk menutup palang tempat sampah
def close_bin():
    pwm.start(2.5)  
    time.sleep(1)   
    pwm.stop()      

def read_uv_sensor(pin):
    GPIO.setup(pin, GPIO.IN) 
    return GPIO.input(pin)

#Fungsi untuk mengirim data sensor UV ke server
def send_uv_sensor_data():
    uv_data = {}
    for i, pin in enumerate(UV_SENSOR_PINS):
        uv_data[f"uv_sensor_{i+1}"] = read_uv_sensor(pin)
    sio.emit('uv_sensor_data', uv_data)

#Menentukan Ukuran Botol
def determine_bottle_size(uv_readings):
    num_detected = sum(uv_readings)

    if num_detected == 2:
        return "Botol Kecil"
    elif num_detected == 4:
        return "Botol Sedang"
    elif num_detected == 6:
        return "Botol Besar"
    else:
        return "Ukuran botol tidak diketahui"


sio = socketio.Client()

@sio.on('open_bin')
def handle_open_bin():
    open_bin()
    logger.info("Palang tempat sampah terbuka.")

@sio.on('close_bin')
def handle_close_bin():
    close_bin()
    logger.info("Palang tempat sampah tertutup.")

@sio.on('message')
def handle_message(data):
    logger.info("Pesan dari server: %s", data['message'])

if __name__ == "__main__":
    try:
        sio.connect('http://192.168.30.113:5000')
        while True:
            uv_readings = [read_uv_sensor(pin) for pin in UV_SENSOR_PINS]
            bottle_size = determine_bottle_size(uv_readings)
            print("Detected Bottle Size:", bottle_size)
            sio.emit('bottle_size', {'size': bottle_size})
            time.sleep(1)
    except Exception as e:
        logger.error("Koneksi ke server Flask gagal: %s", str(e))
    finally:
        GPIO.cleanup()
