# encoding: utf-8
##############################################################################
#
# gogorender.py 2.x
# Timothy Bourke <tim@tbrk.org>
#
# Plugin for rendering segments of text as image files.
#
# The main reason for this plugin is to work around the limitations of
# displaying fonts under J2ME on certain mobile phones. Characters can
# instead be rendered on a PC where more fonts and libraries are available.
#
# NB: On phones where security prompts cannot be disabled, each image
#     will generate a confirmation prompt. This can quickly become annoying.
#
##############################################################################

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import QTextDocument, QTextCursor
from PyQt4.QtCore import QRegExp

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
   ConfigurationWidget

import sys
import re
from copy import copy
import os, os.path

name = "Gogorender"
version = "2.0"
description = "Render words as image files on Mnemogogo export. (v" + version + ")"

render_chains = ["mnemogogo"]

default_config = {
    'transparent'     : True,
    'render_char'     : u'[\u0100-\uff00]',
    'not_render_char' : u'[—≠–œ‘’“”…€]',

    # \xfffc is the "Object Replacement Character" (used for images)
    # \x2028 is the "Line Separator"
    # \x2029 is the "Paragraph Separator"
    'not_word'        : u'[\s\u2028\u2029\ufffc]',
}

def translate(text):
    return text

class GogorenderConfig(Hook):
    used_for = "configuration_defaults"

    def run(self):
        self.config().setdefault("gogorender", default_config)

class GogorenderConfigWdgt(QtGui.QWidget, ConfigurationWidget):
    name = name

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        vlayout = QtGui.QVBoxLayout(self)

        config = self.config()['gogorender']

        # add basic settings
        toplayout = QtGui.QFormLayout()

        self.not_render_char = QtGui.QLineEdit(self)
        self.not_render_char.setText(config["not_render_char"][1:-1])
        toplayout.addRow(
            translate("Treat these characters normally:"),
            self.not_render_char)

        self.transparent = QtGui.QCheckBox(self)
        self.transparent.setChecked(config["transparent"])
        toplayout.addRow(translate("Render with transparency:"), self.transparent)

        vlayout.addLayout(toplayout)

    def apply(self):
        self.config()["gogorender"]["not_render_char"] = \
            u"[%s]" % unicode(self.not_render_char.text())
        self.config()["gogorender"]["transparent"] = \
            self.transparent.isChecked()

        for chain in render_chains:
            try:
                filter = self.render_chain(chain).filter(Gogorender)
                if filter:
                    filter.reconfigure()
            except KeyError: pass

def moveprev(pos):
    pos.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)

def movenext(pos):
    pos.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)

