#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, time
import traceback
from PyQt5.QtWidgets import QApplication, QComboBox, QFileDialog, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QProgressDialog, QPushButton, QSizePolicy, QSpinBox, QStatusBar, QStyleFactory, QTabWidget, QTextBrowser, QVBoxLayout, QWidget, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import QEvent, QObject, QRunnable, QThreadPool, Qt, pyqtSignal, pyqtSlot
import shutil
from datetime import datetime
import shelve
import paramiko
from scp import SCPClient
from helper_com import OT2Com

from ot2_connection_data import OT2ConnectionData


class WorkerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress


    @pyqtSlot()
    def run(self):

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
            # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class RetestApp(QMainWindow):

    # defining vars
    cwd = None
    app = None
    screen = None
    chs_com = None
    cb_com = None
    btn_scan = None
    le_rackid = None
    sb_num = None
    chs_num_racks = None
    num_scanned = 1
    btn_num = None
    lbl_scanned_rack = None
    pb_scan = None
    status_bar = None
    tb_racks = None
    threadpool = None
    pb_dialog = None
    cmd_output = None
    dtpq = None
    filename_save = None
    rack_pos = None
    pos_x_list = None
    lbl_rackid = None
    chs_rackid = None
    lyt_form = None
    btn_save = None
    le_cust = None
    lbl_form_count = None
    lbl_form_count_all = None
    count_all = 0

    lw_connection = None
    shelf_connections = None
    shelf_len = None
    lbl_hostname = None
    le_hostname = None
    lbl_username = None
    le_username = None
    lbl_key = None
    le_key = None
    hostname = None
    username = None
    key = None
    lbl_file_cur = None
    file_path = None
    btn_create = None
    btn_send = None
    sb_rack = None
    sb_tip = None
    sb_pcr = None
    sb_pcr = None
    btn_mm = None
    tube_codes = None
    helper_com = None
    protocol_id = None



    # defining the initialization function
    def __init__(self):

        # initial window setup
        super().__init__()
        
        # defining paths
        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))

        # purge the temporary folder
        self.purge_tmp()

        # create a threadpool
        self.threadpool = QThreadPool()

        # setup of a status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)



        self.open_session("data_connection.out")
        
        self.set_connection()

        
        self.setAcceptDrops(True)

        self.initUI()

        self.populate_list_connections()


        # call a function to setup the UI
        

    # defining a function that responds to dragging a file
    def dragEnterEvent(self, event):
        self.setStyleSheet("background-color: blue;")
        if event.mimeData().hasUrls():
            event.accept() 
        else:
            event.ignore()

     # defining a function that responds to user dropping a file into the app
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.setStyleSheet("background-color: white")
        if len(files) > 1:
            self.show_error("Prosím vkládejte jenom jeden soubor")
        elif len(files) == 1:
            if files[0].endswith(".csv"):
                self.file_path = files[0]
                self.parse_file(files[0])
            else:
                self.show_error("Vložený soubor není ve formátu CSV")

    def parse_file(self, path):
        try:
            file = open(path, "r") #opens the file in read mode
            self.tube_codes = file.read().splitlines() #puts the file into an array
            file.close()
            file_split = path.split("/")
            self.lbl_file_cur.setText(file_split[len(file_split)-1])
            self.lbl_file_cur.setStyleSheet("background-color: green; color: white")
            self.status_bar.showMessage("Soubor " + file_split[len(file_split)-1] + " úspěšně našten")

        except:
            self.show_error("Chyba v načítání souboru")

    def scan_racks(self):
        pass


    def populate_list_connections(self):
        for unit in self.shelf_connections:
            self.lw_connection.addItem("Username: " + unit.username + "  Hostname: " + unit.hostname + "  SSH Key:  " + unit.key)

    def set_connection(self):
        self.hostname = self.shelf_connections[0].hostname
        self.username = self.shelf_connections[0].username
        self.key = self.shelf_connections[0].key

        self.helper_com = OT2Com(self.hostname)

    def create_protocol(self):
        pass



    def save_session(self, filename):

        try:
                
            shelf = shelve.open(os.path.join(self.cwd, "data", filename))
            shelf["connections"] = self.shelf_connections
            shelf.close()

        except:

            shelf = shelve.open(filename,"n")


            self.show_error("Chyba načítání proměnných spojení")
            self.quit_app("end", QEvent)

    def open_session(self, filename):

        try:
                
            shelf = shelve.open(os.path.join(self.cwd, "data", filename))
            self.shelf_connections = shelf["connections"]
            shelf.close()

        except:

            shelf = shelve.open(filename,"n")
            shelf.close()

            self.show_error("Chyba ukládání proměnných spojení")

    def ask_save(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, caption="Uložení souboru", directory=os.path.join(os.path.expanduser("~"), "Diana Biotechnologies, s.r.o", "DL Lab - Documents", "General", "!Prijem_vzorku", "1.Prijem_kuryr_SCAN", self.filename_save), filter="CSV soubor (*.csv);;Všechny soubory (*)", options=options)
        if fileName:
            return fileName
    
    # defining a function to be called when the user attempts to close the window
    def closeEvent(self, event):
        self.quit_app("normal", event)
        
    # defining a function that asks the user if they really want to close the app
    def quit_app(self, type, event):
        if type == "normal":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
            msg.setWindowTitle("Quit app")
            msg.setText("Do you want to quit this app?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            answer = msg.exec_()
            if answer == QMessageBox.Yes:
                self.save_session("data_connection.out")
                self.purge_tmp()
                event.accept()
            elif answer == QMessageBox.No:
                event.ignore()
        if type == "end":
            self.save_session("data_connection.out")
            self.purge_tmp()
            sys.exit()

    # definging a function that removes temporary files
    def purge_tmp(self):
        try:
            for root, dirs, files in os.walk(os.path.join(self.cwd, "tmp")):
                for file in files:
                    if file != "tmp":
                        os.remove(os.path.join(root, file))
        except:
            pass
    
    # defining a function that shows error message
    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("color: black")
        msg.exec_()

    # defining a function that shows a success message
    def show_success(self, message):
        msg = QMessageBox()
        msg.setIconPixmap(QPixmap(os.path.join(self.cwd, "img", "success.png")).scaled(50, 50, Qt.KeepAspectRatio))
        msg.setText(message)
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
        msg.setWindowTitle("Action complete")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("background-color: white;")
        msg.exec_()

    # defining a function that creates a progress dialog
    def create_progress_dialog(self, title, text):
        self.pb_dialog = QProgressDialog(self)
        self.pb_dialog.setMinimum(0)
        self.pb_dialog.setLabelText(text)
        self.pb_dialog.setMaximum(100)
        self.pb_dialog.setValue(0)
        self.pb_dialog.setWindowTitle(title)
        self.pb_dialog.setCancelButton(None)
        self.pb_dialog.setModal(True)

            
    def save_file(self):
        filename = self.ask_save()
        if filename is None:
            self.show_error("Chyba ukládání, uložte soubor manuálně tlačítkem")
            self.btn_save.show()
            self.btn_save.setEnabled(True)
            self.le_rackid.setEnabled(False)
            self.btn_save.setStyleSheet("background-color: green; color: white")
            self.btn_scan.setEnabled(False)
            self.btn_scan.setStyleSheet("background-color: black; color: white")
        else:
            shutil.copy(os.path.join(self.cwd, "tmp", self.filename_save), filename)
            self.show_success("Racky úspěšně naskenovány!")
            self.quit_app("end", QEvent)


    def scp_send_run(self, protocol_file):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, username=self.username, pkey=paramiko.RSAKey.from_private_key_file(os.path.join(os.path.expanduser("~"), self.key)))
            scp = SCPClient(ssh.get_transport())
            cmd = "cd /data/user_storage/ && opentrons_execute /data/user_storage/" + protocol_file
            scp.put(os.path.join(os.path.expanduser("~"), "OneDrive - Diana Biotechnologies, s.r.o", "Desktop", "opentrons_testing", "opentrons2.py"), recursive=True, remote_path="/data/user_storage")
            ssh.exec_command(cmd)
            ssh.close()
        except:
            self.status_bar.showMessage("Chyba v odesílání/spuštení protokolu")

    def send_run_protocol(self, files):
        
        self.protocol_id, response = self.helper_com.send(files)

        errors = ""

        try:
            errors = response.json()['data'].get('errors')
            if errors:
                raise RuntimeError(f"Errors in protocol: {errors}")

            self.helper_com.run_protocol(self.protocol_id)

        finally:
            # Use the protocol_id to DELETE the protocol
            self.helper_com.purge(self.protocol_id)



    def btn_send_callback(self):
        self.send_run_protocol([("protocolFile", open("basic_transfer.py", 'rb')),
                ("supportFiles", open("helpers.py", 'rb')),
                ("supportFiles", open("basic_transfer_config.json", 'rb')),
                ])
        # self.scp_send_run("opentrons2.py")

    def btn_edit_callback(self):
        if self.btn_add.isHidden():
            self.lbl_hostname.show()
            self.le_hostname.show()
            self.lbl_username.show()
            self.le_username.show()
            self.lbl_key.show()
            self.le_key.show()
            self.btn_add.show()
            self.btn_remove.show()
        else:
            self.lbl_hostname.hide()
            self.le_hostname.hide()
            self.lbl_username.hide()
            self.le_username.hide()
            self.lbl_key.hide()
            self.le_key.hide()
            self.btn_add.hide()
            self.btn_remove.hide()

    def btn_add_callback(self):
        hostname = self.le_hostname.text()
        username = self.le_username.text()
        key = self.le_key.text()
        if hostname != "" or username != "" or key != "":
            connection = OT2ConnectionData()
            connection.hostname = hostname
            connection.username = username
            connection.key = key
            self.shelf_connections.append(connection)
            self.lw_connection.addItem("Username: " + username + "  Hostname: " + hostname + "  SSH Key:  " + key)

    def btn_remove_callback(self):
        row = self.lw_connection.currentRow()
        if row != -1:
            self.lw_connection.takeItem(row)
            del self.shelf_connections[row]

    def btn_connect_callback(self):
        row = self.lw_connection.currentRow()
        if row != -1:
            self.hostname = self.shelf_connections[row].hostname
            self.username = self.shelf_connections[row].username
            self.key = self.shelf_connections[row].key
            print("changed to " + self.hostname + self.username + self.key)
            self.status_bar.showMessage("Připojeno k OT2: Username:  " + self.username + "  Hostname: " + self.hostname + "  SSH Key: " + self.key)
        else:
            self.status_bar.showMessage("Prosím vyberte OT2 ze seznamu")

    def btn_mm_callback(self):
        pass

    def btn_create_callback(self):
        pass
            
    def initUI(self):

        # setup of window
        self.setWindowTitle("DIANA Biotechnologies - Opentrons Controller")
        self.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))

        # setup of a bold font
        bold_font = QFont()
        bold_font.setBold(True)
        
        # setup of the main layout
        lyt_main = QHBoxLayout()
        lyt_main.setContentsMargins(20, 20, 20, 20)

         # Initialize tab screen
        tab_widget = QTabWidget()
        tab_connection = QWidget()
        tab_main = QWidget()
        tab_widget.resize(300,200)

        btn_edit = QPushButton()
        btn_edit.setText("Editovat spojení OT-2")
        btn_edit.clicked.connect(self.btn_edit_callback)

        self.lbl_hostname = QLabel()
        self.lbl_hostname.setText("Hostname:")
        self.lbl_hostname.hide()

        self.le_hostname = QLineEdit()
        self.le_hostname.hide()

        self.lbl_username = QLabel()
        self.lbl_username.setText("Username:")
        self.lbl_username.hide()

        self.le_username = QLineEdit()
        self.le_username.hide()

        self.lbl_key = QLabel()
        self.lbl_key.setText("SSH Keyname:")
        self.lbl_key.hide()

        self.le_key = QLineEdit()
        self.le_key.hide()

        lyt_new_connection = QHBoxLayout()
        lyt_new_connection.addWidget(self.lbl_hostname)
        lyt_new_connection.addWidget(self.le_hostname)
        lyt_new_connection.addWidget(self.lbl_username)
        lyt_new_connection.addWidget(self.le_username)
        lyt_new_connection.addWidget(self.lbl_key)
        lyt_new_connection.addWidget(self.le_key)

        self.btn_add = QPushButton()
        self.btn_add.setText("Přidej nové spojení")
        self.btn_add.hide()
        self.btn_add.clicked.connect(self.btn_add_callback)

        self.btn_remove = QPushButton()
        self.btn_remove.setText("Odeber spojení")
        self.btn_remove.hide()
        self.btn_remove.clicked.connect(self.btn_remove_callback)
        

        self.lw_connection = QListWidget()

        btn_connect = QPushButton()
        btn_connect.setText("Vyber spojení")
        btn_connect.clicked.connect(self.btn_connect_callback)

        lyt_connection = QVBoxLayout()
        lyt_connection.addWidget(btn_edit)
        lyt_connection.addLayout(lyt_new_connection)
        lyt_connection.addWidget(self.btn_add)
        lyt_connection.addWidget(self.btn_remove)
        lyt_connection.addWidget(self.lw_connection)
        lyt_connection.addWidget(btn_connect)

        tab_connection.setLayout(lyt_connection)

        lbl_img = QLabel(self)
        im_ot2 = QPixmap(os.path.join(self.cwd, "img", "img_opentrons.png"))
        lbl_img.setPixmap(im_ot2.scaled(300, 200, Qt.KeepAspectRatio))
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        

        lbl_status = QLabel()
        lbl_status.setText("Status:")
        lbl_status.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_status.setAlignment(Qt.AlignCenter)

        self.lbl_status_cur = QLabel()
        self.lbl_status_cur.setText("Disconnected")
        self.lbl_status_cur.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl_status_cur.setAlignment(Qt.AlignCenter)
        self.lbl_status_cur.setFont(bold_font)
        self.lbl_status_cur.setStyleSheet("background-color: red; color: white")
        self.lbl_status_cur.setContentsMargins(7,5,7,5)

        lyt_img = QHBoxLayout()
        lyt_img.addWidget(lbl_img)
        lyt_img.addWidget(lbl_status)
        lyt_img.addWidget(self.lbl_status_cur)

        lbl_file = QLabel()
        lbl_file.setText("Načtený soubor:")
        lbl_file.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_file.setAlignment(Qt.AlignCenter)
        lbl_file.setFont(bold_font)

        self.lbl_file_cur = QLabel()
        self.lbl_file_cur.setText("Žádný")
        self.lbl_file_cur.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl_file_cur.setAlignment(Qt.AlignCenter)
        self.lbl_file_cur.setFont(bold_font)
        self.lbl_file_cur.setStyleSheet("background-color: red; color: white")
        self.lbl_file_cur.setContentsMargins(7,5,7,5)

        lyt_file = QHBoxLayout()
        lyt_file.addWidget(lbl_file)
        lyt_file.addWidget(self.lbl_file_cur)

        lbl_tip = QLabel()
        lbl_tip.setText("Číslo pozice tip boxu:")

        self.sb_tip = QSpinBox()

        lbl_mm = QLabel()
        lbl_mm.setText("Číslo pozice Master Mixu:")

        self.sb_mm = QSpinBox()

        lbl_pcr = QLabel()
        lbl_pcr.setText("Číslo pozice PCR destičky:")

        self.sb_pcr = QSpinBox()

        lbl_rack = QLabel()
        lbl_rack.setText("Číslo pozice racku:")

        self.sb_rack = QSpinBox()

        lyt_form = QFormLayout()
        lyt_form.addRow(lbl_tip, self.sb_tip)
        lyt_form.addRow(lbl_mm, self.sb_mm)
        lyt_form.addRow(lbl_pcr, self.sb_pcr)
        lyt_form.addRow(lbl_rack, self.sb_rack)

        self.btn_mm = QPushButton()
        self.btn_mm.setText("Rozpipetuj Master Mix")
        self.btn_mm.clicked.connect(self.btn_mm_callback)

        self.btn_create = QPushButton()
        self.btn_create.setText("Vytvoř protokol")
        self.btn_create.clicked.connect(self.btn_create_callback)

        self.btn_send = QPushButton()
        self.btn_send.setText("Odešli protokol")
        self.btn_send.clicked.connect(self.btn_send_callback)

        lyt_protocol = QVBoxLayout()
        lyt_protocol.addLayout(lyt_img)
        lyt_protocol.addLayout(lyt_file)
        lyt_protocol.addLayout(lyt_form)
        lyt_protocol.addWidget(self.btn_mm)
        lyt_protocol.addWidget(self.btn_create)
        lyt_protocol.addWidget(self.btn_send)

        tab_main.setLayout(lyt_protocol)

        
        # Add tabs
        tab_widget.addTab(tab_main,"Protokoly")
        tab_widget.addTab(tab_connection,"Připojení")
        
        
        

        
        # Add tabs to widget
        lyt_main.addWidget(tab_widget)

        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        # self.setFixedSize(600,600)
        self.showMaximized()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = RetestApp()
    frame.show()
    sys.exit(app.exec_())
