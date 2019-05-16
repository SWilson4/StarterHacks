import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep
from fbchat import Client
from fbchat.models import *

dr_id = "" # doctor's Facebook profile id

# patient's Facebook login info
patient_email = ""
patient_password = ""
patient_first = ""
patient_last = ""

# dispense times for medication 1 in 24-hour format [hh, mm]
dispense_times_1 = [[11, 15], [11, 16], [11, 18], [11, 19]]

# dispense times for medication 2 in 24-hour format [hh, mm]
dispense_times_2 = [[11, 17], [11, 20], [11, 21], [11, 22], [11, 23]]

# number of pills in dispenser 1
pill_count_1 = 3

# number of pills in dispenser 2
pill_count_2 = 5

# sends a facebook message to the doctor
def send_message(pill_count):
    client = Client(patient_email, patient_password)
    thread_id = dr_id
    thread_type = ThreadType.USER
    if pill_count == 0:
        client.send(Message(patient_first + " " + patient_last + "\'s prescription is running low."), thread_id=thread_id, thread_type=thread_type)
    else:
        client.send(Message(patient_first + " " + patient_last + "\'s prescription is empty."), thread_id=thread_id, thread_type=thread_type)
    client.logout()
                    
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# rotates the pill dispenser's motor by the desired number of degrees
def set_angle(angle):
    GPIO.setup(3, GPIO.OUT)
    pwm=GPIO.PWM(3, 50)
    pwm.start(0)
    duty = angle / 18 + 2
    GPIO.output(3, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)
    pwm.stop()

# sets LED to red, yellow, or green depending on how many pills are left in dispenser
def turn_on_led(pill_count):
    GPIO.setwarnings(False)
    if pill_count > 2:
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(16, False)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, True)
    elif pill_count > 0:
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, False)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(16, True)
    else:
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(16, False)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, True)

# dispenses a pill from 1
def dispense_1():
    set_angle(170)
    set_angle(90)

# dispenses a pill from 2
def dispense_2():
    set_angle(20)
    set_angle(90)

# dispenses pills at the desired times
turn_on_led(pill_count)
while True:
    if [datetime.now().hour, datetime.now().minute] in dispense_times_1:
        dispense_1()
        pill_count_1 -= 1
        if pill_count_1 == 0:
            turn_on_led(0)
            send_message(0)
            break
        elif pill_count_1 < 3:
            turn_on_led(pill_count)
            send_message(pill_count)
            
    if [datetime.now().hour, datetime.now().minute] in dispense_times_2:
        dispense_2()
        pill_count_2 -= 1
        if pill_count_2 == 0:
            turn_on_led(0)
            send_message(0)
            break
        elif pill_count_2 < 3:
            turn_on_led(pill_count_2)
            send_message(pill_count_2)
        sleep(60)
    else:
        sleep(10)

GPIO.cleanup()