class Gogorender(Filter):
    name = name
    version = version
    tag_re = re.compile("(<[^>]*>)")

    def __init__(self, component_manager):
        Filter.__init__(self, component_manager)
        self.reconfigure()
        self.debug = component_manager.debug_file != None

    def setting(self, key):
        try:
            config = self.config()["gogorender"]
        except KeyError: config = {}

        if key == 'imgpath':
            return config.get('imgpath',
                os.path.join(self.config().data_dir, 'gogorender'))
        else:
            return config.get(key, default_config[key])

    def reconfigure(self):
        self.imgpath = self.setting('imgpath')
        if not os.path.exists(self.imgpath): os.mkdir(self.imgpath)

        self.transparent        = self.setting('transparent')
        self.render_char_re     = QRegExp(self.setting('render_char'))
        self.not_render_char_re = QRegExp(self.setting('not_render_char'))
        self.not_word_re        = QRegExp(self.setting('not_word'))

    def debugline(self, msg, pos):
        if self.debug:
            s = pos.selectedText()
            try:
                c = ord(unicode(s[0]))
            except IndexError: c = 0
            self.component_manager.debug(
                u'gogorender: %s pos=%d char="%s" (0x%04x)'
                % (msg, pos.position(), s, c))

    # Must return one of:
    #   None            not rendered after all
    #   path            a path to the rendered image
    def render_word(self, word, font, color):
        fontname = font.family()
        fontsize = font.pointSize()

        style = ""
        if font.bold():   style += 'b'
        if font.italic(): style += 'i'

        colorname = color.name()[1:]

        # Generate a file name
        fword = word.replace('/', '_sl-')\
                    .replace('\\', '_bs-')\
                    .replace(' ', '_')\
                    .replace('#', '_ha-')\
                    .replace('{', '_cpo-')\
                    .replace('}', '_cpc-')\
                    .replace('*', '_ast-')
        if fword[0] == '.': fword = '_' + fword
        if fword[0] == '-': fword = '_' + fword

        filename = "%s-%s-%s-%s-%s.png" % (
            fword, fontname, str(fontsize), style, colorname)
        path = os.path.join(self.imgpath, filename)

        if (os.path.exists(path)):
            return path

        # Render with Qt
        text = QtCore.QString(word)

        fm = QtGui.QFontMetrics(font)
        width = fm.width(text) + (fm.charWidth('M', 0) / 2)
        height = fm.height()

        # Alternative: calculate the bounding box from the text being rendered;
        #              disadvantage = bad alignment of adjacent images.
        #bbox = fm.boundingRect(text)
        #width = bbox.width()
        #height = bbox.height()

        img = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)

        if self.transparent:
            img.fill(QtGui.qRgba(0,0,0,0))
        else:
            img.fill(QtGui.qRgba(255,255,255,255))

        p = QtGui.QPainter()
        p.begin(img)
        p.setFont(font)
        p.setPen(QtGui.QColor(color))
        p.drawText(0, 0, width, height, 0, text)
        p.end()

        if img.save(path, "PNG"):
            return path
        else:
            return None

    def substitute(self, text, mapping):
        r = []
        for s in self.tag_re.split(text):
            if len(s) == 0 or s[0] == '<':
                r.append(s)
                continue

            while mapping:
                (match, path) = mapping[0]

                (before, x, after) = s.partition(match)
                if x == '':
                    s = before
                    break
                
                r.append(before)
                r.append('<img src="%s"/>' % path)
                mapping = mapping[1:]
                s = after

            r.append(s)

        return ''.join(r)

    def run(self, text, card, fact_key, **render_args):
        doc = QTextDocument()

        proxy_key = card.card_type.fact_key_format_proxies()[fact_key]
        font_string = self.config().card_type_property(
            "font", card.card_type, proxy_key)

        if font_string:
            family,size,x,x,weight,italic,u,s,x,x = font_string.split(",")
            font = QtGui.QFont(family, int(size), int(weight), bool(int(italic)))
            doc.setDefaultFont(font)

        doc.setHtml(text)
        if self.debug:
            self.component_manager.debug(
                "gogorender: %s\ngogorender: %s\ngogorender: %s"
                % (70 * "-", text, 70 * "-"))

        render = []
        pos = doc.find(self.render_char_re)
        while not pos.isNull():
            s = pos.selectedText()
            if (self.not_render_char_re.exactMatch(s)
                    or self.not_word_re.exactMatch(s)):
                self.debugline("skip", pos)
                movenext(pos)
                pos = doc.find(self.render_char_re, pos)
                continue;
            self.debugline("==", pos)

            fmt = pos.charFormat()
            font = fmt.font()
            color = fmt.foreground().color()

            # find the start of the word
            #moveprev(pos)
            while not pos.atBlockStart():
                moveprev(pos)
                s = pos.selectedText()
                ccolor = pos.charFormat().foreground().color()
                self.debugline("<--", pos)

                if len(s) > 0 and self.not_word_re.exactMatch(s[0]):
                    movenext(pos)
                    self.debugline("-->", pos)
                    break;

                if pos.charFormat().font() != font or ccolor != color:
                    break;

            pos.setPosition(pos.position(), QTextCursor.MoveAnchor)

            # find the end of the word
            while not pos.atBlockEnd():
                movenext(pos)
                s = pos.selectedText()
                ccolor = pos.charFormat().foreground().color()
                self.debugline("-->", pos)

                if (pos.charFormat().font() != font or ccolor != color
                        or self.not_word_re.exactMatch(s[-1])):
                    moveprev(pos)
                    self.debugline("<--)", pos)
                    break;

            if pos.hasSelection():
                word = pos.selectedText()
                if self.debug:
                    self.component_manager.debug(
                        u'gogorender: word="%s"' % word)
                path = self.render_word(unicode(word), font, color)

                if path is not None:
                    render.append((unicode(word), unicode(path)))

            pos = doc.find(self.render_char_re, pos)

        if render:
            return self.substitute(unicode(text), render)
        else:
            return text

class GogorenderPlugin(Plugin):
    name = name
    description = description
    components = [GogorenderConfig, GogorenderConfigWdgt, Gogorender]

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)

    def activate(self):
        Plugin.activate(self)
        for chain in render_chains:
            try:
                self.new_render_chain(chain)
            except KeyError: pass

    def deactivate(self):
        Plugin.deactivate(self)
        for chain in render_chains:
            try:
                self.render_chain(chain).unregister_filter(Gogorender)
            except KeyError: pass

    def new_render_chain(self, name):
        if name in render_chains:
            self.render_chain(name).register_at_back(Gogorender)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GogorenderPlugin)

