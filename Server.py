import math
import time
import Scanner
import Monitoring
import threading
from winsys import ipc


serv = ipc.mailslot("server")
client = ipc.mailslot("client")
serv_mon = ipc.mailslot("monitoring_server")
client_mon = ipc.mailslot("monitoring_client")


def thread(func):
    def wrapper(*args, **kwargs):
        current_thread = threading.Thread(
            target=func, args=args, kwargs=kwargs)
        current_thread.start()
    return wrapper


def Listen() -> dict:
    while True:
        recv = serv.get()
        return recv


# def ListenMonitoring() -> dict:
#     while True:
#         recv = serv_mon.get()
#         return recv


@thread
def Scan(stop_event, path):
    # while not stop_event.wait(1):
    #     print('Scan...')
    #     time.sleep(1)
    # print('stop')
    # path = 'C:\\Program Files (x86)'
    exes = Scanner.find_exe(path)
    global flag
    flag = False
    total = len(exes)
    percent = 100 / total
    progress = 0
    for exe in exes:
        progress += percent
        client.put({'progress': math.ceil(progress), 'exe': exe})
        if not stop_event.wait(0.1):
            flag = True
            Scanner.scan(exe, flag)
        else:
            break


@thread
def ScanFromMonitoring(stop_event, path):
    Monitoring.StartMonitoring(path)
    while True:
        if stop_event.wait(1):
            Monitoring.StopMonitoring()


if __name__ == '__main__':
    kill = threading.Event()
    kill2 = threading.Event()
    while True:
        request = Listen()
        if request['state'] == 'monitoring':
            kill2.clear()
            ScanFromMonitoring(kill, request['path'])
        if request['state'] == 'true':
            kill.clear()
            Scan(kill, request['path'])
        if request['state'] == 'false':
            kill.set()

