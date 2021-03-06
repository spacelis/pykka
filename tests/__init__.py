import collections
import logging
import threading


class TestLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.lock = threading.RLock()
        with self.lock:
            self.events = collections.defaultdict(threading.Event)
            self.messages = {}
            self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        with self.lock:
            level = record.levelname.lower()
            self.messages[level].append(record)
            self.events[level].set()

    def reset(self):
        with self.lock:
            for level in ('debug', 'info', 'warning', 'error', 'critical'):
                self.events[level].clear()
                self.messages[level] = []

    def wait_for_message(self, level, num_messages=1):
        """Wait until at least ``num_messages`` log messages have been emitted
        to the given log level."""
        while True:
            with self.lock:
                if len(self.messages[level]) >= num_messages:
                    return
                self.events[level].clear()
            self.events[level].wait(5)
