# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gogo_frm.ui'
#
# Created: Sun Sep  8 10:13:09 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_GogoFrm(object):
    def setupUi(self, GogoFrm):
        GogoFrm.setObjectName(_fromUtf8("GogoFrm"))
        GogoFrm.resize(572, 365)
        GogoFrm.setWindowTitle(_fromUtf8("Mnemogogo"))
        self.tabWidget = QtGui.QTabWidget(GogoFrm)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 550, 310))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.synchronizeTab = QtGui.QWidget()
        self.synchronizeTab.setObjectName(_fromUtf8("synchronizeTab"))
        self.localFrame = QtGui.QFrame(self.synchronizeTab)
        self.localFrame.setGeometry(QtCore.QRect(24, 11, 176, 261))
        self.localFrame.setAutoFillBackground(True)
        self.localFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.localFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.localFrame.setObjectName(_fromUtf8("localFrame"))
        self.gridLayout = QtGui.QGridLayout(self.localFrame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 95, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(31, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.localLabel = QtGui.QLabel(self.localFrame)
        self.localLabel.setObjectName(_fromUtf8("localLabel"))
        self.gridLayout.addWidget(self.localLabel, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(32, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 94, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 2, 1, 1, 1)
        self.mobileFrame = QtGui.QFrame(self.synchronizeTab)
        self.mobileFrame.setGeometry(QtCore.QRect(330, 11, 192, 261))
        self.mobileFrame.setAutoFillBackground(True)
        self.mobileFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.mobileFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.mobileFrame.setObjectName(_fromUtf8("mobileFrame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.mobileFrame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem4 = QtGui.QSpacerItem(20, 95, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem4, 0, 1, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(29, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem5, 1, 0, 1, 1)
        self.mobileLabel = QtGui.QLabel(self.mobileFrame)
        self.mobileLabel.setObjectName(_fromUtf8("mobileLabel"))
        self.gridLayout_2.addWidget(self.mobileLabel, 1, 1, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(29, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem6, 1, 2, 1, 1)
        spacerItem7 = QtGui.QSpacerItem(20, 94, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem7, 2, 1, 1, 1)
        self.layoutWidget = QtGui.QWidget(self.synchronizeTab)
        self.layoutWidget.setGeometry(QtCore.QRect(220, 10, 97, 261))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem8 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem8)
        self.exportButton = QtGui.QPushButton(self.layoutWidget)
        self.exportButton.setObjectName(_fromUtf8("exportButton"))
        self.verticalLayout.addWidget(self.exportButton)
        spacerItem9 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem9)
        self.progressBar = QtGui.QProgressBar(self.layoutWidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem10 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem10)
        self.importButton = QtGui.QPushButton(self.layoutWidget)
        self.importButton.setObjectName(_fromUtf8("importButton"))
        self.verticalLayout.addWidget(self.importButton)
        spacerItem11 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem11)
        self.tabWidget.addTab(self.synchronizeTab, _fromUtf8(""))
        self.optionsTab = QtGui.QWidget()
        self.optionsTab.setObjectName(_fromUtf8("optionsTab"))
        self.label_3 = QtGui.QLabel(self.optionsTab)
        self.label_3.setGeometry(QtCore.QRect(10, 11, 181, 24))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.optionsTab)
        self.label_4.setGeometry(QtCore.QRect(10, 41, 175, 33))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.optionsTab)
        self.label_5.setGeometry(QtCore.QRect(10, 80, 175, 24))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.interfaceList = QtGui.QComboBox(self.optionsTab)
        self.interfaceList.setGeometry(QtCore.QRect(192, 80, 343, 24))
        self.interfaceList.setObjectName(_fromUtf8("interfaceList"))
        self.syncPath = QtGui.QLineEdit(self.optionsTab)
        self.syncPath.setGeometry(QtCore.QRect(192, 45, 251, 24))
        self.syncPath.setObjectName(_fromUtf8("syncPath"))
        self.browseButton = QtGui.QPushButton(self.optionsTab)
        self.browseButton.setGeometry(QtCore.QRect(449, 41, 86, 33))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.daysToExport = QtGui.QSpinBox(self.optionsTab)
        self.daysToExport.setGeometry(QtCore.QRect(192, 11, 46, 24))
        self.daysToExport.setObjectName(_fromUtf8("daysToExport"))
        self.forceMobileButton = QtGui.QPushButton(self.optionsTab)
        self.forceMobileButton.setGeometry(QtCore.QRect(11, 196, 119, 33))
        self.forceMobileButton.setObjectName(_fromUtf8("forceMobileButton"))
        self.forceLocalButton = QtGui.QPushButton(self.optionsTab)
        self.forceLocalButton.setGeometry(QtCore.QRect(11, 235, 119, 33))
        self.forceLocalButton.setObjectName(_fromUtf8("forceLocalButton"))
        self.groupBox = QtGui.QGroupBox(self.optionsTab)
        self.groupBox.setGeometry(QtCore.QRect(270, 130, 276, 118))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.maxSize = QtGui.QSpinBox(self.groupBox)
        self.maxSize.setGeometry(QtCore.QRect(95, 84, 72, 24))
        self.maxSize.setMinimum(16)
        self.maxSize.setMaximum(256)
        self.maxSize.setProperty("value", 64)
        self.maxSize.setObjectName(_fromUtf8("maxSize"))
        self.maxHeight = QtGui.QSpinBox(self.groupBox)
        self.maxHeight.setGeometry(QtCore.QRect(95, 55, 72, 24))
        self.maxHeight.setMinimum(32)
        self.maxHeight.setMaximum(4096)
        self.maxHeight.setSingleStep(100)
        self.maxHeight.setProperty("value", 300)
        self.maxHeight.setObjectName(_fromUtf8("maxHeight"))
        self.maxWidth = QtGui.QSpinBox(self.groupBox)
        self.maxWidth.setGeometry(QtCore.QRect(95, 25, 72, 24))
        self.maxWidth.setMinimum(32)
        self.maxWidth.setMaximum(4096)
        self.maxWidth.setSingleStep(100)
        self.maxWidth.setProperty("value", 240)
        self.maxWidth.setObjectName(_fromUtf8("maxWidth"))
        self.maxSize_label = QtGui.QLabel(self.groupBox)
        self.maxSize_label.setGeometry(QtCore.QRect(17, 84, 67, 17))
        self.maxSize_label.setObjectName(_fromUtf8("maxSize_label"))
        self.maxHeight_label = QtGui.QLabel(self.groupBox)
        self.maxHeight_label.setGeometry(QtCore.QRect(17, 55, 67, 17))
        self.maxHeight_label.setObjectName(_fromUtf8("maxHeight_label"))
        self.maxWidth_label = QtGui.QLabel(self.groupBox)
        self.maxWidth_label.setGeometry(QtCore.QRect(17, 25, 67, 17))
        self.maxWidth_label.setObjectName(_fromUtf8("maxWidth_label"))
        self.tabWidget.addTab(self.optionsTab, _fromUtf8(""))
        self.horizontalLayoutWidget = QtGui.QWidget(GogoFrm)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 330, 551, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem12)
        self.doneButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.doneButton.setObjectName(_fromUtf8("doneButton"))
        self.horizontalLayout.addWidget(self.doneButton)

        self.retranslateUi(GogoFrm)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GogoFrm)
        GogoFrm.setTabOrder(self.exportButton, self.importButton)
        GogoFrm.setTabOrder(self.importButton, self.doneButton)
        GogoFrm.setTabOrder(self.doneButton, self.tabWidget)
        GogoFrm.setTabOrder(self.tabWidget, self.daysToExport)
        GogoFrm.setTabOrder(self.daysToExport, self.browseButton)
        GogoFrm.setTabOrder(self.browseButton, self.interfaceList)
        GogoFrm.setTabOrder(self.interfaceList, self.maxWidth)
        GogoFrm.setTabOrder(self.maxWidth, self.maxHeight)
        GogoFrm.setTabOrder(self.maxHeight, self.maxSize)
        GogoFrm.setTabOrder(self.maxSize, self.syncPath)
        GogoFrm.setTabOrder(self.syncPath, self.forceMobileButton)
        GogoFrm.setTabOrder(self.forceMobileButton, self.forceLocalButton)

    def retranslateUi(self, GogoFrm):
        self.localLabel.setText(_translate("GogoFrm", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\"font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:xx-large; font-weight:600;\">Local</span></p></body></html>", None))
        self.mobileLabel.setText(_translate("GogoFrm", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\"font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:xx-large; font-weight:600;\">Mobile</span></p></body></html>", None))
        self.exportButton.setText(_translate("GogoFrm", "&Export >>", None))
        self.progressBar.setFormat(_translate("GogoFrm", "%p%", None))
        self.importButton.setText(_translate("GogoFrm", "<< &Import", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.synchronizeTab), _translate("GogoFrm", "Synchronize", None))
        self.label_3.setText(_translate("GogoFrm", "Number of days to export:", None))
        self.label_4.setText(_translate("GogoFrm", "Synchronisation path:", None))
        self.label_5.setText(_translate("GogoFrm", "Interface:", None))
        self.browseButton.setText(_translate("GogoFrm", "&Browse", None))
        self.forceMobileButton.setText(_translate("GogoFrm", "Force to Mobile", None))
        self.forceLocalButton.setText(_translate("GogoFrm", "Force to Local", None))
        self.groupBox.setTitle(_translate("GogoFrm", "Exported image limits", None))
        self.maxSize_label.setText(_translate("GogoFrm", "Size (Kb):", None))
        self.maxHeight_label.setText(_translate("GogoFrm", "Height:", None))
        self.maxWidth_label.setText(_translate("GogoFrm", "Width:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.optionsTab), _translate("GogoFrm", "Options", None))
        self.doneButton.setText(_translate("GogoFrm", "&Done", None))
        self.doneButton.setShortcut(_translate("GogoFrm", "Alt+D", None))

