import argparse
import threading

from cmd import Cmd
from ddp import *


class App(Cmd):
    """Main input loop."""

    def __init__(self, ddp_endpoint):
        Cmd.__init__(self)
        self.received = False
        self.disconnected = False

        call_id = 'call_id'
        received_cond = threading.Condition()
        def received_message_callback(message):
            if isinstance(message, ResultMessage) and message.id_ == call_id:
                with received_cond:
                    self.received = True
                    received_cond.notify()

        disconnected_cond = threading.Condition()
        def disconnected_callback(code, reason=None):
            with disconnected_cond:
                self.disconnected = True
                disconnected_cond.notify()

        conn = DdpConnection(
            str(ServerUrl(ddp_endpoint)),
            received_message_callback=received_message_callback,
            disconnected_callback=disconnected_callback
        )
        conn.connect()
        conn.send(MethodMessage(call_id, 'echo', ['Hello, World!']))

        with received_cond:
            while not self.received:
                received_cond.wait(timeout=1)


def main():
    """Parse the command line arguments and create a new App instance"""
    parser = argparse.ArgumentParser(
        description='A command-line tool for communicating with a DDP server.')
    parser.add_argument(
        'ddp_endpoint', metavar='ddp_endpoint',
        help='DDP websocket endpoint to connect ' +
        'to, e.g. madewith.meteor.com')
    # parser.add_argument(
    #     '--print-raw', dest='print_raw', action="store_true",
    #     help='print raw websocket data in addition to parsed results')
    args = parser.parse_args()

    app = App(args.ddp_endpoint)
    try:
        app.cmdloop()
    except KeyboardInterrupt:
        # On Ctrl-C or thread.interrupt_main(), just exit without printing a
        # traceback.
        pass


if __name__ == '__main__':
    main()