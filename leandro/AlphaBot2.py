import RPi.GPIO as GPIO
from PCA9685 import PCA9685


def clamp(val: float, mini: float, maxi: float) -> float:
    if (val < mini):
        return mini
    elif (val > maxi):
        return maxi
    return val


class AlphaBot2(object):

    def __init__(self, ain1=12, ain2=13, ena=6, bin1=20, bin2=21, enb=26):
        self.AIN1 = ain1
        self.AIN2 = ain2
        self.BIN1 = bin1
        self.BIN2 = bin2
        self.ENA = ena
        self.ENB = enb
        self.PA = 50
        self.PB = 50

        self.ServoPWM = PCA9685(0x40, debug=False)
        self.ServoPWM.setPWMFreq(50)
        # TODO: Discover the actual limit
        self.ServoLimit = 2500

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def forward(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)

    def backward(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def left(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PA)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def right(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PA)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def setPWMA(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def setPWMB(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)

    def setMotor(self, left, right):
        if ((right >= 0) and (right <= 100)):
            GPIO.output(self.AIN1, GPIO.HIGH)
            GPIO.output(self.AIN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif ((right < 0) and (right >= -100)):
            GPIO.output(self.AIN1, GPIO.LOW)
            GPIO.output(self.AIN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if ((left >= 0) and (left <= 100)):
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif ((left < 0) and (left >= -100)):
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

    """
    takes the phone angles and converts to the camera limits
    clamps the x and y to be between -40 and 40

    servo x limit from -160 to 100
    -40         40
    |------------|

    -160       100
    |------------|
    offset: -30

    servo y limit from -100 to 180
    -40         40
    |------------|

    -100       180
    |------------|
    offset: 40

    """

    def moveCameraTo(self, x, y):
        x = -x

        # clamp values
        x = clamp(x, -90, 90)
        y = clamp(y, -90, 90)

        # normalize
        x = (x + 90)/180
        y = (y + 90)/180

        # the camera has limits
        x = clamp(x, 0.25, 0.85)
        y = clamp(y, 0.2, 0.95)

        y = y * self.ServoLimit
        x = x * self.ServoLimit

        self.ServoPWM.setServoPulse(0, y)
        self.ServoPWM.setServoPulse(1, x)
