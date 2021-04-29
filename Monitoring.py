import os
import fnmatch
import time
import Scanner
from watchdog.events import FileSystemEventHandler



class Handler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.flag = False
        self.path = None
        self.res = None

    def on_created(self, event):
        time.sleep(1)
        p = str(event.src_path)
        self.path = os.path.normpath(p)
        if fnmatch.fnmatch(self.path, '*.exe'):
            self.res = Scanner.scan(self.path)
            self.flag = True
        else:
            print("Файл не исполняемый")
            self.res = {'exe': None, 'name': 'Файл не исполняемый'}
            self.flag = True