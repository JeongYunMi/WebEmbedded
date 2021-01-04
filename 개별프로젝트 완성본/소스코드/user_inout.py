from time import sleep
import serial
import requests
from gpiozero import LED
import adafruit_fingerprint

uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

check_led = LED(17)

url = "http://127.0.0.1:1880/user_inout"

users = []
try:
    f = open('users.txt')
    for user in f.readlines():
        print("Registered user: ", user)
        users.append(user)
    location = len(users)
except:
    users = []
    location = 0

print("users: ", users)
print("location: ", location)


##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image... start")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False 
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False

    print("check: ", users[finger.finger_id-1])
    try:
        params = {'user_nick': users[finger.finger_id-1]}
        r = requests.post(url, data=params)
        print("##user check##\n\n")
        return True
    except RuntimeError as error:
        print(error.args[0])
        return False



    print("Waiting for image... end")
    return True

##################################################

while True:
    if get_fingerprint():
        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        check_led.on()
        sleep(2)
        check_led.off()
        sleep(2)
    else:
        print("Finger not found")
