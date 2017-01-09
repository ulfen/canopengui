#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CANopenGUI MainWindow
"""

import sys
import os

try:
    from PySide import QtGui as QtWidgets
    from PySide.QtCore import Qt
    from PySide.QtCore import Slot
    from .pyside_loadUiType import loadUiType
except ImportError:
    try:
        from PyQt5 import QtWidgets
        from PyQt5.QtCore import Qt
        from PyQt5.QtCore import pyqtSlot as Slot
        from PyQt5.uic import loadUiType
    except ImportError:
        from PyQt4 import QtGui as QtWidgets
        from PyQt4.QtCore import Qt
        from PyQt4.QtCore import pyqtSlot as Slot
        from PyQt4.uic import loadUiType

import canopen

from .interfacedialog import InterfaceDialog

# --

def datatype_group_description(datatype):
    if 0x0001 <= datatype <= 0x001f:
        description = 'Standard Data Type'
    elif 0x0020 <= datatype <= 0x0023:
        description = 'Pre-defined Complex Data Type'
    elif 0x0024 <= datatype <= 0x003f:
        description = 'Reserved'
    elif 0x0040 <= datatype <= 0x005f:
        description = 'Manufacturer Complex Data Type'
    elif 0x0060 <= datatype <= 0x007f:
        description = 'Device Profile Standard Data Type'
    elif 0x0080 <= datatype <= 0x009f:
        description = 'Device Profile Complex Data Type'
    elif 0x00A0 <= datatype <= 0x025f:
        description = 'Multiple Device Modules Data Type'
    elif 0x0260 <= datatype <= 0x0fff:
        description = 'Reserved'
    else:
        description = 'Invalid'
    return description

def standard_datatype_description(datatype):
    std_types = {
        0x01:'BOOLEAN',
        0x02:'INTEGER8',
        0x03:'INTEGER16',
        0x04:'INTEGER32',
        0x05:'UNSIGNED8',
        0x06:'UNSIGNED16',
        0x07:'UNSIGNED32',
        0x08:'REAL32',
        0x09:'VISIBLE_STRING',
        0x0A:'OCTET_STRING',
        0x0B:'UNICODE_STRING',
        0x0C:'TIME_OF_DAY',
        0x0D:'TIME_DIFFERENCE',
        0x0E:'BIT_STRING',
        0x0F:'DOMAIN',
        0x10:'INTEGER24',
        0x11:'REAL64',
        0x12:'INTEGER40',
        0x13:'INTEGER48',
        0x14:'INTEGER56',
        0x15:'INTEGER64',
        0x16:'UNSIGNED24',
        0x18:'UNSIGNED40',
        0x19:'UNSIGNED48',
        0x1A:'UNSIGNED56',
        0x1B:'UNSIGNED64',
        0x20:'PDO_COMMUNICATION_PARAMETER',
        0x21:'PDO_MAPPING',
        0x22:'SDO_PARAMETER',
        0x23:'IDENTITY',
    }
    return std_types.get(datatype, '')

# ----------

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        Ui_Class, _ = loadUiType('ui/mainwindow.ui')
        self.ui = Ui_Class()
        self.ui.setupUi(self)
        self.ui.actionConnect.setEnabled(False)
        self.ui.actionDisconnect.setEnabled(False)
        self.ui.pushButton_Read.setEnabled(False)
        self.ui.pushButton_Write.setEnabled(False)

        self.network = None
        self.node = None
        self.node_id = 0

    def __del__(self):
        if self.network and self.network.bus:
            self.network.disconnect()

    # --

    @Slot()
    def on_actionConnect_triggered(self):
        assert self.network

        dlg = InterfaceDialog(self)

        od = self.node.object_dictionary
        if od.bitrate is not None:
            dlg.select_bitrate(od.bitrate/1000)

        ok = dlg.exec_()
        if ok:
            interface = dlg.interface()
            channel = dlg.channel()
            bitrate = dlg.bitrate()

            try:
                if self.network.bus:
                    self.network.disconnect()
                self.network.connect(channel, bustype=interface, bitrate=bitrate*1000)
                self.ui.actionDisconnect.setEnabled(True)
            except Exception as e:
                self.ui.statusbar.showMessage(str(e), 5000)

        self.update_push_buttons()

    @Slot()
    def on_actionDisconnect_triggered(self):
        assert self.network.bus

        try:
            self.network.disconnect()
        except Exception as e:
            self.ui.statusbar.showMessage(str(e), 5000)

        self.ui.actionDisconnect.setEnabled(False)
        self.update_push_buttons()

    @Slot()
    def on_actionExit_triggered(self):
        self.close()

    @Slot()
    def on_actionAbout_triggered(self):
        QtWidgets.QMessageBox.about(
            self,
            'About CANopenGUI',
            'CANopenGUI v0.1\n'
            'A simple CANopen Object Browser\n'
            'Copyright 2017 Ulf Erikson\n'
            '\n'
            'This software is based on:\n'
            'Qt (PySide/PyQt), python-can, canopen'
        )

    # --

    def get_currently_selected_item(self):
        current_item = self.ui.treeWidget_ObjectDictionary.currentItem()
        return current_item

    def get_current_index(self):
        current_item = self.get_currently_selected_item()
        if current_item is None:
            return None, None
        parent_item = current_item.parent()
        if parent_item is not None:
            index = int(parent_item.data(0, Qt.DisplayRole), 16)
            subindex = int(current_item.data(0, Qt.DisplayRole), 10)
        else:
            index = int(current_item.data(0, Qt.DisplayRole), 16)
            subindex = None
        return index, subindex

    def get_dictionary_object(self, index, subindex):
        try:
            if subindex is not None:
                obj = self.node.object_dictionary[index][subindex]
            else:
                obj = self.node.object_dictionary[index]
        except Exception as e:
            obj = None
        return obj

    def get_sdo_object(self, index, subindex):
        try:
            if subindex is not None:
                obj = self.node.sdo[index][subindex]
            else:
                obj = self.node.sdo[index]
        except Exception as e:
            obj = None
        return obj

    def get_current_dictionary_object(self):
        index, subindex = self.get_current_index()
        obj = self.get_dictionary_object(index, subindex)
        return obj

    def get_current_sdo_object(self):
        index, subindex = self.get_current_index()
        obj = self.get_sdo_object(index, subindex)
        return obj

    # --

    def import_object_dictionary(self, fname):
        try:
            od = canopen.objectdictionary.import_od(fname)
            return od
        except Exception as e:
            self.ui.statusbar.showMessage(str(e), 5000)

    def get_node_id(self, od=None):
        node_id = self.ui.spinBox_NodeId.value()
        if od and od.node_id and od.node_id!=node_id:
            node_id = od.node_id
            self.ui.spinBox_NodeId.setValue(node_id)
        return node_id

    def create_network_node(self, node_id, od):
        # Start with creating a network representing a CAN bus
        network = canopen.Network()

        try:
            # Add a node with its corresponding Object Dictionary
            node = network.add_node(node_id, od)
        except Exception as e:
            self.ui.statusbar.showMessage(str(e), 5000)
            network, node = None, None

        return network, node

    def populate_treewidget(self, od):
        self.ui.treeWidget_ObjectDictionary.clear()
        for key in od.keys():
            obj = od[key]
            txt = '0x{0:04x}\t{1}'.format(obj.index, obj.name)
            parent = QtWidgets.QTreeWidgetItem(txt.split('\t'))
            self.ui.treeWidget_ObjectDictionary.addTopLevelItem(parent)
            try:
                for subindex in obj.subindices:
                    subobj = obj[subindex]
                    txt = '{0}\t{1}'.format(subindex, subobj.name)
                    child = QtWidgets.QTreeWidgetItem(txt.split('\t'))
                    parent.addChild(child)
            except:
                pass
        self.ui.treeWidget_ObjectDictionary.setCurrentItem(
            self.ui.treeWidget_ObjectDictionary.topLevelItem(0))

    @Slot()
    def on_pushButton_Browse_clicked(self):
        selection = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open EDS file',
            '',
            'CANopen Files (*.eds *.epf);;'
            'All Files (*.*)')
        fname = selection[0] if isinstance(selection, tuple) else selection
        if fname:
            od = self.import_object_dictionary(fname)
            if od:
                node_id = self.get_node_id(od)
                network, node = self.create_network_node(node_id, od)
                if network and node:
                    self.ui.actionConnect.setEnabled(True)
                    self.ui.lineEdit_EDS.setText(fname)
                    self.network = network
                    self.node_id = node_id
                    self.node = node
                    self.populate_treewidget(node.object_dictionary)

    # --
    # Item attributes

    def show_attributes(self, attributes):
        self.ui.lineEdit_Index.setText(attributes.get('index', ''))
        self.ui.lineEdit_SubIndex.setText(attributes.get('subindex', ''))
        self.ui.lineEdit_Name.setText(attributes.get('name', ''))
        self.ui.lineEdit_Datatype.setText(attributes.get('datatype', ''))
        self.ui.lineEdit_Access.setText(attributes.get('access', ''))
        self.ui.lineEdit_Limits.setText(attributes.get('limits', ''))

    def clear_attributes(self):
        self.show_attributes({})

    def update_attributes(self):
        obj = self.get_current_dictionary_object()

        attributes = {}
        attributes['index'] = '0x{0:04x}'.format(obj.index)
        is_subobject = hasattr(obj, 'parent') and hasattr(obj.parent, 'parent')
        attributes['subindex'] = '0x{0:02x}'.format(obj.subindex) if is_subobject else ''
        attributes['name'] = obj.name

        try:
            std_desc = standard_datatype_description(obj.data_type)
            type_txt = std_desc or '0x{0:04x}'.format(obj.data_type)
            group_desc = datatype_group_description(obj.data_type)
            attributes['datatype'] = '{0} - {1}'.format(type_txt, group_desc)
        except AttributeError:
            attributes['datatype'] = ''

        attributes['access'] = getattr(obj, 'access_type', '')

        min_val = getattr(obj, 'min', None)
        max_val = getattr(obj, 'max', None)
        if min_val is not None or max_val is not None:
            attributes['limits'] = u' \u2264 '.join([str(x) for x in [min_val, 'x', max_val] if x is not None])
        else:
            attributes['limits'] = ''

        self.show_attributes(attributes)

    @Slot(QtWidgets.QTreeWidgetItem,QtWidgets.QTreeWidgetItem)
    def on_treeWidget_ObjectDictionary_currentItemChanged(self, current, previous):
        if not current:
            self.clear_attributes()
        else:
            self.update_attributes()
        self.ui.lineEdit_CurrentValue.setText('')
        self.update_push_buttons()

    # --
    # Read/Write push buttons

    def update_push_buttons(self):
        obj = self.get_current_dictionary_object()
        access_txt = getattr(obj, 'access_type', '')
        has_read_access = access_txt.startswith('rw') or access_txt in ['ro', 'const']
        has_write_access = access_txt.startswith('rw') or access_txt in ['wo']
        has_connection = self.network is not None and self.network.bus is not None
        self.ui.pushButton_Read.setEnabled(has_connection and has_read_access)
        self.ui.pushButton_Write.setEnabled(has_connection and has_write_access)

    @Slot()
    def on_pushButton_Read_clicked(self):
        obj = self.get_current_sdo_object()
        if obj is not None:
            try:
                data = obj.raw
            except Exception as e:
                self.ui.statusbar.showMessage('Read ERROR: '+str(e), 5000)
                data = ''

            self.ui.lineEdit_CurrentValue.setText(str(data))

    @Slot()
    def on_pushButton_Write_clicked(self):
        obj = self.get_current_sdo_object()
        if obj is not None:
            data = self.ui.lineEdit_CurrentValue.text().strip()
            if data:
                try:
                    obj.raw = data
                except Exception as e:
                    self.ui.statusbar.showMessage('Write ERROR: '+str(e), 5000)

# ----------
# EOF
