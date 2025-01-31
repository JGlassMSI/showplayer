import threading
import time
import logging

class TimerClass(threading.Thread):
    def __init__(self, func, args, delay=0.1):
        threading.Thread.__init__(self, daemon = True)
        self.event = threading.Event()
        self.func = func
        self.args = args
        self.delay = delay
        

    def run(self):
        logging.debug("TimerClass (probably InputStarter) has begun via run method")
        self.event.clear()
        while not self.event.is_set():
            self.func()
            time.sleep(self.delay)

    def stop(self):
        oldState = self.event.is_set
        if oldState:
            oldState = "Event was previously set though"
        else:
            oldState = "Event will now be set."
        logging.debug(f"Called stop() method of TimerClass (probably InputStarter) {oldState}")
        self.event.set()
