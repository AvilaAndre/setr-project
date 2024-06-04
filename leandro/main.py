from picamera2.outputs import FileOutput
from picamera2.encoders import JpegEncoder
from picamera2 import Picamera2
import multiprocessing as mp
import io
import base64
import socket
import json
from AlphaBot2 import AlphaBot2
import RPi.GPIO as GPIO
import scheddl

UDP_IP = ""  # leaving it empty will ensure every local address
UDP_CMDS_PORT = 5005
UDP_STREAM_PORT = 4242

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

speed = 40


class StreamingOutput(io.BufferedIOBase):
    def __init__(self, recv_pipe):
        self.frame = None
        self.output_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peers = []
        self.recv_pipe = recv_pipe

    def write(self, buf):
        self.frame = buf

        if self.recv_pipe.poll():
            self.peers = self.recv_pipe.recv()

        message = base64.b64encode(buf)

        if self.output_socket:
            for (peer_ip, _peer_port) in self.peers:
                try:
                    self.output_socket.sendto(
                        bytes(message), (peer_ip, UDP_STREAM_PORT))
                except:
                    pass


def camera(recv_pipe):
    transmitting = True

    picam2 = Picamera2()
    video_config = picam2.create_video_configuration({"size": (1280, 720)})
    picam2.video_configuration.controls.FrameRate = 60.0
    picam2.configure(video_config)
    encoder = JpegEncoder()

    output = StreamingOutput(recv_pipe)

    picam2.start_recording(encoder, FileOutput(output))

    while transmitting:
        scheddl.set_deadline(
            200 * 1000 * 1000,  # runtime in nanoseconds
            200 * 1000 * 1000,  # deadline in nanoseconds
            500 * 1000 * 1000  # time period in nanoseconds
        )
        scheddl.sched_yield()

    picam2.stop_recording()


def cmd_receiver(send_pipe):
    peers = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((UDP_IP, UDP_CMDS_PORT))

    bot = AlphaBot2()
    bot.stop()

    while True:
        scheddl.set_deadline(
            200 * 1000 * 1000,  # runtime in nanoseconds
            400 * 1000 * 1000,  # deadline in nanoseconds
            2000 * 1000 * 1000  # time period in nanoseconds
        )
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        if addr not in peers:
            print("new peer added", addr)
            peers.append(addr)
            send_pipe.send(peers)

        try:
            data = data.decode('utf-8')
            parsed = json.loads(data)

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

        scheddl.sched_yield()


if __name__ == "__main__":
    ctx = mp.get_context("spawn")

    camera_peers_conn, cmd_receiver_peers_conn = ctx.Pipe()

    camera_p = ctx.Process(target=camera, args=(camera_peers_conn, ))
    cmd_receiver_p = ctx.Process(
        target=cmd_receiver, args=(cmd_receiver_peers_conn, ))

    camera_p.start()
    cmd_receiver_p.start()

    try:
        while True:
            scheddl.set_deadline(
                200 * 1000 * 1000,  # runtime in nanoseconds
                400 * 1000 * 1000,  # deadline in nanoseconds
                1000 * 1000 * 1000,  # time period in nanoseconds
            )
            scheddl.sched_yield()
    except KeyboardInterrupt:
        print("Received exit, exiting")
        camera_p.kill()
        cmd_receiver_p.kill()
