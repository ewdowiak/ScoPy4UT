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

import sys, os
from gi.repository import Gtk,Clutter,GLib
import cairo

APP_VERSION = '0.4.2'
APP_NAME = 'scopy'

#setting up gettext
import gettext
from gettext import gettext as _
gettext.bindtextdomain('scopy', '/usr/share/locale')
gettext.textdomain('scopy')

#recupero percorsi dove si trovano le immagini
percorso = sys.path[0][0:-4]
percorso_tap = percorso+'/data/images/tappeti/'
percorso_carte = percorso+'/data/images/carte/'
percorso_gui = percorso+'/data/ui/'
percorso_doc = percorso+'/doc/'

#funzione per spostamenti
def go_to(actor,x,y,time):
	an = actor.animatev(Clutter.AnimationMode.EASE_IN_OUT_QUAD, time,['x','y'],[x,y])
	return an

#destroys the given widget
def destroy(widget, response):
	widget.destroy()

#nomi dei file delle immagini delle carte
immagini = [
	["0.png", "1d.png", "2d.png", "3d.png", "4d.png", "5d.png", "6d.png", "7d.png", "8d.png", "9d.png", "10d.png"],
	["bg.png", "1c.png", "2c.png", "3c.png", "4c.png", "5c.png", "6c.png", "7c.png", "8c.png", "9c.png", "10c.png"],
	["mazzo.png", "1b.png", "2b.png", "3b.png", "4b.png", "5b.png", "6b.png", "7b.png", "8b.png", "9b.png", "10b.png"],
	["0.png", "1s.png", "2s.png", "3s.png", "4s.png", "5s.png", "6s.png", "7s.png", "8s.png", "9s.png", "10s.png"]
]

#varianti
varianti = [_('Classic scopa'), _('Cirulla'), _('Cucita'), _('Re Bello')]

#tempo in ms da aspettare dopo che una carta viene giocata, si regola con self.velocita
times=[1,3000,2000,1000]

#caricamento tipi di carte
tipi_di_carte = []
for cartella in os.listdir(percorso_carte):
	if cartella[0] != '.':
		tipi_di_carte.append(cartella)
tipi_di_carte.sort()

#caricamento sfondi
sfondi = []
for cartella in os.listdir(percorso_tap):
	if cartella[0] != '.':
		sfondi.append(cartella[0:-4])
sfondi.sort()

class Carta():
	def __init__(self,palo,valore,tipo_carte):
		self.palo = palo
		self.valore = valore
		self.actor = Clutter.Texture.new_from_file(percorso_carte+tipo_carte+'/'+immagini[palo][valore])
	def get_actor(self):
		return self.actor
		
