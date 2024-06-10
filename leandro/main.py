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
import time

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
    video_config = picam2.create_video_configuration({"size": (640, 360)})
    picam2.video_configuration.controls.FrameRate = 30.0
    picam2.configure(video_config)
    encoder = JpegEncoder()

    output = StreamingOutput(recv_pipe)

    picam2.start_recording(encoder, FileOutput(output))

    while transmitting:
        continue
        scheddl.set_deadline(
            15_000_000,  # runtime in nanoseconds
            20_000_000,  # deadline in nanoseconds
            22_000_000  # time period in nanoseconds
        )
        scheddl.set_deadline(
            200 * 1000 * 1000,  # runtime in nanoseconds
            200 * 1000 * 1000,  # deadline in nanoseconds
            500 * 1000 * 1000  # time period in nanoseconds
        )
        scheddl.sched_yield()

    picam2.stop_recording()


def flush_socket(sock):
    # flush socket
    while True:
        try:
            sock.recv(1024)
        except:
            break


def cmd_receiver(send_pipe, movement_pipe):
    DEBUG = False

    peers = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setblocking(False)

    sock.bind((UDP_IP, UDP_CMDS_PORT))

    times_rec = []

    while True:
        scheddl.set_deadline(
            300_000,  # runtime in nanoseconds
            700_000,  # deadline in nanoseconds
            22_000_000  # time period in nanoseconds
        )

        hasdata = True
        data = None
        addr = None

        if DEBUG:
            start = time.time_ns()
        try:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            if addr not in peers:
                # print("new peer added", addr)
                peers.append(addr)
                send_pipe.send(peers)
        except:
            # no data to read
            hasdata = False

        if hasdata:
            try:
                data = data.decode('utf-8')
                parsed = json.loads(data)

                movement_pipe.send(parsed)
            except:
                print("error occurred", addr)

        flush_socket(sock)

        if DEBUG:
            times_rec.append(time.time_ns() - start)

        if DEBUG:
            total = 0
            maxi = -1
            for t in times_rec:
                total = total + t
                if t > maxi:
                    maxi = t
            if len(times_rec):
                print("cmd_receiver media:", total/len(times_rec), "max", maxi)

        scheddl.sched_yield()


def move_bot(movement_recv):
    DEBUG = False

    bot = AlphaBot2()
    bot.stop()

    times_rec = []

    while True:
        scheddl.set_deadline(
            15_000_000,  # runtime in nanoseconds
            20_000_000,  # deadline in nanoseconds
            22_000_000  # time period in nanoseconds
        )

        if DEBUG:
            start = time.time_ns()
        if movement_recv.poll():
            parsed = movement_recv.recv()
            # print("new", parsed)

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
                bot.moveCameraTo(parsed["x"], parsed["y"])

        if DEBUG:
            times_rec.append(time.time_ns() - start)

        if DEBUG:
            total = 0
            maxi = -1
            for t in times_rec:
                total = total + t
                if t > maxi:
                    maxi = t
            if len(times_rec):
                print("move_bot media:", total/len(times_rec), "max", maxi)

        scheddl.sched_yield()


if __name__ == "__main__":
    ctx = mp.get_context("spawn")

    camera_peers_conn, cmd_receiver_peers_conn = ctx.Pipe()
    movement_recv_conn, movement_data_conn = ctx.Pipe()

    camera_p = ctx.Process(target=camera, args=(camera_peers_conn, ))
    cmd_receiver_p = ctx.Process(
        target=cmd_receiver, args=(
            cmd_receiver_peers_conn,
            movement_recv_conn,
        ))
    movement_p = ctx.Process(
        target=move_bot, args=(movement_data_conn, ))

    camera_p.start()
    cmd_receiver_p.start()
    movement_p.start()

    try:
        while True:
            continue
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
        movement_p.kill()
