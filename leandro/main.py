from picamera2.outputs import FileOutput
from picamera2.encoders import JpegEncoder
from picamera2 import Picamera2
import io
import cv2
import base64
import socket
import json
from AlphaBot2 import AlphaBot2
import RPi.GPIO as GPIO

UDP_IP = ""  # leaving it empty will ensure every local address
UDP_CMDS_PORT = 5005
UDP_STREAM_PORT = 4242

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

speed = 10

output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peers = []


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        # self.condition = Condition()

    def write(self, buf):
        # with self.condition:
        self.frame = buf

        message = base64.b64encode(buf)
        print("wrote frame", peers)

        if output_socket:
            for (peer_ip, _peer_port) in peers:
                try:
                    output_socket.sendto(
                        bytes(message), (peer_ip, UDP_STREAM_PORT))
                except:
                    pass
        # self.condition.notify_all()


def camera():
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration({"size": (1280, 720)})
    picam2.configure(video_config)
    encoder = JpegEncoder()

    output = StreamingOutput()

    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    # sock.connect((UDP_IP, UDP_STREAM_PORT))
    picam2.start_recording(encoder, FileOutput(output))

    return picam2


def main():
    picam2 = camera()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((UDP_IP, UDP_CMDS_PORT))

    bot = AlphaBot2()
    bot.stop()

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        if addr not in peers:
            peers.append(addr)

        try:
            data = data.decode('utf-8')
            parsed = json.loads(data)
            # print("received: %s" % parsed)
            # print("received from", addr)

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
        except:
            print("error occurred", addr)

    picam2.stop_recording()


if __name__ == "__main__":
    main()