#container for clutter actor
class Box():
	def __init__(self, stage, rows, cols, x=0, y=0, spacing=5, padding=5, child_w=100, child_h=100):
		self.stage = stage
		self.rows = rows
		self.cols = cols
		self.x = x
		self.y = y
		self.spacing = spacing
		self.padding = padding
		self.child_w = child_w
		self.child_h = child_h
		self.width = 2*padding+cols*child_w+(cols-1)*spacing
		self.height = 2*padding+rows*child_h+(rows-1)*spacing
		self.back = Clutter.CairoTexture.new(self.width,self.height)
		self.back.set_position(self.x,self.y)
		self.stage.add_actor(self.back)
		self.draw_rect()
		self.children = []
		n=0
		while n<rows:
			self.children.append([])
			i=0
			while i<cols:
				self.children[n].append(0)
				i=i+1
			n=n+1

	def draw_rect(self):
		self.back.set_surface_size(self.width,self.height)
		self.back.clear()
		cr = self.back.create()
		cr.set_source_rgba(1,1,1,0.1)
		cr.move_to(2,2)
		cr.line_to(self.width-2,2)
		cr.line_to(self.width-2,self.height-2)
		cr.line_to(2,self.height-2)
		cr.line_to(2,2)
		cr.fill()
		self.back.invalidate()
		
	def set_children_coords(self):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] != 0:
					 self.children[n][i].set_x(self.x+self.padding+i*(self.child_w+self.spacing))
					 self.children[n][i].set_y(self.y+self.padding+n*(self.child_h+self.spacing))
				i=i+1
			n=n+1
	
	def set_x(self,x):
		self.x = x
		self.set_children_coords()
		self.back.set_position(self.x,self.y)
		
	def set_y(self,y):
		self.y = y
		self.set_children_coords()
		self.back.set_position(self.x,self.y)
		
	def set_child_w(self, w):
		self.child_w = w
		self.set_children_coords()
		self.width = 2*self.padding+self.cols*self.child_w+(self.cols-1)*self.spacing
		self.draw_rect()

	def set_child_h(self, h):
		self.child_h = h
		self.set_children_coords()
		self.height = 2*self.padding+self.rows*self.child_h+(self.rows-1)*self.spacing
		self.draw_rect()
		
	def set_child_size(self, w, h):
		self.set_child_w(w)
		self.set_child_h(h)
		
	def get_x(self):
		return self.x
		
	def get_y(self):
		return self.y
		
	def get_height(self):
		return self.height
		
	def get_width(self):
		return self.width

	def add(self, actor, time=500, add_to_stage=True):
		r,c=-1,-1
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] == 0 and (r,c)==(-1,-1):
					r,c=n,i
					break
				i=i+1
			n=n+1
		self.children[r][c]=actor
		x=self.x+self.padding+c*(self.child_w+self.spacing)
		y=self.y+self.padding+r*(self.child_h+self.spacing)
		if add_to_stage:
			self.stage.add_actor(actor)
		go_to(actor,x,y,time)
		
	def remove(self, actor):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] == actor:
					self.children[n][i] = 0
				i=i+1
			n=n+1

	def move_to(self, actor, new_box, time=500):
		self.remove(actor)
		new_box.add(actor,time,False)
	
	def get_child_pos(self, actor):
		r,c=-1,-1
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				if self.children[n][i] == actor:
					r,c=n,i
				i=i+1
			n=n+1
		x=self.x+self.padding+c*(self.child_w+self.spacing)
		y=self.y+self.padding+r*(self.child_h+self.spacing)
		return x,y
		
	def clean(self):
		n=0
		while n<self.rows:
			i=0
			while i<self.cols:
				self.children[n][i] = 0
				i=i+1
			n=n+1
		
#container for clutter actor
class Mazzo():
	def __init__(self, stage, name, x=0, y=0, padding=5, child_w=100, child_h=100):
		self.stage = stage
		self.x = x
		self.y = y
		self.padding = padding
		self.surface = cairo.ImageSurface.create_from_png(name)
		self.child_w = self.surface.get_width()
		self.child_h = self.surface.get_height()
		self.width = 2*padding+self.child_w
		self.height = 2*padding+self.child_h
		self.actor = Clutter.CairoTexture.new(self.width+20,self.height+20)
		self.actor.set_position(x+padding,y+padding)
		self.stage.add_actor(self.actor)
		self.children = 0
	
	def draw(self):
		c=self.children/2
		cr = self.actor.create()
		n=0
		while n<c:
			cr.set_source_surface(self.surface,n,n)
			cr.paint()
			n=n+1
		self.actor.invalidate()
	
	def set_retro(self, name):
		self.surface = cairo.ImageSurface.create_from_png(name)
		self.actor.clear()
		self.draw()
		
	def set_child_w(self, w):
		self.child_w = w
		self.width = 2*self.padding+self.child_w

	def set_child_h(self, h):
		self.child_h = h
		self.height = 2*self.padding+self.child_w
		
	def set_child_size(self, w, h):
		self.set_child_w(w)
		self.set_child_h(h)
	
	def set_x(self,x):
		self.x=x
		self.actor.set_x(x+self.padding)
	
	def set_y(self,y):
		self.y=y
		self.actor.set_y(y+self.padding)
		
	def get_height(self):
		return self.height
		
	def get_width(self):
		return self.width
		
	def get_x(self):
		return self.x
		
	def get_y(self):
		return self.y

	def add(self, actor, time=500, add_to_stage=True):
		self.children = self.children+1
		go_to(actor,self.x+self.padding,self.y+self.padding,time)
		GLib.timeout_add(time,actor.destroy)
		GLib.timeout_add(time,self.draw)
		
	def clean(self):
		self.children = 0
		self.actor.clear()
		self.actor.invalidate()

