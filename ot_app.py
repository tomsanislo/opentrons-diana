#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, time, subprocess
from PyQt5.QtWidgets import QAction, QApplication, QButtonGroup, QFileDialog, QFrame, QGridLayout, QLabel, QMainWindow, QTextEdit, QWidget, QPushButton, QMenuBar, QMenu, QRadioButton, QVBoxLayout, QComboBox, QCheckBox, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QObject, Qt, pyqtSignal
import datapaq_remote as dtpq
from shutil import copy, copyfile
#import ElementTree as ET
#import pandas as pd

class ScanWin(QWidget):

    # defining vars
    mom = None
    ckb_ask = None
    ckb_state = None

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def start_scan(self):
        if self.ckb_state:
            self.mom.start_scan()
        else:
            self.show_error("Prosím potvrďte,  že rack byl položen na skener")

    def ckb_state_changed(self, ckb):
        self.ckb_state = ckb.isChecked()

    def __init__(self, mom):
        super().__init__()
        self.mom = mom
        self.resize(300, 150)
        layout = QVBoxLayout()
        lbl_method_ask = QLabel("Polož rack na skener")
        lbl_method_ask.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_method_ask)
        ckb_ask = QCheckBox("Rack položen")
        ckb_ask.setChecked(False)
        ckb_ask.stateChanged.connect(lambda:self.ckb_state_changed(ckb_ask))
        #ckb_ask.setAlignment(Qt.AlignCenter) !!!FIX
        layout.addWidget(ckb_ask)
        btn_start_scan = QPushButton("Spustit sken racku", self)
        btn_start_scan.clicked.connect(self.start_scan)
        layout.addWidget(btn_start_scan)
        self.setLayout(layout)

class StartWin(QWidget):

    # defining vars
    cb_method = None
    chosen_method = None
    mom = None

    def show_next_win(self, mom):
        self.scan_win_inst = ScanWin(self.mom)
        self.scan_win_inst.show()
        self.hide()  

    def selection_change(self,i):
        
        self.mom.lbl_method_cur.setText(self.cb_method.currentText())
        self.mom.lbl_method_cur.setStyleSheet("background-color: green; color: white")
        if self.mom.regime == "Automat":
            self.show_next_win(self.mom)


    def __init__(self, mom):
        super().__init__()
        self.mom = mom
        self.resize(300, 150)
        layout = QVBoxLayout()
        lbl_method_ask = QLabel("Zvol metodu příjmu")
        lbl_method_ask.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_method_ask)
        self.cb_method = QComboBox()
        self.cb_method.addItems(["DIANA app", "Firma", "Ežádanky", "COVIDPASS", "FYZIO"])
        self.cb_method.activated.connect(self.selection_change)
        layout.addWidget(self.cb_method)
        self.setLayout(layout)

class ScanWin(QWidget):

    # defining vars
    mom = None
    ckb_ask = None
    ckb_state = None

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def start_scan(self):
        if self.ckb_state:
            self.mom.start_scan()
        else:
            self.show_error("Prosím potvrďte,  že rack byl položen na skener")

    def ckb_state_changed(self, ckb):
        self.ckb_state = ckb.isChecked()

    def __init__(self, mom):
        super().__init__()
        self.mom = mom
        self.resize(300, 150)
        layout = QVBoxLayout()
        #layout.setAlignment(Qt.AlignCenter)
        lbl_method_ask = QLabel("Polož rack na skener")
        lbl_method_ask.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_method_ask)
        ckb_ask = QCheckBox("Rack položen")
        ckb_ask.setChecked(False)
        ckb_ask.stateChanged.connect(lambda:self.ckb_state_changed(ckb_ask))
        #ckb_ask.setAlignment(Qt.AlignCenter) !!!FIX
        layout.addWidget(ckb_ask)
        btn_start_scan = QPushButton("Spustit sken racku", self)
        btn_start_scan.clicked.connect(self.start_scan)
        layout.addWidget(btn_start_scan)
        self.setLayout(layout)

