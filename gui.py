import time
from winsys import ipc
import sys
from multiprocessing.connection import Client

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QListWidget,
    QComboBox
)

mail_server = ipc.mailslot("server")
mail_client = ipc.mailslot("client")
client_mon = ipc.mailslot("monitoring_client")
address = ('localhost', 6000)


class ServiceListener(QObject):
    def __init__(self):
        super().__init__()
        self.state = None

    def run(self):
        global pbar, scanned_listbox, infected_listbox
        listener_thread = QThread.currentThread()
        while getattr(listener_thread, "listening", True):
            message = mail_client.get()
            pbar.setValue(message['progress'])
            if message['exe'] is not None:
                if message['marker'] == 'scan':
                    msg = "[СКАНЕР] " + message['exe']
                    scanned_listbox.insertItem(0, msg)

            if message['infected'] is not None:
                res = str(message['infected']['name']) + str(message['infected']['exe'])
                infected_listbox.insertItem(0, res)


class ServiceListener2(QObject):
    def __init__(self):
        super().__init__()
        self.state = 0

    def run(self):
        global infected_listbox, scanned_listbox
        listener_thread = QThread.currentThread()
        while getattr(listener_thread, "listening", True):
            message = client_mon.get()
            if message['marker'] == 'sched':
                msg = "[ПО РАСПИСАНИЮ] " + str(message['exe'])
                scanned_listbox.insertItem(0, msg)
            if message['marker'] == 'mon':
                msg = "[МОНИТОРИНГ] " + str(message['item'])
                scanned_listbox.insertItem(0, msg)
            if message['infected'] is not None:
                res = str(message['infected']['name']) + str(message['infected']['exe'])
                infected_listbox.insertItem(0, res)


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global conn
        conn = Client(address)
        font = QtGui.QFont()
        font.setFamily('Century Gothic')
        font.setPointSize(10)

        self.setGeometry(300, 300, 580, 650)
        self.setWindowTitle("Простой антивирус")
        self.setFixedSize(self.size())

        self.combo = QComboBox(self)
        self.combo.addItems(["Каждые 30 секунд", "Каждую 1 минуту", "Каждые 5 минут", "Каждые 10 минут", "Каждые 30 минут"])
        self.combo.move(10, 290)
        self.combo.setFont(QtGui.QFont("Century Gothic", 8))
        self.combo.setFixedSize(140, 30)
        self.comboState = 30

        global pbar
        pbar = QProgressBar(self)
        pbar.setGeometry(170, 290, 400, 30)
        pbar.setStyleSheet("text-align: center")

        global scanned_listbox
        scanned_listbox = QListWidget(self)
        scanned_listbox.setGeometry(170, 80, 400, 200)

        global infected_listbox
        infected_listbox = QListWidget(self)
        infected_listbox.setGeometry(170, 410, 400, 180)

        self.button_start_scan = QPushButton("Старт", self)
        self.button_start_scan.setFixedSize(140, 50)
        self.button_start_scan.move(10, 30)
        self.button_start_scan.setFont(font)

        self.button_stop_scan = QPushButton("Стоп", self)
        self.button_stop_scan.setEnabled(False)
        self.button_stop_scan.setFixedSize(140, 50)
        self.button_stop_scan.move(10, 100)
        self.button_stop_scan.setFont(font)

        self.button_start_monitoring = QPushButton("Старт", self)
        self.button_start_monitoring.setFixedSize(140, 50)
        self.button_start_monitoring.move(10, 510)
        self.button_start_monitoring.setFont(font)

        self.button_stop_monitoring = QPushButton("Стоп", self)
        self.button_stop_monitoring.setFixedSize(140, 50)
        self.button_stop_monitoring.move(10, 580)
        self.button_stop_monitoring.setFont(font)
        self.button_stop_monitoring.setEnabled(False)

        self.button_start_scheduler = QPushButton("Старт", self)
        self.button_start_scheduler.setFixedSize(140, 50)
        self.button_start_scheduler.move(10, 340)
        self.button_start_scheduler.setFont(font)

        self.button_stop_scheduler = QPushButton("Стоп", self)
        self.button_stop_scheduler.setFixedSize(140, 50)
        self.button_stop_scheduler.move(10, 410)
        self.button_stop_scheduler.setFont(font)
        self.button_stop_scheduler.setEnabled(False)

        self.button_start_scan.clicked.connect(self.buttonStartClicked)
        self.button_stop_scan.clicked.connect(self.buttonStopClicked)
        self.button_start_monitoring.clicked.connect(self.buttonStartMonitoringClicked)
        self.button_stop_monitoring.clicked.connect(self.buttonStopMonitoringClicked)
        self.button_start_scheduler.clicked.connect(self.buttonStartScheduler)
        self.button_stop_scheduler.clicked.connect(self.buttonStopScheduler)

        self.label_path = QLabel("", self)
        self.label_path.setFixedSize(440, 20)
        self.label_path.move(170, 25)
        self.label_path.setFont(font)

        self.label_path_monitoring = QLabel("", self)
        self.label_path_monitoring.setFixedSize(440, 20)
        self.label_path_monitoring.move(170, 600)
        self.label_path_monitoring.setFont(font)

        self.label_path_scheduling = QLabel("", self)
        self.label_path_scheduling.move(170, 340)
        self.label_path_scheduling.setFont(font)
        self.label_path_scheduling.adjustSize()

        self.label_scanned = QLabel("Сканированные файлы ", self)
        self.label_scanned.setFont(font)
        self.label_scanned.setGeometry(280, 50, 220, 20)

        self.label_infected = QLabel("Инфицированные файлы ", self)
        self.label_infected.setFont(font)
        self.label_infected.setGeometry(260, 10, 230, 750)

        self.label_monitoring = QLabel("Мониторинг", self)
        self.label_monitoring.setFont(font)
        self.label_monitoring.adjustSize()
        self.label_monitoring.move(30, 485)

        self.label_scan = QLabel("Сканирование", self)
        self.label_scan.setFont(font)
        self.label_scan.adjustSize()
        self.label_scan.move(18, 7)

        self.label_schedule = QLabel("Расписание", self)
        self.label_schedule.setFont(font)
        self.label_schedule.adjustSize()
        self.label_schedule.move(23, 265)

        self.combo.activated[str].connect(self.schedulerScan)

        self.show()

        self.listener_thread = QThread()
        self.service_listener = ServiceListener()
        self.service_listener.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.service_listener.run)

        self.listener_thread2 = QThread()
        self.service_listener2 = ServiceListener2()
        self.service_listener2.moveToThread(self.listener_thread2)
        self.listener_thread2.started.connect(self.service_listener2.run)

    def buttonStartScheduler(self):
        scan_path_scheduler = QFileDialog.getExistingDirectory(self, "Выберите директорию", ".")
        conn.send({'state': 'scheduling', 'path': scan_path_scheduler, 'interval': self.comboState})
        self.service_listener2.state = 1
        self.listener_thread2.start()
        self.button_start_scheduler.setEnabled(False)
        self.button_stop_scheduler.setEnabled(True)

    def buttonStopScheduler(self):
        self.button_start_scheduler.setEnabled(True)
        self.button_stop_scheduler.setEnabled(False)
        conn.send({'state': 'stop_sched', 'path': None, 'interval': None})

    def schedulerScan(self):
        if self.combo.currentText() == "Каждые 30 секунд":
            print("30 seconds")
            self.comboState = 30
        if self.combo.currentText() == "Каждую 1 минуту":
            print("1 minutes")
            self.comboState = 1
        if self.combo.currentText() == "Каждые 5 минут":
            print("5 minutes")
            self.comboState = 5
        if self.combo.currentText() == "Каждые 10 минут":
            print("10 minutes")
            self.comboState = 10
        if self.combo.currentText() == "Каждые 30 минут":
            print("30 minutes")
            self.comboState = 30


    def buttonStartClicked(self):
        global pbar
        global scanned_listbox
        self.button_stop_scan.setEnabled(True)
        self.button_start_scan.setEnabled(False)
        scanned_listbox.clear()
        pbar.setValue(0)
        scan_path = QFileDialog.getExistingDirectory(self, "Выберите директорию", ".")
        self.label_path.setText("Директория: " + scan_path)
        conn.send({'state': 'true', 'path': scan_path})
        self.service_listener.state = 1
        self.listener_thread.start()

    def buttonStopClicked(self):
        global pbar
        conn.send({'state': 'false', 'path': '--'})
        self.service_listener.state = 0
        self.button_start_scan.setEnabled(True)
        self.button_stop_scan.setEnabled(False)
        time.sleep(0.5)
        pbar.setValue(0)

    def buttonStartMonitoringClicked(self):
        self.button_start_monitoring.setEnabled(False)
        self.button_stop_monitoring.setEnabled(True)
        self.service_listener2.state = 1
        self.listener_thread2.start()
        scan_path_monitoring = QFileDialog.getExistingDirectory(self, "Выберите директорию", ".")
        self.label_path_monitoring.setText("Директория: " + scan_path_monitoring)
        conn.send({'state': 'monitoring', 'path': scan_path_monitoring})

    def buttonStopMonitoringClicked(self):
        self.button_start_monitoring.setEnabled(True)
        self.button_stop_monitoring.setEnabled(False)
        conn.send({'state': '1', 'path': '--'})


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())
