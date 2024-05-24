from AlphaBot2 import AlphaBot2
import RPi.GPIO as GPIO
import time

UDP_IP = ""  # leaving it empty will ensure every local address
UDP_PORT = 5005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def main():
    bot = AlphaBot2()
    bot.stop()
    pwma = 0
    pwmb = 0

    print("left")
    for pwma in range(0, 100):
        bot.left()
        bot.setPWMA(pwma)
        bot.setPWMB(pwma)
        time.sleep(0.1)
    print("right")
    for pwmb in range(0, 100):
        bot.right()
        bot.setPWMA(pwmb)
        bot.setPWMB(pwmb)
        time.sleep(0.1)
    print("forward")
    for pwma in range(0, 100):
        bot.forward()
        bot.setPWMA(pwma)
        bot.setPWMB(pwma)
        time.sleep(0.1)
    print("backward")
    for pwmb in range(0, 100):
        bot.backward()
        bot.setPWMA(pwmb)
        bot.setPWMB(pwmb)
        time.sleep(0.1)

    bot.stop()


if __name__ == "__main__":
    main()