class SettingsWin(QWidget):

    # defining vars
    scan_regime = None
    regime = None
    mom = None
    rbtn_regime_auto = None
    rbtn_regime_man = None
    rbtn_regime_scan_auto = None
    rbtn_regime_scan_man = None

    def rbtn_regime(self, button):
	
      if button.text() == "Automat":
        if button.isChecked() == True:
            self.rbtn_regime_man.setChecked(False)
            self.mom.change_regime("Automat")
				
      if button.text() == "Manual":
        if button.isChecked() == True:
            self.rbtn_regime_auto.setChecked(False)
            self.mom.change_regime("Manual")
         
    def rbtn_regime_scan(self, button):
	
      if button.text() == "Automat":
        if button.isChecked() == True:
            self.rbtn_regime_scan_man.setChecked(False)
            self.mom.change_scan_regime("Automat")
				
      if button.text() == "Manual":
        if button.isChecked() == True:
            self.rbtn_regime_scan_auto.setChecked(False)
            self.mom.change_scan_regime("Manual")

    def ckb_state_changed(self, ckb):
        if ckb.isChecked():
            self.mom.te_debug.show()
        elif ckb.isChecked() == False:
            self.mom.te_debug.hide()
         
    def __init__(self, mom):
        super().__init__()
        self.setWindowTitle("Nastavení")
        self.mom = mom
        self.resize(300, 200)
        layout = QGridLayout()
        self.rbtn_regime_auto = QRadioButton("Automat")
        self.rbtn_regime_auto.setChecked(True)
        self.rbtn_regime_auto.toggled.connect(lambda:self.rbtn_regime(self.rbtn_regime_auto))
        layout.addWidget(self.rbtn_regime_auto, 1, 2)
        self.rbtn_regime_man = QRadioButton("Manual")
        self.rbtn_regime_man.setChecked(False)
        self.rbtn_regime_man.toggled.connect(lambda:self.rbtn_regime(self.rbtn_regime_man))
        layout.addWidget(self.rbtn_regime_man, 1, 3)
        self.rbtn_regime_scan_auto = QRadioButton("Automat")
        self.rbtn_regime_scan_auto.setChecked(True)
        self.rbtn_regime_scan_auto.toggled.connect(lambda:self.rbtn_regime_scan(self.rbtn_regime_scan_auto))
        layout.addWidget(self.rbtn_regime_scan_auto, 2, 2)
        self.rbtn_regime_scan_man = QRadioButton("Manual")
        self.rbtn_regime_scan_man.setChecked(False)
        self.rbtn_regime_scan_man.toggled.connect(lambda:self.rbtn_regime_scan(self.rbtn_regime_scan_man))
        layout.addWidget(self.rbtn_regime_scan_man, 2, 3)
        grp_regime = QButtonGroup(self)
        grp_regime.addButton(self.rbtn_regime_auto)
        grp_regime.addButton(self.rbtn_regime_man)
        grp_regime_scan = QButtonGroup(self)
        grp_regime_scan.addButton(self.rbtn_regime_scan_auto)
        grp_regime_scan.addButton(self.rbtn_regime_scan_man)
        lbl_regime = QLabel("Režim příjmu")
        lbl_regime.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_regime, 1, 1)
        lbl_regime_scan = QLabel("Režim scanu")
        lbl_regime_scan.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_regime_scan, 2, 1)
        lbl_debug = QLabel("Debug mód")
        lbl_debug.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_debug, 3, 1)
        ckb_ask = QCheckBox()
        ckb_ask.setChecked(False)
        ckb_ask.stateChanged.connect(lambda:self.ckb_state_changed(ckb_ask))
        layout.addWidget(ckb_ask, 3, 2)
        self.setLayout(layout)


