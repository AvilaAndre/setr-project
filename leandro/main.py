import socket
import json

UDP_IP = ""  # leaving it empty will ensure every local address
UDP_PORT = 5005


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        data = data.decode('utf-8')
        parsed = json.loads(data)
        print("received: %s" % parsed)


if __name__ == "__main__":
    main()
