#
# Copyright (C) 2009 Timothy Bourke
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gogo_frm import *
import traceback
from os import mkdir
from core import *

def tr(text):
    return QCoreApplication.translate("Mnemogogo", text)

class GogoDlg(QDialog):
    settings = {
            'extra_factor' : 1.00,
        }

    def showWarning(self, msg):
        status = QMessageBox.warning(None, "Mnemogogo", msg, self.tr("&OK"))

    def showError(self, msg):
        status = QMessageBox.critical(None, "Mnemogogo", msg, self.tr("&OK"))

    def showMnemogogoError(self, exc):
        if exc.err == exc.ErrInitInterface:
            msg = self.tr("Error initialising interface: ") + exc.details
        elif exc.err == exc.ErrRegInterface:
            msg = self.tr("Error registering interface: ") + exc.details
        elif exc.err == exc.ErrAnotherDB:
            msg = self.tr("These cards were exported from a different database!")
        elif exc.err == exc.ErrExportFailed:
            msg = self.tr("Export failed!") + exc.details
        elif exc.err == exc.ErrCannotOpen:
            msg = self.tr("Cannot open file: ") + exc.details
        elif exc.err == exc.ErrCannotFind:
            msg = self.tr("Could not find: ") + exc.details
        elif exc.err == exc.ErrShortStats:
            msg = self.tr("Too few fields in stats.csv: ") + exc.details
        elif exc.err == exc.ErrImportFailed:
            msg = self.tr("Import failed: ") + exc.details

        self.showError(msg)

    def markInactive(self, frame, label):
        pal = frame.palette();
        pal.setColor(frame.backgroundRole(), QColor(124,124,124));
        frame.setPalette(pal);

        pal = label.palette();
        pal.setColor(label.backgroundRole(), QColor(124,124,124));
        pal.setColor(label.foregroundRole(), QColor(192,192,192));
        label.setPalette(pal);

    def markActive(self, frame, label):
        pal = frame.palette();
        pal.setColor(frame.backgroundRole(), QColor(0,170,0));
        frame.setPalette(pal);

        pal = label.palette();
        pal.setColor(label.backgroundRole(), QColor(0,170,0));
        pal.setColor(label.foregroundRole(), QColor(255,255,255));
        label.setPalette(pal);

    def setLocal(self):
        self.mode = "local"
        self.markInactive(self.ui.mobileFrame, self.ui.mobileLabel)
        self.markActive(self.ui.localFrame, self.ui.localLabel)
        self.ui.exportButton.setEnabled(1)
        self.ui.importButton.setEnabled(0)
        self.ui.forceMobileButton.setEnabled(1)
        self.ui.forceLocalButton.setEnabled(0)
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.hide()
        self.ui.progressBar.setInvertedAppearance(False)

    def setMobile(self):
        self.mode = "mobile"
        self.markActive(self.ui.mobileFrame, self.ui.mobileLabel)
        self.markInactive(self.ui.localFrame, self.ui.localLabel)
        self.ui.exportButton.setEnabled(0)
        self.ui.importButton.setEnabled(1)
        self.ui.forceMobileButton.setEnabled(0)
        self.ui.forceLocalButton.setEnabled(1)
        self.ui.progressBar.setProperty("value", 0)
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.hide()
        self.ui.progressBar.setInvertedAppearance(True)

    def setInterfaceList(self, interfaces):
        self.name_to_desc = {}
        self.desc_to_name = {}
        self.name_to_object = {}
        self.name_to_index = {}
        self.ui.interfaceList.clear()
        i = 0
        for iface in interfaces:
            self.name_to_desc[iface['name']] = iface['description']
            self.desc_to_name[iface['description']] = iface['name']
            self.name_to_object[iface['name']] = iface['object']
            self.name_to_index[iface['name']] = i
            self.ui.interfaceList.insertItem(i, iface['description'])
            i = i + 1

    def getInterface(self):
        return self.desc_to_name[unicode(self.ui.interfaceList.currentText())]

    def writeSettings(self):
        self.settings['mode'] = self.mode
        self.settings['interface'] = self.getInterface()
        self.settings['n_days'] = self.ui.daysToExport.value()
        self.settings['sync_path'] = unicode(self.ui.syncPath.text())
        self.settings['max_width'] = self.ui.maxWidth.value()
        self.settings['max_height'] = self.ui.maxHeight.value()
        self.settings['max_size'] = self.ui.maxSize.value()

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_GogoFrm()
        self.ui.setupUi(self)

        self.main_dlg = parent

        self.setLocal()

        self.connect(self.ui.exportButton, SIGNAL("clicked()"), self.doExport)
        self.connect(self.ui.importButton, SIGNAL("clicked()"), self.doImport)
        self.connect(self.ui.browseButton, SIGNAL("clicked()"), self.browse)
        self.connect(self.ui.doneButton, SIGNAL("clicked()"), self.close)
        self.connect(self.ui.forceMobileButton, SIGNAL("clicked()"),
                     self.forceMobile)
        self.connect(self.ui.forceLocalButton, SIGNAL("clicked()"),
                     self.forceLocal)
        self.connect(self, SIGNAL("rejected()"), self.writeSettings)

    def doExport(self):
        self.writeSettings()
        try:
            if self.settings['sync_path'] == '':
                self.showError(tr("A synchronization path must be set first!"))
                return

            if not os.path.exists(self.settings['sync_path']):
                try:
                    mkdir(self.settings['sync_path'])
                except: pass

            if not os.path.exists(self.settings['sync_path']):
                self.showError(tr("The synchronization path ('%s') is not valid!")
                                % self.settings['sync_path'])
                return

            self.ui.progressBar.setEnabled(True)
            self.ui.progressBar.show()
            logger().clear_log_status()
            do_export(
                self.name_to_object[self.settings['interface']],
                self.settings['n_days'],
                self.settings['sync_path'],
                self.mnemosyne_database,
                self.mnemosyne_config,
                self.card_types,
                self.mnemosyne_debug,
                self.ui.progressBar,
                self.settings['extra_factor'],
                self.settings['max_width'],
                self.settings['max_height'],
                self.settings['max_size'])
            self.setMobile()
            if logger().check_log_status():
                self.showWarning(
                    tr(u"Messages were written to gogolog.txt in the Mnemosyne home directory."))

        except Mnemogogo, e:
            self.showMnemogogoError(e)
        except Exception:
            self.showError(traceback.format_exc())

    def doImport(self):
        self.writeSettings()
        try:
            self.ui.progressBar.setEnabled(True)
            self.ui.progressBar.show()
            logger().clear_log_status()
            do_import(
                self.name_to_object[self.settings['interface']],
                self.settings['sync_path'],
                self.mnemosyne_database,
                self.mnemosyne_config,
                self.mnemosyne_scheduler,
                self.mnemosyne_debug,
                self.ui.progressBar)
            self.setLocal()

            self.mnemosyne_revcontroller.reset_but_try_to_keep_current_card()
            
            if logger().check_log_status():
                self.showWarning(
                    tr(u"Messages were written to log.txt in the Mnemosyne home directory."))

        except Mnemogogo, e:
            self.showMnemogogoError(e)
        except Exception:
            self.showError(traceback.format_exc())

    def forceMobile(self):
        self.setMobile()

    def forceLocal(self):
        self.setLocal()

    def browse(self):
        d = unicode(QFileDialog.getExistingDirectory(self, 
                        tr("Select synchronization path"),
                        self.ui.syncPath.text(),
                        QFileDialog.ShowDirsOnly))
                
        if d != "":
            self.ui.syncPath.setText(d)
    
    def configure(self, settings, mnemosyne_config, database,
                  review_controller, scheduler, component_manager):
        self.mnemosyne_config = mnemosyne_config
        self.mnemosyne_database = database
        self.mnemosyne_revcontroller = review_controller
        self.mnemosyne_scheduler = scheduler
        self.mnemosyne_debug = component_manager.debug
        self.card_types = component_manager.all("card_type")

        if settings.has_key('mode'):
            self.mode = settings['mode']
        else:
            self.mode = 'local'
        self.settings['mode'] = self.mode
        
        if self.mode == 'mobile':
            self.setMobile()
        else:
            self.setLocal()

        if settings.get('interface'):
            try:
                if not settings['interface'] is None:
                    self.ui.interfaceList.setCurrentIndex(
                        self.name_to_index[settings['interface']])
            except KeyError:
                self.showWarning(
                    tr("The interface '%s' is not currently available. Please select another.")
                    % settings['interface'])

        if settings.has_key('n_days'):
            self.ui.daysToExport.setValue(settings['n_days'])

        if settings.has_key('sync_path'):
            self.ui.syncPath.setText(settings['sync_path'])
        
        if settings.has_key('extra_factor'):
            self.settings['extra_factor'] = settings['extra_factor']
        
        if settings.has_key('max_width'):
            self.ui.maxWidth.setValue(settings['max_width'])

        if settings.has_key('max_height'):
            self.ui.maxHeight.setValue(settings['max_height'])

        if settings.has_key('max_size'):
            self.ui.maxSize.setValue(settings['max_size'])

