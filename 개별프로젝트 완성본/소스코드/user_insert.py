import time
import serial
import requests
import adafruit_fingerprint

uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

url = "http://127.0.0.1:1880/user_insert"


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
def enroll_finger():
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
        name = input('name >')
        fw = open('users.txt', 'w')
        users.append(name+'\n')
        fw.writelines(users)
        fw.close()
        print('user name Stored')

    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num(max_number):
    global location
    if location < max_number -1:
        location = location + 1


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates: ", finger.templates)
    if finger.count_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Number of templates found: ", finger.template_count)
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to get system parameters")
    print("finger library size: ", finger.library_size)
    print("e) enroll print")
    print("d) delete print")
    print("q) quit")
    print("----------------")
    c = input("> ")

    if c == "e":
        get_num(finger.library_size)
        enroll_finger()
    if c == "d":
        if location > 0:
            for i in range(location):
                print("{0}. {1}", i, users[i])
            ch = input('delete user number: ')
            if finger.delete_model(ch) == adafruit_fingerprint.OK:
                print("Deleted!")
            else:
                print("Failed to delete")
    if c == "q":
        print("Exiting fingerprint example program")
        raise SystemExit
