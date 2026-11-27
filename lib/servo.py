from machine import Pin, PWM

class Servo:

    def __init__(self, signal_pin: int|str):
        """
        A simple class for interacting with a servo through PWM
        
        :param signal_pin: The pin the servo is connected to
        :type signal_pin: int | str
        """

        self._servo = PWM(Pin(signal_pin, Pin.OUT))
        # Initialize base frequency for the PWM
        self._servo.freq(50)
        self.MICROSEC_PER_DEGREE: int = 10000
        self.LOW_ANGLE_OFFSET: int = 500000

    def set_angle(self, degrees: float):
        """
        Sets the angle of the servo
        :param degrees: The angle to set the servo to [0,200]
        :ptype degrees: float
        """
        self._servo.duty_ns(int(degrees * self.MICROSEC_PER_DEGREE + self.LOW_ANGLE_OFFSET))

    def free(self):
        """
        Allows the servo to spin freely without holding position
        """
        self._servo.duty_ns(0)
