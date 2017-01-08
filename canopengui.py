#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CANopenGUI
A simple CANopen Object Browser
"""

import sys

from PyQt5.QtWidgets import QApplication

from ui.mainwindow import MainWindow

def main(argv=None):
    if argv is None:
        argv = sys.argv
    app = QApplication(argv)
    app.setApplicationName('CANopenGUI')
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
