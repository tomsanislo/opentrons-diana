#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, time
import traceback
from PyQt5.QtWidgets import QApplication, QComboBox, QFileDialog, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QMainWindow, QProgressDialog, QPushButton, QSizePolicy, QSpinBox, QStatusBar, QStyleFactory, QTabWidget, QTextBrowser, QVBoxLayout, QWidget, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import QEvent, QObject, QRunnable, QThreadPool, Qt, pyqtSignal, pyqtSlot
import shutil
from datetime import datetime


class WorkerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    save = pyqtSignal()
    num_scanned = pyqtSignal()
    initialise = pyqtSignal()

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
        self.kwargs['num_scanned_callback'] = self.signals.num_scanned
        self.kwargs['initialise_callback'] = self.signals.initialise

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


        self.setAcceptDrops(True)

        # call a function to setup the UI
        self.initUI()

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
        if len(files) > 1:
            self.show_error("Please import only one file")
        elif len(files) == 1:
            if files[0].endswith(".csv"):
                self.setStyleSheet("background-color: white")
            else:
                self.show_error("The imported file is not in the CSV format")

    

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
                self.purge_tmp()
                event.accept()
            elif answer == QMessageBox.No:
                event.ignore()
        if type == "end":
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
        
    def initUI(self):

        # setup of window
        self.setWindowTitle("Retestovací utilita")
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
        
        # Add tabs
        tab_widget.addTab(tab_connection,"Připojení")
        tab_widget.addTab(tab_main,"Protokoly")
        
        # Create first tab
        
        self.pushButton1 = QPushButton("PyQt5 button")

        lyt_cn_main = QVBoxLayout(self)
        lyt_cn_main.addWidget(self.pushButton1)


        tab_connection.setLayout(lyt_cn_main)
        
        # Add tabs to widget
        lyt_main.addWidget(tab_widget)
        self.setLayout(lyt_main)

        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        self.setFixedSize(600,600)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = RetestApp()
    frame.show()
    sys.exit(app.exec_())
