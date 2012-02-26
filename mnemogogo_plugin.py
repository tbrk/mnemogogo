##############################################################################
#
# mnemogogo.py <tim@tbrk.org>
#
# Mnemogogo: making mnemosyne 2.x mobile
#
##############################################################################

#
# Copyright (C) 2012 Timothy Bourke
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
from PyQt4.QtWebKit import QWebView

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.criterion import Criterion
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt
from mnemosyne.libmnemosyne.ui_components.configuration_widget \
    import ConfigurationWidget

# for MnemogogoRenderChain
from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.plain_text import PlainText
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease

import sys, copy
from os.path import exists, join

try:
    import mnemogogo
    mnemogogo_imported = True
except Exception, e:
    mnemogogo_imported = False
    mnemogogo_imported_error = str(e)

name = 'Mnemogogo'
version = "2.0.0-alpha1"
exported_tag_name = "Mnemogogo"

def tr(text):
    return QCoreApplication.translate("Mnemogogo", text)

class MnemogogoConfig(Hook):
    used_for = "configuration_defaults"

    def run(self):
        pass

class MnemogogoRenderChain(RenderChain):
    id = "mnemogogo"
    filters = [EscapeToHtml, Latex, ExpandPaths,
               NonLatinFontSizeIncrease]
    renderers = [PlainText]

    def __init__(self, component_manager):
        RenderChain.__init__(self, component_manager)

        for plugin in self.component_manager.all("plugin"):
            try:
                plugin.new_render_chain(id)
            except: pass

class MnemogogoReviewWdgt(ReviewWdgt):
    plugin = None

    def __init__(self, component_manager):
        ReviewWdgt.__init__(self, component_manager)

        mnemogogo.lock_enabling.add(self.show_button)
        mnemogogo.lock_enabling.add(self.grades)
        mnemogogo.lock_enabling.add(self.main_widget().actionActivatePlugins)

        mnemogogo.lock_visible.add(self.question)
        mnemogogo.lock_visible.add(self.question_label)
        mnemogogo.lock_visible.add(self.answer)
        mnemogogo.lock_visible.add(self.answer_label)

        bd = self.config().data_dir
        lock_msg_main = tr("Mobile reviewing is enabled.")
        lock_msg_info = tr("Choose Mnemogogo from the Cards menu for options.")
        html =  '<html>'
        html += '<body style="margin:0; padding:0; border:thin solid #8F8F8F;">'
        html += '<div style="height:200px; width:400px; position:absolute;'
        html += ' top:50%; margin-top:-100px; left:50%; margin-left:-200px;'
        html += ' text-align:center;">'
        html += '<b><font color="red">%s</font></b><br/>' % lock_msg_main
        html += '<br/><img src="file://%s/plugins/mnemogogo/locked.png">' % bd
        html += '<br/><br/><i>%s</i>' % lock_msg_info
        html += "</div></body></html>"

        self.gogoinfo = QWebView(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                self.gogoinfo.sizePolicy().hasHeightForWidth())
        self.gogoinfo.setSizePolicy(sizePolicy)
        self.gogoinfo.setMinimumSize(QSize(295, 50))
        self.gogoinfo.setHtml(html)
        self.gogoinfo.setObjectName("Mnemogogo message")
        self.question_box.addWidget(self.gogoinfo)

        for plugin in component_manager.all("plugin"):
            if plugin.__class__.__name__ == "MnemogogoPlugin":
                self.plugin = plugin

        if self.plugin:
            self.plugin.refresh(self)

    def remove_locking(self):
        self.show_button.removeLocking()
        self.grades.removeLocking()
        self.main_widget().actionActivatePlugins.removeLocking()

        self.question.removeLocking()
        self.question_label.removeLocking()
        self.answer.removeLocking()
        self.answer_label.removeLocking()

