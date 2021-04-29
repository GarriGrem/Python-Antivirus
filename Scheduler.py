import schedule
from winsys import ipc
import Scanner


def Scan(path):
    client_mon = ipc.mailslot("monitoring_client")
    exes = Scanner.find_exe(path)
    total = len(exes)
    if total == 0:
        return
    for exe in exes:
        res = Scanner.scan(exe)
        try:
            client_mon.put({'progress': None, 'exe': exe, 'infected': res, 'marker': 'sched'})
        except Exception:
            print('Клиент выключен.')
            break


def startScheduling(path, interval, flag):
    global job1
    if interval == 30:
        job1 = schedule.every(interval).seconds.do(Scan, path, flag)
    job2 = schedule.every(interval).minutes.do(Scan, path, flag)
    schedule.run_pending()
    while True:
        if flag:
            if interval == 30:
                print('ddd')
                schedule.cancel_job(job1)
            else:
                schedule.cancel_job(job2)
            break
