# coding: utf-8

##
# Project: ScoPy
# Author: Marco Scarpetta <marcoscarpetta@mailoo.org>
# Copyright: 2012 Marco Scarpetta
# License: GPL-3+
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# On Debian GNU/Linux systems, the full text of the GNU General Public License
# can be found in the file /usr/share/common-licenses/GPL-3.
##

import re
from gi.repository import Gtk

#importing modules
import Start
import Settings
import About
import Quit
import Help
import LastMove

#modules tuple
modules = [
	Start,
	LastMove,
	Settings,
	Help,
	About,
	Quit
	]

#returns the Gtk.MenuBar with all the menus
def create_menu(app):
	menubar = Gtk.MenuBar()
	for module in modules:
		path = re.split(':',module.Path)
		add(menubar,path,module.main,module.Name,app)
	return menubar

def add(menu,path,func,name,app):
	if len(path) > 0:
		items = menu.get_children()
		for item in items:		
			if item.get_label() == path[0]:
				if item.get_submenu() != None:
					submenu = item.get_submenu()
					add(submenu,path[1:],func,name,app)
					break
		else:
			submenu = Gtk.Menu()
			menuitem = Gtk.MenuItem()
			menuitem.set_label(path[0])
			menuitem.set_submenu(submenu)
			menu.append(menuitem)
			add(submenu,path[1:],func,name,app)
	else:
		menuitem = Gtk.MenuItem()
		menuitem.set_label(name)
		menuitem.connect('activate', func, app)
		menu.append(menuitem)
