import socket
import json
from AlphaBot2 import AlphaBot2
import RPi.GPIO as GPIO

UDP_IP = ""  # leaving it empty will ensure every local address
UDP_PORT = 5005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

speed = 10


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((UDP_IP, UDP_PORT))

    bot = AlphaBot2()
    bot.stop()

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        data = data.decode('utf-8')
        parsed = json.loads(data)
        print("received: %s" % parsed)

        if (parsed["type"] == "state"):
            if (parsed["up"]):
                bot.forward()
                bot.setPWMA(speed)
                bot.setPWMB(speed)
            elif (parsed["down"]):
                bot.backward()
                bot.setPWMA(speed)
                bot.setPWMB(speed)
            elif (parsed["right"]):
                bot.right()
                bot.setPWMA(speed)
                bot.setPWMB(speed)
            elif (parsed["left"]):
                bot.left()
                bot.setPWMA(speed)
                bot.setPWMB(speed)
            else:
                bot.stop()
        elif (parsed["type"] == "gyro"):
            bot.moveCameraTo(parsed["x"], parsed["y"])


if __name__ == "__main__":
    main()