#container for clutter actor
class Scope():
	def __init__(self, stage, x=0, y=0, padding=5, child_w=100, child_h=100):
		self.stage = stage
		self.x = x
		self.y = y
		self.padding = padding
		self.surface = 0
		self.scope = 0
		self.child_w = child_w
		self.child_h = child_h
		self.width = 2*padding+child_w
		self.height = 2*padding+child_h
		self.actor = Clutter.CairoTexture.new(self.width+20,self.height+20)
		self.actor.set_position(x+padding,y+padding)
		self.stage.add_actor(self.actor)
	
	def set_n_scope(self, n):
		self.scope = n
		self.draw()
	
	def set_scopa(self, nome):
		self.actor.clear()
		self.surface = cairo.ImageSurface.create_from_png(nome)
		self.draw()
	
	def draw(self):
		cr = self.actor.create()
		if self.surface != 0:
			cr.set_source_surface(self.surface)
			cr.paint()
		if self.scope != 0:
			cr.set_font_size(15)
			xb, yb, w, h, xadvance, yadvance = (cr.text_extents(str(self.scope)))
			cr.set_source_rgb(0,0,0)
			cr.move_to(self.width-2*self.padding-w-10,0)
			cr.line_to(self.width-2*self.padding,0)
			cr.line_to(self.width-2*self.padding,+h+10)
			cr.line_to(self.width-2*self.padding-w-10,+h+10)
			cr.line_to(self.width-2*self.padding-w-10,0)
			cr.fill()
			cr.set_font_size(15)
			cr.move_to(self.width-2*self.padding-w-5,+h+5)
			cr.set_source_rgb(1,1,1)
			cr.show_text(str(self.scope))
		self.actor.invalidate()
		
	def set_child_w(self, w):
		self.child_w = w
		self.width = 2*self.padding+self.child_w

	def set_child_h(self, h):
		self.child_h = h
		self.height = 2*self.padding+self.child_w
		
	def set_child_size(self, w, h):
		self.set_child_w(w)
		self.set_child_h(h)
	
	def set_x(self,x):
		self.x=x
		self.actor.set_x(x+self.padding)
	
	def set_y(self,y):
		self.y=y
		self.actor.set_y(y+self.padding)
		
	def get_height(self):
		return self.height
		
	def get_width(self):
		return self.width
		
	def get_x(self):
		return self.x
		
	def get_y(self):
		return self.y
		
	def clean(self):
		self.surface = 0
		self.scope = 0
		self.actor.clear()
		self.actor.invalidate()

class Obj():
	def __init__(self, stage, carta, opzioni, scoperta):
		self.uid = carta.uid
		if scoperta:
			self.object = Clutter.Texture.new_from_file(percorso_carte+opzioni['carte']+'/'+immagini[carta.palo][carta.valore])
		else:
			self.object = Clutter.Texture.new_from_file(percorso_carte+opzioni['carte']+'/'+immagini[1][0])

class Carte():
	def __init__(self):
		self.carte = []
	def __getitem__(self, uid):
		if type(uid) == int:
			for carta in self.carte:
				if carta.uid == uid:
					return carta.object
		else:
			for carta in self.carte:
				if carta.object == uid:
					return carta.uid
	def __delitem__(self, uid):
		n=0
		while n < len(self.carte):
				if self.carte[n].uid == uid:
					del self.carte[n]
				n=n+1
	def append(self, obj):
		self.carte.append(obj)
