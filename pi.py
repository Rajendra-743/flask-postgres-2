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
IR_SENSOR_PINS = [22,27]
GPIO.setup(IR_SENSOR_PINS, GPIO.IN)

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

def read_ir_sensor(pin): 
    return GPIO.input(pin)

# #Fungsi untuk mengirim data sensor IR ke server
# def send_ir_sensor_data():  
#     ir_data = {}
#     for i, pin in enumerate(IR_SENSOR_PINS):
#         ir_data[f"ir_sensor_{i+1}"] = read_ir_sensor(pin)

#Menentukan Ukuran Botol
def determine_bottle_size(ir_readings):
    num_detected = sum(ir_readings)

    if num_detected == 1:
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
            ir_readings = [read_ir_sensor(pin) for pin in IR_SENSOR_PINS]
            bottle_size = determine_bottle_size(ir_readings)
            print("Detected Bottle Size:", bottle_size)
            sio.emit('bottle_size', {'size': bottle_size})
            time.sleep(1)
    except Exception as e:
        logger.error("Koneksi ke server Flask gagal: %s", str(e))
    finally:    
        GPIO.cleanup()