class MnemogogoPlugin(Plugin):
    name = name
    description = "Making mnemosyne mobile (v" + version + ")"

    components = [MnemogogoConfig, MnemogogoRenderChain, MnemogogoReviewWdgt]

    is_locked = False
    config_key = "mnemogogo"

    default_settings = {
        'sync_path'     : '',
        'interface'     : None,
        'n_days'        : 7,
        'mode'          : 'local',
        'extra_factor'  : 1.00,
        'max_width'     : 240,
        'max_height'    : 300,
        'max_size'      : 64,
    }

    def load_config(self):
        self.config_key = mnemogogo.get_config_key(self.config())

        try:
            config = self.config()[self.config_key]
        except KeyError:
            self.config()[self.config_key] = {}
            config = {}
        
        self.settings = copy.copy(self.default_settings)
        for k in self.settings.keys():
            if config.has_key(k): self.settings[k] = config[k]
        
    def save_config(self):
        self.config()[self.config_key] = copy.copy(self.settings)

    def open_dialog(self):
        mobile_before = self.settings['mode'] == 'mobile'

        self.gogo_dlg.configure(self.settings, self.config(), self.database(),
                                self.review_controller(),
                                self.component_manager.debug)
        self.gogo_dlg.exec_()
        self.settings = self.gogo_dlg.settings

        mobile_after = self.settings['mode'] == 'mobile'

        try:
            if mobile_after:
                self.lock()
            else:
                self.unlock()
        except KeyError:
            self.show_error("Missing state."
                + "Mnemogogo could not determine whether it should "
                + " be in local or mobile mode. Please use the "
                + "'Force to Mobile' and 'Force to Local' buttons to "
                + "establish the correct state.")
            self.unlock()

        if mobile_before and not mobile_after:
            self.review_controller().reset()

        self.save_config()

    def show_error(self, msg):
        try:
            QMessageBox.critical(None, tr("Mnemogogo"), tr(msg),
                                 tr("&OK"), "", "", 0, -1)
        except TypeError:
            QMessageBox.critical(None, tr("Mnemogogo"), msg, tr("&OK"),
                                 "", "", 0, -1)

    def lock(self):
        self.is_locked = True
        self.refresh()

    def unlock(self):
        self.is_locked = False
        self.refresh()

    def refresh(self, widget=None):
        try:
            if widget is None:
                review_controller = self.component_manager.current("review_controller")
                widget = review_controller.widget
            main_widget = self.main_widget()

            if self.is_locked:
                widget.show_button.disableAndLock()
                widget.grades.disableAndLock()
                widget.question.hideAndLock()
                widget.question_label.hideAndLock()
                widget.answer.hideAndLock()
                widget.answer_label.hideAndLock()
                widget.gogoinfo.show()
                main_widget.actionActivatePlugins.disableAndLock()
            else:
                widget.show_button.unlockAndRestore()
                widget.grades.unlockAndRestore()
                widget.question.unlockAndRestore()
                widget.question_label.unlockAndRestore()
                widget.answer.unlockAndRestore()
                widget.answer_label.unlockAndRestore()
                widget.gogoinfo.hide()
                main_widget.actionActivatePlugins.unlockAndRestore()

        except Exception as e:
            pass

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        self.menu_action = None

    def activate(self):
        Plugin.activate(self)

        basedir = self.config().data_dir

        if not exists(join(basedir, "plugins", "mnemogogo")):
            self.show_error("Incorrect installation. Missing "
                + join(basedir, "plugins", "mnemogogo")
                + " directory")
            return

        if not mnemogogo_imported:
            self.show_error("Incorrect installation."
                + " The mnemogogo module could not be imported.\n\n("
                + mnemogogo_imported_error + ")")
            return
        
        mnemogogo.set_logger(mnemogogo.Logger(basedir))

        mnemogogo.logger().log_info('version %s' % version)
        if not mnemogogo.htmltounicode_working:
            mnemogogo.logger().log_warning(
                'Neither html.entities nor htmlentitydefs could be imported.')
        
        self.interfaces = mnemogogo.register_interfaces(basedir)

        self.gogo_dlg = mnemogogo.GogoDlg(self.main_widget())
        self.gogo_dlg.setInterfaceList(self.interfaces)

        # Add Menu Item
        self.menu_action = QAction("&Mnemogogo", self.main_widget(),
                shortcut=QKeySequence(Qt.ControlModifier + Qt.Key_M),
                statusTip="Transfer cards to and from your mobile device.",
                triggered=self.open_dialog)

        self.main_widget().menu_Cards.addAction(self.menu_action)
        try:
            self.review_controller().reset()
        except:
            pass

        self.load_config()
        if self.settings['mode'] == 'mobile':
            self.lock()
        else:
            self.unlock()

    def deactivate(self):
        Plugin.deactivate(self)

        if self.menu_action:
            self.main_widget().menu_Cards.removeAction(self.menu_action)
            self.menu_action = None

        self.unlock()

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(MnemogogoPlugin)

