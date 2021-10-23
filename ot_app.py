#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, time
import traceback
from PyQt5.QtWidgets import QApplication, QComboBox, QFileDialog, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QMainWindow, QProgressDialog, QPushButton, QSizePolicy, QSpinBox, QStatusBar, QStyleFactory, QTextBrowser, QVBoxLayout, QWidget, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import QEvent, QObject, QRunnable, QThreadPool, Qt, pyqtSignal, pyqtSlot
import shutil
from datetime import datetime

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class ScannerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    save = pyqtSignal()
    num_scanned = pyqtSignal()
    initialise = pyqtSignal()

class Scanner(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Scanner, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ScannerSignals()

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

class ScanUtil(QMainWindow):

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

        self.initialise_dtpq()

        # call a function to setup the UI
        self.initUI()
    

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
            msg.setWindowTitle("Ukončení aplikace")
            msg.setText("Chceš skutečně ukončit aplikaci?")
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
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("color: black")
        msg.exec_()

    # defining a function that shows a success message
    def show_success(self, message):
        msg = QMessageBox()
        msg.setIconPixmap(QPixmap(os.path.join(self.cwd, "img", "success.png")).scaled(50, 50, Qt.KeepAspectRatio))
        msg.setText(message)
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
        msg.setWindowTitle("Hotovo")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("background-color: white;")
        msg.exec_()

    # defining a function that responds to the combo box
    def cb_com_callback(self,i):
        self.chs_com = self.cb_com.currentText()
        if self.chs_com == "":
            self.btn_com.setEnabled(False)
            self.le_cust.setText("")
            self.le_cust.hide()
        elif self.chs_com == "Custom":
            self.le_cust.show()
            self.btn_com.setEnabled(False)
        else:
            self.le_cust.setText("")
            self.le_cust.hide()
            self.btn_com.setEnabled(True)

    def le_cust_change_callback(self):
        self.chs_com = self.le_cust.text()
        if self.chs_com == "":
            self.btn_com.setEnabled(False)
        else:
            self.btn_com.setEnabled(True)

    # defining a function that responds to a button click
    def btn_com_click_callback(self):
        self.cb_com.setEnabled(False)
        self.cb_com.setStyleSheet("background-color: green; color: white")
        self.btn_com.setEnabled(False)
        self.sb_num.setEnabled(True)
        self.filename_save = datetime.now().strftime("%Y%m%d") + "_DL_prijem_" + self.chs_com + ".csv"
        self.statusBar().showMessage("Vytvářím nový soubor " + self.filename_save)
        with open(os.path.join(self.cwd, "tmp", self.filename_save), "w") as f1:
            pass
        
    # defining a function that responds to a change in the spin box
    def sp_num_callback(self):
        self.chs_num_racks = self.sb_num.value()
        if self.chs_num_racks == 0:
            self.btn_num.setEnabled(False)
        else:
            self.btn_num.setEnabled(True)

    # defining a function that responds to a button click
    def btn_num_callback(self):
        try:
            self.sb_num.setEnabled(False)
            self.sb_num.setStyleSheet("background-color: green; color: white")
            self.le_rackid.setEnabled(True)
            self.le_rackid.setFocus()
            self.btn_num.setEnabled(False)
            self.statusBar().showMessage("Počet racků je " + str(self.chs_num_racks))
        except:
            self.show_error("Server neodpovídá")

    # defining a function that responds to hitting of enter key in line edit
    def le_enter_callback(self):
        if self.le_rackid.text() != "":
            self.chs_rackid = self.le_rackid.text()
            self.btn_scan.setEnabled(False)
            self.scan_click_callback()

    # defining a function that responds to a change in th line edit
    def le_change_callback(self):
        if self.le_rackid.text() != "":
            self.chs_rackid = self.le_rackid.text()
            self.btn_scan.setEnabled(True)
        else:
            self.btn_scan.setEnabled(False)

    # defining a function that responds to a button click
    def scan_click_callback(self):
        self.btn_scan.setEnabled(False)
        scanner = Scanner(self.scan_racks, self.cwd, self.num_scanned, self.chs_num_racks, self.chs_rackid) # Any other args, kwargs are passed to the run function
        scanner.signals.result.connect(self.scan_output)
        scanner.signals.finished.connect(self.scan_complete)
        scanner.signals.progress.connect(self.scan_progress)
        scanner.signals.initialise.connect(self.initialise_dtpq)
        scanner.signals.num_scanned.connect(self.num_scanned_up)
        self.create_progress_dialog("Sken racku", "Probíhá sken racku, prosím vyčkejte")  
        self.scan_progress(0)
        self.pb_dialog.show()
        self.threadpool.start(scanner)

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


    def scan_progress(self, done_percentage):
        self.pb_dialog.setValue(done_percentage)

            
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

    def scan_output(self, string):
        self.le_rackid.setText("")
        self.btn_scan.setEnabled(True)
        self.btn_scan.setStyleSheet("background-color: green; color: white")
        self.lbl_rackid.setText(self.chs_rackid)
        self.lbl_rackid.setStyleSheet("color: green")
        if string is not None:
            string = string.splitlines()
            line_array = []
            lines_com = ""
            df = False
            for line in string:
                if line.startswith("20"):
                    line_array.append(line)
            array_index = 0
            et_count = 0
            sc_count = 0
            for index_y in range(8):
                y_list = self.rack_pos[index_y]
                for index_x in range(12):
                    lines_com = lines_com + "\n" + line_array[array_index].replace(";0;", ";" + self.chs_rackid + ";")
                    if line_array[array_index].endswith("EMPTY"):
                        y_list[11 - index_x].setText("EMPTY")
                        y_list[11 - index_x].setStyleSheet("background-color: #BEBEBE; color: white")
                        et_count = et_count + 1
                    elif line_array[array_index].endswith("FAILURE"):
                        df = True
                        y_list[11 - index_x].setText("DF")
                        y_list[11 - index_x].setStyleSheet("background-color: red; color: white")
                    elif not line_array[array_index].endswith("EMPTY"):
                        y_list[11 - index_x].setText("OK")
                        y_list[11 - index_x].setStyleSheet("background-color: green; color: white")
                        sc_count = sc_count + 1
                    
                    array_index = array_index + 1

            if not df:
                if et_count == 96:
                    lbl_num = QLabel(self)
                    lbl_num.setText(str(self.num_scanned) + "   ("  + str(sc_count) + " ks)")
                    lbl_num.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    lbl_num.setAlignment(Qt.AlignCenter)
                    lbl_rackid = QLabel(self)
                    lbl_rackid.setText(self.chs_rackid)
                    lbl_rackid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    lbl_rackid.setAlignment(Qt.AlignCenter)
                    lbl_rackid.setStyleSheet("background-color: blue; color: white")
                    self.lyt_form.addRow(lbl_num, lbl_rackid)
                    self.show_error("EMPTY RACK\nProsím naskenujte rack ještě jednou")
                else:

                    if self.chs_num_racks == 1:
                        self.num_scanned_up()
                        self.lbl_form_count.setText(str(sc_count))   
                        self.lbl_form_count_all.setText(str(sc_count))                  
                        with open(os.path.join(self.cwd, "tmp", self.filename_save), "a") as f:
                            f.writelines(lines_com[1 : ])
                        self.scan_progress(66)
                        time.sleep(1)
                        self.save_file()
                        
                    if self.chs_num_racks != 1:
                        self.num_scanned_up()
                        self.count_all = self.count_all + sc_count
                        self.lbl_form_count.setText(str(sc_count)) 
                        self.lbl_form_count_all.setText(str(self.count_all)) 
                        with open(os.path.join(self.cwd, "tmp", self.filename_save), "a") as f:
                            f.writelines(lines_com[1 : ] + "\n")
                        self.scan_progress(66)
                        time.sleep(1)
                        if self.num_scanned - 1 == self.chs_num_racks:
                            self.save_file()
                    lbl_num = QLabel(self)
                    lbl_num.setText(str(self.num_scanned - 1) + "   ("  + str(sc_count) + " ks)")
                    lbl_num.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    lbl_num.setAlignment(Qt.AlignCenter)
                    lbl_rackid = QLabel(self)
                    lbl_rackid.setText(self.chs_rackid)
                    lbl_rackid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    lbl_rackid.setAlignment(Qt.AlignCenter)
                    lbl_rackid.setStyleSheet("background-color: green; color: white")
                    self.lyt_form.addRow(lbl_num, lbl_rackid)
                    
                    
            else:
                lbl_num = QLabel(self)
                lbl_num.setText(str(self.num_scanned))
                lbl_num.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                lbl_num.setAlignment(Qt.AlignCenter)
                lbl_rackid = QLabel(self)
                lbl_rackid.setText(self.chs_rackid)
                lbl_rackid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                lbl_rackid.setAlignment(Qt.AlignCenter)
                lbl_rackid.setStyleSheet("background-color: red; color: white")
                self.lyt_form.addRow(lbl_num, lbl_rackid)
                self.show_error("DECODE FAILURE\nProsím naskenujte rack ještě jednou.")
        else:
            self.show_error("Chyba skenování\nProsím naskenujte rack ještě jednou.")

   
    def scan_complete(self):
        self.scan_progress(100)
        
    
    def num_scanned_up(self):
        self.num_scanned = self.num_scanned + 1

    def initialise_dtpq(self):
        self.dtpq = datapaq_remote.DataPaqRemote()
        try:
            self.dtpq.initialise()
        except:
            self.show_error("Server nebyl spuštěn\nProsím spusťte server.bat na ploše.")
        print("Status = " + self.dtpq.getStatus())

    def scan_racks(self, cwd, num_scanned, num_racks, rackid, progress_callback, initialise_callback, num_scanned_callback):
        progress_callback.emit(33)
        scan_data = self.dtpq.scanRack("1")
        return scan_data
        

        
    def initUI(self):

        # setup of window
        self.setWindowTitle("Skenovací utilita")
        self.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
        self.setStyle(QStyleFactory.create("Windows"))

        # setup of a bold font
        bold_font = QFont()
        bold_font.setBold(True)

        # setup of the central label
        lbl_company = QLabel(self)
        lbl_company.setText("Vyber firmu")
        lbl_company.setAlignment(Qt.AlignCenter)
        lbl_company.setStyleSheet("font-size: 17px")
        lbl_company.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lbl_company.setAlignment(Qt.AlignCenter)
        lbl_company.setFont(bold_font)

       # setup of the combo box for selecting a company
        self.cb_com = QComboBox()
        self.cb_com.addItems(["", "AVCR", "BATIST", "BENEFITY", "COVPAS", "CPKOLIN", "DIANA", "ELI", "FDENT", "FERRING", "FYZIO", "LAPUTYKA", "POS", "RENTURI", "RETEST", "S2T", "SFMD", "SFMDOP", "ZENTIVA", "Custom"])
        self.cb_com.activated.connect(self.cb_com_callback)
        self.cb_com.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # setup of the line edit
        self.le_cust = QLineEdit()
        self.le_cust.hide()
        self.le_cust.textEdited.connect(self.le_cust_change_callback)

        # setup of the button to finish setting the company name
        self.btn_com = QPushButton("Ulož firmu", self)
        self.btn_com.clicked.connect(self.btn_com_click_callback)
        self.btn_com.setEnabled(False)

        # setup of label that shows the user where to input the number of racks
        lbl_racks = QLabel(self)
        lbl_racks.setText("Vyber počet racků")
        lbl_racks.setAlignment(Qt.AlignCenter)
        lbl_racks.setStyleSheet("font-size: 17px")
        lbl_racks.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lbl_racks.setFont(bold_font)

        # setup of the spin box for selecting the number of racks
        self.sb_num = QSpinBox()
        self.sb_num.valueChanged.connect(self.sp_num_callback)
        self.sb_num.setEnabled(False)
        
        # setup of the button to finish setting the number of racks
        self.btn_num = QPushButton("Ulož počet racků", self)
        self.btn_num.clicked.connect(self.btn_num_callback)
        self.btn_num.setEnabled(False)

        # setup of the label to inform the user to scan the rack id
        lbl_scan = QLabel(self)
        lbl_scan.setText("Naskenuj Rack ID")
        lbl_scan.setAlignment(Qt.AlignCenter)
        lbl_scan.setStyleSheet("font-size: 17px")
        lbl_scan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lbl_scan.setFont(bold_font)
        
        # setup of the line edit
        self.le_rackid = QLineEdit()
        self.le_rackid.setEnabled(False)
        self.le_rackid.returnPressed.connect(self.le_enter_callback)
        self.le_rackid.textEdited.connect(self.le_change_callback)

        # setup of the button to start a scan
        self.btn_scan = QPushButton("Start skenu", self)
        self.btn_scan.clicked.connect(self.scan_click_callback)
        self.btn_scan.setEnabled(False)

        # setup of the button to ask to save
        self.btn_save = QPushButton("Ulož soubor dodatečně", self)
        self.btn_save.clicked.connect(self.save_file)
        self.btn_save.setEnabled(False)
        self.btn_save.hide()


        # defining a central layout and adding widgets to it
        lyt_left = QVBoxLayout()
        lyt_left.addWidget(lbl_company)
        lyt_left.addWidget(self.cb_com)
        lyt_left.addWidget(self.le_cust)
        lyt_left.addWidget(self.btn_com)
        lyt_left.addWidget(lbl_racks)
        lyt_left.addWidget(self.sb_num)
        lyt_left.addWidget(self.btn_num)
        lyt_left.addWidget(lbl_scan)
        lyt_left.addWidget(self.le_rackid)
        lyt_left.addWidget(self.btn_scan)
        lyt_left.addWidget(self.btn_save)

        # setup of a rackid title label
        lbl_rackid_title = QLabel(self)
        lbl_rackid_title.setText("Rack ID:")

        self.lbl_rackid = QLabel(self)
        self.lbl_rackid.setText("EMPTY")
        self.lbl_rackid.setStyleSheet("color: red")
        self.lbl_rackid.setFont(bold_font)
        
        # setup of a rackid title layout
        lyt_rackid = QHBoxLayout()
        lyt_rackid.addWidget(lbl_rackid_title)
        lyt_rackid.addWidget(self.lbl_rackid)

        # setup of a rack widget
        self.rack_pos = []
        self.pos_x_list = ["A", "B", "C", "D", "E", "F", "G", "H"]
        lyt_table = QGridLayout()
        for pos_y in range(8):
            y_list = []
            for pos_x in range(12):
                y_list.append(QLabel(self))
                y_list[pos_x].setText("EMPTY")
                y_list[pos_x].setMinimumSize(y_list[pos_x].sizeHint().width(), y_list[pos_x].sizeHint().width())
                y_list[pos_x].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                y_list[pos_x].setAlignment(Qt.AlignCenter)
                y_list[pos_x].setStyleSheet("background-color: #BEBEBE; color: white")
                lyt_table.addWidget(y_list[pos_x], pos_x + 1, pos_y + 1)
            self.rack_pos.append(y_list)

        for pos_x in range(8):
            x_label = QLabel()
            x_label.setText(self.pos_x_list[pos_x])
            x_label.setAlignment(Qt.AlignCenter)
            x_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            x_label.setAlignment(Qt.AlignCenter)
            lyt_table.addWidget(x_label, 13, pos_x + 1)

        for pos_y in range(12):
            y_label = QLabel()
            y_label.setText(str(pos_y + 1))
            y_label.setAlignment(Qt.AlignCenter)
            lyt_table.addWidget(y_label, 12 - pos_y , 12)

        lyt_middle = QVBoxLayout()
        lyt_middle.addLayout(lyt_rackid)
        lyt_middle.addLayout(lyt_table, 2)

        # setup of a count title label
        lbl_form_count_title = QLabel(self)
        lbl_form_count_title.setText("Počet vialek v racku")
        lbl_form_count_title.setFont(bold_font)
        lbl_form_count_title.setAlignment(Qt.AlignCenter)
        lbl_form_count_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # setup of a count_all title label
        lbl_form_count_all_title = QLabel(self)
        lbl_form_count_all_title.setText("Počet všech vialek")
        lbl_form_count_all_title.setFont(bold_font)
        lbl_form_count_all_title.setAlignment(Qt.AlignCenter)
        lbl_form_count_all_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # setup of a count label
        self.lbl_form_count = QLabel(self)
        self.lbl_form_count.setText("0")
        self.lbl_form_count.setAlignment(Qt.AlignCenter)
        self.lbl_form_count.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # setup of a count_all label
        self.lbl_form_count_all = QLabel(self)
        self.lbl_form_count_all.setText("0")
        self.lbl_form_count_all.setAlignment(Qt.AlignCenter)
        self.lbl_form_count_all.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lbl_form_num = QLabel(self)
        lbl_form_num.setText("Číslo skenu")
        lbl_form_num.setFont(bold_font)
        lbl_form_num.setAlignment(Qt.AlignCenter)
        lbl_form_num.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lbl_form_id = QLabel(self)
        lbl_form_id.setText("RackID")
        lbl_form_id.setFont(bold_font)
        lbl_form_id.setAlignment(Qt.AlignCenter)
        lbl_form_id.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.lyt_form = QFormLayout()
        self.lyt_form.addRow(lbl_form_count_title, lbl_form_count_all_title)
        self.lyt_form.addRow(self.lbl_form_count, self.lbl_form_count_all)
        self.lyt_form.addRow(lbl_form_num, lbl_form_id)
        self.lyt_form.setAlignment(Qt.AlignCenter)

        
        self.tb_racks = QTextBrowser(self)
        self.tb_racks.hide()
        
        # setup of the main layout
        lyt_main = QHBoxLayout()
        lyt_main.setAlignment(Qt.AlignCenter)
        lyt_main.addLayout(lyt_left)
        lyt_main.addSpacing(100)
        lyt_main.addLayout(lyt_middle)
        lyt_main.addSpacing(100)
        lyt_main.addWidget(self.tb_racks)
        lyt_main.addSpacing(100)
        lyt_main.addLayout(self.lyt_form)
        lyt_main.setContentsMargins(20, 20, 20, 20)

        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        self.setFixedSize(1200,600)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = ScanUtil()
    frame.show()
    sys.exit(app.exec_())
