#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget,QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import ot_app as ot_app

class LaunchUtil(QWidget):

    # defining vars
    cwd = None

    # defining an initilization function
    def __init__(self):
        super().__init__()
        
       # defining paths
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))
            
        self.initUI()

        


    # defining vars
    easter_clicked = 0

    # defining a function that responds to a click
    def prijem_click_callback(self):
        self.show_error("Tato funkcionalita je zatím nedostupná")
        #self.prijem_util_inst = prijem_util.PrijemUtil()
        #self.prijem_util_inst.show()

    # defining a function that responds to a click
    def snip_click_callback(self):
        self.snip_util_inst = snip_util.SnipUtil(app.primaryScreen().size().width())
        self.snip_util_inst.show()

    # defining a function that responds to a click
    def scan_click_callback(self):
        self.scan_util_inst = scan_util.ScanUtil()
        self.scan_util_inst.show()

     # defining a function that responds to a click
    def retest_click_callback(self):
        self.retest_inst = ot_app.RetestApp()
        self.retest_inst.show()

    # defining a function that shows the easter egg
    def show_easter_egg(self, event):
        if self.easter_clicked >= 2:
            msg = QMessageBox()
            msg.setIconPixmap(QPixmap(os.path.join(self.cwd, "img", "ic_launcher.ico")).scaled(50, 50, Qt.KeepAspectRatio))
            msg.setText("Tyto aplikace byly vytvořeny Tomášem Sanislem z DIANA LABU\n- 2021 -")
            msg.setWindowTitle("Příjem DIANA LAB - info")
            btn_thank = QPushButton("Děkuji", self)
            msg.addButton(btn_thank, QMessageBox.YesRole)
            msg.exec_()
            self.easter_clicked = 0
        else:
            self.easter_clicked = self.easter_clicked + 1

    # defining a function that shows error message
    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("color: black")
        msg.exec_()

    def initUI(self):
            
        # window setup
        self.setWindowTitle("Launcher příjmových utilit - DIANA LAB")
        self.setWindowIcon(QIcon(os.path.join(self.cwd, "img", "ic_launcher.ico")))

        # define buttons
        btn_scan = QPushButton("Skenovací utilita", self)
        btn_scan.setIcon(QIcon(os.path.join(self.cwd, "img", "ic_scan.ico")))
        btn_prijem = QPushButton("Příjem", self)
        btn_prijem.setIcon(QIcon(os.path.join(self.cwd, "img", "ic_prijem.ico")))
        btn_snip = QPushButton("Odstraň středníky", self)
        btn_snip.setIcon(QIcon(os.path.join(self.cwd, "img", "ic_snip.ico")))
        btn_retest = QPushButton("Retest vzorků", self)
        btn_retest.setIcon(QIcon(os.path.join(self.cwd, "img", "ic_snip.ico")))

        # define a horizontal box to hold buttons
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(btn_scan)
        hbox_btns.addWidget(btn_prijem)
        hbox_btns.addWidget(btn_snip)
        hbox_btns.addWidget(btn_retest)

        # define a vertical box to hold an image
        vbox_img = QVBoxLayout()

        # define a label to hold an image
        lbl_logo = QLabel(self)
        im_logo = QPixmap(os.path.join(self.cwd, "img", "logo.png"))
        lbl_logo.setPixmap(im_logo.scaled(300, 200, Qt.KeepAspectRatio))
        lbl_logo.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        lbl_logo.mousePressEvent = self.show_easter_egg

        # add objects to b
        vbox_img.addWidget(lbl_logo)
        vbox_img.addLayout(hbox_btns)
        
        # define on click events for buttons
        #btn_scan.setStyleSheet("background-color: red; color: white");
        # btn_scan.clicked.connect(self.scan_click_callback)
        # #btn_prijem.setStyleSheet("background-color: yellow; color: black");
        # btn_prijem.clicked.connect(self.prijem_click_callback)
        # #btn_snip.setStyleSheet("background-color: blue; color: white");
        # btn_snip.clicked.connect(self.snip_click_callback)
        # btn_retest.setStyleSheet("background-color: blue; color: white");
        btn_retest.clicked.connect(self.retest_click_callback)

        # final setup of window
        self.setLayout(vbox_img)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = LaunchUtil()
    frame.show()
    sys.exit(app.exec_())