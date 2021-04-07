from winsys import ipc
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QThread, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QCheckBox, QListWidget
)

mail_server = ipc.mailslot("server")
mail_client = ipc.mailslot("client")
serv_mon = ipc.mailslot("monitoring_server")
client_mon = ipc.mailslot("monitoring_client")


# def thread(func):
#
#     def wrapper(*args, **kwargs):
#         current_thread = threading.Thread(
#             target=func, args=args, kwargs=kwargs)
#         current_thread.start()
#
#     return wrapper
#
#
# @thread
# def Listen():
#     while True:
#         recv = mail_client.get()
#         return recv

class ServiceListener(QObject):
    def __init__(self):
        super().__init__()
        self.state = 0

    def run(self):
        global pbar
        global scanned_listbox
        listener_thread = QThread.currentThread()
        while getattr(listener_thread, "listening", True):
            message = mail_client.get()
            print(message)
            pbar.setValue(message['progress'])
            scanned_listbox.insertItem(len(scanned_listbox), message['exe'])


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        font = QtGui.QFont()
        font.setFamily('Century Gothic')
        font.setPointSize(10)

        self.setGeometry(300, 300, 580, 600)
        #self.setStyleSheet("background-color: Honeydew")
        self.setWindowTitle("Простой антивирус")
        self.setFixedSize(self.size())

        global pbar
        pbar = QProgressBar(self)
        pbar.setGeometry(170, 250, 400, 30)
        pbar.setStyleSheet("text-align: center")

        global scanned_listbox
        scanned_listbox = QListWidget(self)
        scanned_listbox.setGeometry(170, 40, 400, 200)

        global infected_listbox
        infected_listbox = QListWidget(self)
        infected_listbox.setGeometry(170, 320, 400, 200)

        self.cb = QCheckBox('Мониторинг', self)
        self.cb.move(10, 300)
        self.cb.setFixedSize(150, 50)
        self.cb.toggle()
        self.cb.setFont(font)
        self.cb.setChecked(False)
        self.cb.stateChanged.connect(self.changeMonitoring)

        self.button_start_scan = QPushButton("Начать", self)
        self.button_start_scan.setFixedSize(140, 50)
        self.button_start_scan.move(10, 40)
        self.button_start_scan.setFont(font)

        self.button_stop_scan = QPushButton("Остановить", self)
        self.button_stop_scan.setEnabled(False)
        self.button_stop_scan.setFixedSize(140, 50)
        self.button_stop_scan.move(10, 110)
        self.button_stop_scan.setFont(font)

        self.button_quarantine = QPushButton("Переместить в \nкарантин", self)
        self.button_quarantine.setFixedSize(140, 50)
        self.button_quarantine.move(10, 180)
        self.button_quarantine.setFont(font)

        # self.button_delete = QPushButton("Удалить", self)
        # self.button_delete.setFixedSize(100, 50)
        # self.button_delete.move(340, 240)
        # self.button_delete.setStyleSheet("QPushButton{"
        #                                  "background-color: white;"
        #                                  "border-style: outset;"
        #                                  "border-width: 1px;"
        #                                  "border-radius: 10px;"
        #                                  "font: arial 10px;"
        #                                  "padding: 6px;"
        #                                  "border-radius: 10px}"
        #                                  "QPushButton:pressed {border-style: inset}")

        self.button_start_monitoring = QPushButton("Старт", self)
        self.button_start_monitoring.setFixedSize(140, 50)
        self.button_start_monitoring.move(10, 360)
        self.button_start_monitoring.setFont(font)
        self.button_start_monitoring.setEnabled(False)

        self.button_stop_monitoring = QPushButton("Стоп", self)
        self.button_stop_monitoring.setFixedSize(140, 50)
        self.button_stop_monitoring.move(10, 430)
        self.button_stop_monitoring.setFont(font)
        self.button_stop_monitoring.setEnabled(False)

        self.button_start_scan.clicked.connect(self.buttonStartClicked)
        self.button_stop_scan.clicked.connect(self.buttonStopClicked)
        self.button_start_monitoring.clicked.connect(self.buttonStartMonitoringClicked)
        # self.button_stop_monitoring.clicked.connect(self.button_stop_monitoring)

        self.label_path = QLabel("", self)
        self.label_path.setFixedSize(440, 20)
        self.label_path.move(10, 10)
        self.label_path.setFont(font)

        self.label_path_monitoring = QLabel("Путm ", self)
        self.label_path_monitoring.setFixedSize(110, 20)
        self.label_path_monitoring.move(10, 490)
        self.label_path_monitoring.setFont(font)
        self.label_path_monitoring.setEnabled(False)

        self.label_scanned = QLabel("Сканированные файлы ", self)
        self.label_scanned.setFont(font)
        self.label_scanned.setGeometry(280, 10, 220, 20)

        self.show()

        self.listener_thread = QThread()
        self.service_listener = ServiceListener()
        self.service_listener.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.service_listener.run)

    def changeMonitoring(self, state):
        if state == Qt.Checked:
            self.label_path_monitoring.setEnabled(True)
            self.button_start_monitoring.setEnabled(True)
            self.button_stop_monitoring.setEnabled(True)
        else:
            self.label_path_monitoring.setEnabled(False)
            self.button_start_monitoring.setEnabled(False)
            self.button_stop_monitoring.setEnabled(False)

    def buttonStartClicked(self):
        global pbar
        global scanned_listbox
        self.button_start_scan.setEnabled(False)
        scanned_listbox.clear()
        pbar.setValue(0)
        scan_path = QFileDialog.getExistingDirectory(self, "Выберите директорию", ".")
        self.label_path.setText("Scan path: " + scan_path)
        mail_server.put({'state': 'true', 'path': scan_path})
        self.service_listener.state = 1
        self.listener_thread.start()

    def buttonStopClicked(self):
        mail_server.put({'state': 'false', 'path': '--'})
        self.service_listener.state = 0
        global pbar
        pbar.setValue(0)

    def buttonStartMonitoringClicked(self):
        scan_path_monitoring = QFileDialog.getExistingDirectory(self, "Choose directory", ".")
        self.label_path.setText("Scan path: " + scan_path_monitoring)
        mail_server.put({'state': 'monitoring', 'path': scan_path_monitoring})

    #def buttonStopMonitoringClicked(self):


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())