import math
import time

import schedule
import Scanner
import Monitoring
import Scheduler
import threading
from winsys import ipc
from watchdog.observers import Observer
from multiprocessing.connection import Listener


address = ('localhost', 6000)


serv = ipc.mailslot("server")
serv_mon = ipc.mailslot("monitoring_server")


def thread(func):
    def wrapper(*args, **kwargs):
        current_thread = threading.Thread(
            target=func, args=args, kwargs=kwargs)
        current_thread.start()
    return wrapper


# def Listen() -> dict:
#     conn = listener.accept()
#     msg = conn.recv()
#     # recv = serv.get()
#     # return recv
#     return msg


@thread
def Scan(stop_event, path):
    client = ipc.mailslot("client")
    exes = Scanner.find_exe(path)
    global flag
    flag = False
    total = len(exes)
    if total == 0:
        return
    percent = 100 / total
    progress = 1
    for exe in exes:
        progress += percent
        if not stop_event.wait(0.1):
            flag = True
            res = Scanner.scan(exe)
            try:
                client.put({'progress': math.ceil(progress), 'exe': exe, 'infected': res, 'marker': 'scan'})
            except Exception:
                print('Клиент отключен')
                break
        else:
            break


@thread
def StartMonitoring(path, stop_event):
    global observer
    observer = Observer()
    handler = Monitoring.Handler()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    client_mon = ipc.mailslot("monitoring_client")
    while True:
        if stop_event.isSet():
            observer.stop()
            break
        if handler.flag:
            handler.flag = False
            try:
                client_mon.put({'item': handler.path, 'infected': handler.res, 'marker': 'mon'})
                handler.res = None
            except Exception:
                print('Клиент выключен.')


@thread
def startScheduling(path, interval, stop_event):
    global job1
    if interval == 30:
        job1 = schedule.every(interval).seconds.do(Scheduler.Scan, path)
    job2 = schedule.every(interval).minutes.do(Scheduler.Scan, path)
    while True:
        schedule.run_pending()
        if stop_event.isSet():
            schedule.cancel_job(job1)
            schedule.cancel_job(job2)
            break


if __name__ == '__main__':
    kill = threading.Event()
    kill2 = threading.Event()
    kill3 = threading.Event()
    listener = Listener(address)
    while True:
        conn = listener.accept()
        while not conn.closed:
            try:
                request = conn.recv()
            except Exception:
                request = {'state': None}
                print('Клиент отрубился')
                conn.close()
            if request['state'] == 'scheduling':
                kill3.clear()
                print(request)
                startScheduling(request['path'], request['interval'], kill3)
            if request['state'] == 'stop_sched':
                print(request)
                kill3.set()
            if request['state'] == 'monitoring':
                print(request)
                kill2.clear()
                StartMonitoring(request['path'], kill2)
                # StartMonitoring(kill2, request['path'])
            if request['state'] == '1':
                print(request)
                kill2.set()
                # StopMonitoring()
            if request['state'] == 'true':
                print(request)
                kill.clear()
                time.sleep(1)
                Scan(kill, request['path'])
            if request['state'] == 'false':
                print(request)
                kill.set()
