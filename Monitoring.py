import os
import time
import fnmatch

import Scanner
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        p = str(event.src_path)
        path = os.path.normpath(p)
        if fnmatch.fnmatch(path, '*.exe'):
            Scanner.scan(path, True)
        else:
            print("Файл не исполняемый")

    # def on_deleted(self, event):
    #     print(event)

    def on_moved(self, event):
        self.p = event.src_path
        #print(self.p)

    def get_path(self):
        return self.p


def StartMonitoring(path):
    global observer
    observer = Observer()
    observer.schedule(Handler(), path, recursive=True)
    observer.start()
    while True:
        time.sleep(1)

    # try:
    #     while True:
    #         time.sleep(0.1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()


def StopMonitoring():
    observer.stop()
    observer.join()