class PrijemUtil(QMainWindow):

    # defining vars
    cwd = None
    app = None
    screen = None
    screen_width = None
    chs_com = "Žádná vybraná metoda"
    lbl_scan = None
    scan_regime = "Automat"
    regime = "Automat"
    btn_start = None
    btn_change_method = None
    btn_scan = None
    btn_file = None
    te_debug = None
    scan_filename = None
    compare_filename = None
    save_filename = None

    def __init__(self):
        super().__init__()
        
         # defining paths
        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))

        self.create_menu_bar()
        menu_bar = self.menuBar()


        self.initUI()

    def openScanFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","CSV Soubory (*.csv);;Všechny soubory (*)", options=options)
        if fileName:
            self.scan_filename = fileName
            self.lbl_scan.setText(fileName)
            self.lbl_scan.setStyleSheet("background-color:green")

    def openCompareFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","CSV Soubory (*.csv);;Všechny soubory (*)", options=options)
        if fileName:
            self.compare_filename = fileName
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            copyfile(os.path.join(self.cwd, "tmp", self.save_filename), fileName)



    def change_regime(self, regime):
        if regime == "Automat":
            self.regime = "Automat"
            self.btn_start.setEnabled(True)
            self.btn_start.setStyleSheet("background-color: green; color: white");
            self.btn_change_method.setEnabled(False)
            self.btn_scan.setEnabled(False)
            self.btn_file.setEnabled(False)
        if regime == "Manual":
            self.regime = "Manual"
            self.btn_start.setEnabled(False)
            self.btn_start.setStyleSheet("background-color: black; color: white");
            self.btn_change_method.setEnabled(True)
            self.btn_scan.setEnabled(True)
            self.btn_file.setEnabled(True)


    def change_scan_regime(self, regime):
        if regime == "Automat":
            self.scan_regime = "Automat"
            self.lbl_scan.setText("Zapni sken racku")
            self.btn_scan.setText("Zapni sken")
        if regime == "Manual":
            self.scan_regime = "Manual"
            self.lbl_scan.setText("Vlož soubor ze skeneru")
            self.btn_scan.setText("Vlož soubor")

     # defining a function to be called when the user attempts to close the window
    def closeEvent(self, event):
        self.quit_app("normal", event)
        
    # defining a function that asks the user if they really want to close the app
    def quit_app(self, type, event):
        print("quit called")
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



    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_prijem.ico"))))
        msg.setText(message)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("&Soubor")
        edit_menu = menu_bar.addMenu("&Úpravy")
        help_menu = menu_bar.addMenu("&Pomoc")

        settings_action = QAction("&Nastavení", self)
        settings_action.setShortcut("Ctrl+I")
        settings_action.setStatusTip("Změň nastavení aplikace")
        edit_menu.triggered[QAction].connect(self.edit_called)
        edit_menu.addAction(settings_action)

        quit_action = QAction("&Ukončit", self)
        quit_action.setShortcut("Ctrl+H")
        quit_action.setStatusTip("Ukonči aplikaci")
        file_menu.triggered[QAction].connect(self.file_called)
        file_menu.addAction(quit_action)

        help_action = QAction("&README", self)
        help_action.setShortcut("Ctrl+Q")
        help_action.setStatusTip("Otevři README soubor na pomoc")
        help_menu.triggered[QAction].connect(self.help_called)
        help_menu.addAction(help_action)

        self.setMenuBar(menu_bar)

    def edit_called(self, action):
        if action.text() == "&Nastavení":
            self.settings_win_inst = SettingsWin(self)
            self.settings_win_inst.show()

    def file_called(self, action):
        if action.text() == "&Ukončit":
            self.quit_app()
            
    def help_called(self, action):
        if action.text() == "&README":
            print("help")

    
    def load_scan_file(self, filename):
        print(filename)
        print(os.path.join(os.getcwd(), "tmp", "tmp_scan_file.csv"))
        #try:
        copy(filename, os.path.join(os.getcwd(), "tmp", "tmp_scan_file.csv"))
       # except:
            #self.show_error("Chyba v kopírování souboru")

    def start_click_callback(self):
        print("starting scan")
        self.start_win_inst = StartWin(self)
        self.start_win_inst.show()

    def scan_click_callback(self):
        if self.scan_regime == "Automat":
            print("starting příjem")
            self.scan_win_inst = ScanWin(self)
            self.scan_win_inst.show()
        elif self.scan_regime == "Manual":
            print("opening ask open file dialog")
            print(self.cwd)
            self.load_scan_file(self.openScanFileNameDialog())
        
        

    def method_click_callback(self):
        self.start_win_inst = StartWin(self)
        self.start_win_inst.show()   

    def file_click_callback(self):
        self.openFileNameDialog()


    def initUI(self):

        self.setWindowTitle("Příjmová utilita")
        self.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_prijem.ico"))))

        widget = QWidget()
        lyt_grid = QGridLayout()
        widget.setLayout(lyt_grid)
        self.setCentralWidget(widget)

        lbl_logo = QLabel(self)
        im_logo = QPixmap(os.path.join(self.cwd, "img", "logo.png"))
        lbl_logo.setPixmap(im_logo.scaled(300, 200, Qt.KeepAspectRatio))
        lbl_logo.setAlignment(Qt.AlignCenter)

        lbl_change_method = QLabel(self)
        lbl_change_method.setText("Vyber firmu")
        lbl_change_method.setAlignment(Qt.AlignCenter)

        self.lbl_scan = QLabel(self)
        self.lbl_scan.setText("Vlož soubor ze skeneru")
        self.lbl_scan.setAlignment(Qt.AlignCenter)

        lbl_file = QLabel(self)
        lbl_file.setText("Vlož párovací soubor od firmy")
        lbl_file.setAlignment(Qt.AlignCenter)

        lyt_grid.addWidget(lbl_logo, 1,1)
        lyt_grid.addWidget(lbl_change_method, 3,1)
        lyt_grid.addWidget(self.lbl_scan, 5, 1)
        lyt_grid.addWidget(lbl_file, 7, 1)

        self.lbl_scan = QLabel(self)
        self.lbl_scan.setText(self.chs_com)
        self.lbl_scan.setAlignment(Qt.AlignCenter)

        lbl_scan_cur = QLabel(self)
        lbl_scan_cur.setText("Žádný vybraný soubor")
        lbl_scan_cur.setAlignment(Qt.AlignCenter)

        lbl_file_cur = QLabel(self)
        lbl_file_cur.setText("Žádný vybraný soubor")
        lbl_file_cur.setAlignment(Qt.AlignCenter)

        lyt_grid.addWidget(self.lbl_scan, 3, 2, 1, 2)
        lyt_grid.addWidget(lbl_scan_cur, 5, 2, 1, 2)
        lyt_grid.addWidget(lbl_file_cur, 7, 2, 1, 2)

        vline_left = QFrame(self)
        vline_left.setFrameShape(QFrame.VLine)
        vline_left.setFrameShadow(QFrame.Sunken)
        vline_left.setLineWidth(2)

        vline_right = QFrame(self)
        vline_right.setFrameShape(QFrame.VLine)
        vline_right.setFrameShadow(QFrame.Sunken)
        vline_right.setLineWidth(2)

        lyt_grid.addWidget(vline_left, 2, 0, 7, 1)
        lyt_grid.addWidget(vline_right, 2, 5, 7, 1)

        hline_method = QFrame(self)
        hline_method.setFrameShape(QFrame.HLine)
        hline_method.setFrameShadow(QFrame.Sunken)
        hline_method.setLineWidth(2)

        hline_scan = QFrame(self)
        hline_scan.setFrameShape(QFrame.HLine)
        hline_scan.setFrameShadow(QFrame.Sunken)
        hline_scan.setLineWidth(2)

        hline_file = QFrame(self)
        hline_file.setFrameShape(QFrame.HLine)
        hline_file.setFrameShadow(QFrame.Sunken)
        hline_file.setLineWidth(2)

        hline_regime = QFrame(self)
        hline_regime.setFrameShape(QFrame.HLine)
        hline_regime.setFrameShadow(QFrame.Sunken)
        hline_regime.setLineWidth(2)

        lyt_grid.addWidget(hline_method, 2, 1, 1, 4)
        lyt_grid.addWidget(hline_scan, 4, 1, 1, 4)
        lyt_grid.addWidget(hline_file, 6, 1, 1, 4)
        lyt_grid.addWidget(hline_regime, 8, 1, 1, 4)
        
        self.btn_start = QPushButton("Spusti příjem", self)
        self.btn_start.setStyleSheet("background-color: green; color: white")
        self.btn_start.clicked.connect(self.start_click_callback)

        self.btn_change_method = QPushButton("Změň metodu", self)
        self.btn_change_method.setEnabled(False)
        self.btn_change_method.clicked.connect(self.method_click_callback)

        self.btn_scan = QPushButton("Vlož soubor", self)
        self.btn_scan.setEnabled(False)
        self.btn_scan.clicked.connect(self.openScanFileNameDialog)

        self.btn_file = QPushButton("Vlož soubor", self)
        self.btn_file.clicked.connect(self.openCompareFileNameDialog)
        self.btn_file.setEnabled(False)

        lyt_grid.addWidget(self.btn_start, 1, 4)
        lyt_grid.addWidget(self.btn_change_method, 3, 4)
        lyt_grid.addWidget(self.btn_scan, 5, 4)
        lyt_grid.addWidget(self.btn_file, 7, 4)

        self.te_debug = QTextEdit(self)
        self.te_debug.setReadOnly(True)
        self.te_debug.hide()

        lyt_grid.addWidget(self.te_debug, 9, 1, 1, 4)

        self.showMaximized()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = PrijemUtil()
    sys.exit(app.exec_())