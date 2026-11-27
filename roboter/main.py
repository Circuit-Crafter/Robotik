from apds9960 import APDS9960
from IDG_I2C_Bus import I2C_Bus
from adafruit_tcs34725 import TCS34725
import time
from motor import DualPWMMotor
from encoder import Encoder
from machine import Pin, ADC
from imu import IMU
import math
from ir_sensors import QTRRCSensors
from output import *

from machine import Pin
from neopixel import NeoPixel



def is_black(value: int):
    return value < 250



GREEN = "\033[32m"
BLUE = "\033[34m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

print(f"{YELLOW}Initialisierung startet.{RESET}")
print(f"{YELLOW}Sensoren werden initialisiert.{RESET}")
liniensensoren = QTRRCSensors()
print(f"{GREEN}Sensoren Initialisierung erfolgreich.{RESET}")


print(f"{YELLOW}Motoren werden initialisiert.{RESET}")
getriebe_uebersetzung = 298

motorLeft = DualPWMMotor("MOTOR_L_IN_1", "MOTOR_L_IN_2", flip_dir=True)
encoderLeft = Encoder(0, "MOTOR_L_ENCODER_A", "MOTOR_L_ENCODER_B", flip_dir=True, gear_ratio=getriebe_uebersetzung)
usedPowerLeft = ADC(Pin(40, Pin.IN)) 

motorRight = DualPWMMotor("MOTOR_R_IN_1", "MOTOR_R_IN_2")
encoderRight = Encoder(1, "MOTOR_R_ENCODER_A", "MOTOR_R_ENCODER_B", gear_ratio=getriebe_uebersetzung)
usedPowerRight = ADC(Pin(43, Pin.IN))
print(f"{GREEN}Sensoren Initialisierung erfolgreich.{RESET}")

try:
    while(True):
        lenkstärke = 0.0
        helligkeiten = liniensensoren.read()
        for i in helligkeiten:
            # print(wert_aufzeichnen(i), end="")
            pass
        # print()


        if is_black(helligkeiten[5]):
            # print("Rechts")
            lenkstärke -=1
        if is_black(helligkeiten[4]):
            # print("leicht Rechts")
            lenkstärke -=0.25
        if is_black(helligkeiten[0]):
            # print("Links")
            lenkstärke +=1
        if is_black(helligkeiten[1]):
            # print("leicht Links")
            lenkstärke +=0.25
        if abs(lenkstärke)>0:
            motorRight.set_effort(0.1+lenkstärke)
            motorLeft.set_effort(0.1-lenkstärke)
        else:
            motorRight.set_effort(0.3)
            motorLeft.set_effort(0.3)
        

        


except KeyboardInterrupt:
    pass

finally:
    print(f"{RED}Abbruch.{RESET}")
    motorLeft.coast()
    motorRight.coast()