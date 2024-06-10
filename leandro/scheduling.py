import multiprocessing as mp
import scheddl


def camera(recv_pipe):
    transmitting = True

    peers = []

    while transmitting:
        scheddl.set_deadline(
            200 * 1000 * 1000,  # runtime in nanoseconds
            200 * 1000 * 1000,  # deadline in nanoseconds
            500 * 1000 * 1000  # time period in nanoseconds
        )
        if recv_pipe.poll():
            peers = recv_pipe.recv()
        print("camera")
        scheddl.sched_yield()


def cmd_receiver(send_pipe):

    peers = []
    while True:
        scheddl.set_deadline(
            200 * 1000 * 1000,  # runtime in nanoseconds
            400 * 1000 * 1000,  # deadline in nanoseconds
            2000 * 1000 * 1000  # time period in nanoseconds
        )
        send_pipe.send(peers)
        print("cmd_receiver")
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

            # print("os", os.sched_getscheduler(os.getpid()))
            print("main")
            scheddl.sched_yield()
    except KeyboardInterrupt:
        print("Received exit, exiting")
        camera_p.kill()
        cmd_receiver_p.kill()
