from threading import Thread
from queue import Queue

import requests
import pynfc
import time
import sys


MUSICBOX_SERVER = 'https://musicbox.cleverdevil.app'


class MessageDispatcher(Thread):

    def __init__(self):
        self.message_queue = Queue()
        super().__init__(daemon=True)

    def dispatch(self, message):
        self.message_queue.put(message)

    def send_event(self, message):
        print(f'Sending Event -> {message}')
        message = message.decode('utf-8')
        requests.get(f'{MUSICBOX_SERVER}/{message}')

    def run(self):
        while True:
            message = self.message_queue.get()
            self.send_event(message)
            self.message_queue.task_done()


def poll(reader, dispatcher):
    last_time = 0

    for target in reader.poll():
        now = time.time()
        if now - last_time > 10:
            dispatcher.dispatch(target.uid)
            last_time = now


def main():
    dispatcher = MessageDispatcher()
    dispatcher.start()

    reader = pynfc.Nfc('acr122_usb')

    try:
        while True:
            try:
                poll(reader, dispatcher)
            except pynfc.TimeoutException as e:
                print('Timed out... reconnecting to reader...')

    except KeyboardInterrupt as e:
        print('Stop requested')
        dispatcher.join()
        sys.exit()


if __name__ == '__main__':
    main()
