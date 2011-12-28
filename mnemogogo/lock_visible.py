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

#
# Wrapper to lock the visible status of QWidget instances
#
# To add locking to a widget:
#   add(widget)
#
# To remove locking from a widget:
#   widget.removeLocking()
#
# When locking is available:
#   To lock in the hidden state:      widget.hideAndLock()
#   To unlock and restore the state:  widget.unlockAndRestore()
#

import types

def _showWithLocking(self):
    self._hidden = False
    if not self._locked:
        self._show()

def _hideWithLocking(self):
    self._hidden = True
    if not self._locked:
        self._hide()

def _hideAndLock(self):
    self._locked = True
    self._hide()

def _showAndLock(self):
    self._locked = True
    self._show()

def _unlockAndRestore(self):
    self._locked = False
    if self._hidden:
        self._hide()
    else:
        self._show()

def _removeLocking(self):
    self.unlockAndRestore()

    self.show = self._show
    self.hide = self._hide

    del self.__dict__['_hidden']
    del self.__dict__['_locked']
    del self.__dict__['_show']
    del self.__dict__['_hide']
    del self.__dict__['hideAndLock']
    del self.__dict__['showAndLock']
    del self.__dict__['unlockAndRestore']
    del self.__dict__['removeLocking']

def add(obj):
    dict = obj.__class__.__dict__

    obj._hidden = obj.isHidden()
    obj._locked = False

    obj._show = obj.show
    obj._hide = obj.hide

    obj.show = types.MethodType(_showWithLocking, obj)
    obj.hide = types.MethodType(_hideWithLocking, obj)

    obj.showAndLock = types.MethodType(_showAndLock, obj)
    obj.hideAndLock = types.MethodType(_hideAndLock, obj)
    obj.unlockAndRestore = types.MethodType(_unlockAndRestore, obj)
    obj.removeLocking = types.MethodType(_removeLocking, obj)

