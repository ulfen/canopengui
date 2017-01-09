#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CAN Interface Settings Dialog
"""

try:
    from PySide.QtCore import Qt
    from PySide.QtCore import Slot
    from PySide.QtGui import QDialog
    from .pyside_loadUiType import loadUiType
except ImportError:
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtCore import pyqtSlot as Slot
        from PyQt5.QtWidgets import QDialog
        from PyQt5.uic import loadUiType
    except ImportError:
        from PyQt4.QtCore import Qt
        from PyQt4.QtCore import pyqtSlot as Slot
        from PyQt4.QtGui import QDialog
        from PyQt4.uic import loadUiType

import can

# --

canopen_bitrates = {
    1000:'1000 kbit/s',
    800:'800 kbit/s',
    500:'500 kbit/s',
    250:'250 kbit/s',
    125:'125 kbit/s',
    100:'100 kbit/s',
    50:'50 kbit/s',
    20:'20 kbit/s',
    10:'10 kbit/s',
}

# ----------

class InterfaceDialog(QDialog):

    def __init__(self, parent=None):
        super(InterfaceDialog, self).__init__(parent)

        Ui_Class, _ = loadUiType('ui/interfacedialog.ui')
        self.ui = Ui_Class()
        self.ui.setupUi(self)

        self.ui.comboBox_interface.addItems(sorted(can.interfaces.interface.VALID_INTERFACES))
        self.set_bitrates(canopen_bitrates)
        self.selection = {}

        cfg = can.util.load_config()
        if cfg['interface']:
            index = self.ui.comboBox_interface.findText(
                cfg['interface'],
                flags=Qt.MatchFlag(Qt.MatchFixedString))
            if index >= 0:
                self.ui.comboBox_interface.setCurrentIndex(index)
                if cfg['channel']:
                    index = self.ui.comboBox_channel.findText(
                        cfg['channel'],
                        flags=Qt.MatchFlag(Qt.MatchFixedString))
                    if index >= 0:
                        self.ui.comboBox_channel.setCurrentIndex(index)
                    else:
                        self.ui.comboBox_channel.setCurrentText(cfg['channel'])

    def set_bitrates(self, bitrates):
        self.ui.comboBox_bitrate.clear()
        self.ui.comboBox_bitrate.addItems([canopen_bitrates[baud] for baud in sorted(bitrates, reverse=True)])

    def select_bitrate(self, bitrate):
        if bitrate in canopen_bitrates:
            text = canopen_bitrates[bitrate]
            index = self.ui.comboBox_bitrate.findText(text)
            self.ui.comboBox_bitrate.setCurrentIndex(index)

    @Slot(str)
    def on_comboBox_interface_currentIndexChanged(self, text):
        self.ui.comboBox_channel.clear()

        if text=='pcan':
            self.ui.comboBox_channel.addItems(
                ['PCAN_USBBUS1', 'PCAN_USBBUS2', 'PCAN_USBBUS3', 'PCAN_USBBUS4',
                 'PCAN_USBBUS5', 'PCAN_USBBUS6', 'PCAN_USBBUS7', 'PCAN_USBBUS8',
                 'PCAN_ISABUS1', 'PCAN_ISABUS2', 'PCAN_ISABUS3', 'PCAN_ISABUS4',
                 'PCAN_ISABUS5', 'PCAN_ISABUS6', 'PCAN_ISABUS7', 'PCAN_ISABUS8',
                 'PCAN_DNGBUS1',
                 'PCAN_PCIBUS1', 'PCAN_PCIBUS2', 'PCAN_PCIBUS3', 'PCAN_PCIBUS4',
                 'PCAN_PCIBUS5', 'PCAN_PCIBUS6', 'PCAN_PCIBUS7', 'PCAN_PCIBUS8',
                 'PCAN_PCCBUS1', 'PCAN_PCCBUS2'])

        cfg = can.util.load_config()
        if cfg['interface']==text:
            index = self.ui.comboBox_channel.findText(
                cfg['channel'],
                flags=Qt.MatchFlag(Qt.MatchFixedString))
            if index >= 0:
                self.ui.comboBox_channel.setCurrentIndex(index)

    def interface(self):
        return self.ui.comboBox_interface.currentText()

    def channel(self):
        return self.ui.comboBox_channel.currentText()

    def bitrate(self):
        text = self.ui.comboBox_bitrate.currentText()
        for kbit_s, desc in canopen_bitrates.items():
            if desc == text:
                return kbit_s

# ----------
# EOF
