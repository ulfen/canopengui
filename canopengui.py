#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CANopenGUI
A simple CANopen Object Browser
"""

import sys

try:
    from PySide.QtGui import QApplication
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            if sys.version_info.major < 3:
                import sip
                sip.setapi('QDate', 2)
                sip.setapi('QDateTime', 2)
                sip.setapi('QString', 2)
                sip.setapi('QTextStream', 2)
                sip.setapi('QTime', 2)
                sip.setapi('QUrl', 2)
                sip.setapi('QVariant', 2)
            from PyQt4.QtGui import QApplication
        except ImportError:
            sys.exit('No Python bindings for Qt found')

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
