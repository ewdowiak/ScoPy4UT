
##
# Project: ScoPy - The italian card game 'scopa'
# Author: Marco Scarpetta <marcoscarpetta02@gmail.com>
# Copyright: 2011 Marco Scarpeta
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

import pygtk
pygtk.require('2.0')
import gtk.glade
import gtk
import glib
import sys, os
import classica

percorso = os.path.abspath(os.path.dirname(sys.argv[0]))[0:-4]+'/data/images/'
percorso_carte = os.path.abspath(os.path.dirname(sys.argv[0]))[0:-4]+'/data/images/carte/'
percorso_gui = os.path.abspath(os.path.dirname(sys.argv[0]))[0:-4]+'/data/ui/'
velocit = [0, 3, 2, 1]
immagini = [
	["0.png", "1d.png", "2d.png", "3d.png", "4d.png", "5d.png", "6d.png", "7d.png", "8d.png", "9d.png", "10d.png"],
	["bg.png", "1c.png", "2c.png", "3c.png", "4c.png", "5c.png", "6c.png", "7c.png", "8c.png", "9c.png", "10c.png"],
	["mazzo.png", "1b.png", "2b.png", "3b.png", "4b.png", "5b.png", "6b.png", "7b.png", "8b.png", "9b.png", "10b.png"],
	["0.png", "1s.png", "2s.png", "3s.png", "4s.png", "5s.png", "6s.png", "7s.png", "8s.png", "9s.png", "10s.png"]
]
varianti = ['Classica', 'Cirulla', 'Cucita', 'Re Bello']

def yieldsleep(func):
    def start(*args, **kwds):
        iterable = func(*args, **kwds)
        def step(*args, **kwds):
            try:
                time = next(iterable)
                glib.timeout_add_seconds(time, step)
            except StopIteration:
                pass
        glib.idle_add(step)
    return start

class main_win(object):
	def __init__(self):
		#carica le impostazioni
		d = os.path.expanduser('~')+"/.scopy"
		if not os.path.exists(os.path.expanduser('~')+"/.scopy"):
			os.makedirs(d)
			config = open(os.path.expanduser('~')+"/.scopy/config.pck", 'w')
			config.close()
		self.carica()
		self.percorso = percorso_carte + self.default['carte']+'/'
		self.gladeFile = gtk.glade.XML(percorso_gui+'gtk2.glade')
		#servono per dei controlli nell'esecuzione
		self.control0 = 0
		self.control1 = 0
		self.control2 = 1
		self.giocatore = 0
		#connessione segnali
		segnali = {
			'on_main_win_destroy': self.on_main_win_destroy,
			'on_nuova_clicked': self.nuova_partita,
			'on_about_clicked': self.about,
			'on_inizia_clicked': self.gioca_partita,
			'on_modifica_clicked': self.modifica_impostazioni,
			'on_impostazioni_clicked': self.impostazioni,
			'on_about_close': self.about_close,
		}
		self.gladeFile.signal_autoconnect(segnali)
		#importazione widgets
		self.main_win = self.gladeFile.get_widget('main_win')
		self.main_win.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#279a32"))
		self.main_win.set_icon_from_file(os.path.abspath(os.path.dirname(sys.argv[0]))[0:-4]+'/data/icons/icona32.png')
		self.inizio = self.gladeFile.get_widget('inizio')
		self.inizio.connect("delete-event", self.chiudi)
		self.modifica = self.gladeFile.get_widget('modifica')
		self.modifica.connect("delete-event", self.chiudi)
		self.turni = self.gladeFile.get_widget('turni')
		self.dic_texts = [self.gladeFile.get_widget('dic_gio'),
			self.gladeFile.get_widget('dic_com')
		]
		self.aboutdialog = self.gladeFile.get_widget('aboutdialog')
		self.entry = self.gladeFile.get_widget('entry')
		self.combo_tipo_carte = self.gladeFile.get_widget('tipo_carte')
		self.combo_tipo_carte1 = self.gladeFile.get_widget('tipo_carte1')
		self.combo_variante = self.gladeFile.get_widget('variante')
		self.hscale = self.gladeFile.get_widget('hscale')
		self.hscale1 = self.gladeFile.get_widget('hscale1')
		self.aboutdialog.connect("response", self.about_close)
		#finestra comunicazione
		self.comunicazione = self.gladeFile.get_widget('comunicazione')
		self.riepilogo = self.gladeFile.get_widget('riepilogo')
		self.com_text = self.gladeFile.get_widget('testo')
		self.rie_1 = self.gladeFile.get_widget('r1')
		self.rie_2 = self.gladeFile.get_widget('r2')
		self.rie_3 = self.gladeFile.get_widget('r3')
		self.rie_but = self.gladeFile.get_widget('button')
		self.rie_but.connect("clicked", self.fine_partita)
		#finestra scelta presa
		self.win_scelta_presa = self.gladeFile.get_widget('scelta_presa')
		self.prese = []
		n = 0
		while n < 4:
			self.prese.append([])
			i = 0
			while i < 4:
				self.prese[n].append(self.gladeFile.get_widget('p'+str(n)+str(i)))
				i = i+1
			n = n+1
		for lista_immagini in self.prese:
			for immagine in lista_immagini:
				immagine.set_from_file(self.percorso+immagini[0][0])
		#carte finestra principale
		self.cpc = self.gladeFile.get_widget('cpc')
		self.cpg = self.gladeFile.get_widget('cpg')
		self.sc = self.gladeFile.get_widget('sc')
		self.sg = self.gladeFile.get_widget('sg')
		self.carte_terra = []
		self.carte_giocatore = []
		self.carte_computer = []
		n = 0
		while n < 10:
			self.carte_terra.append(self.gladeFile.get_widget('ct'+str(n)))
			n = n+1
		n = 0
		while n < 3:
			self.carte_giocatore.append(self.gladeFile.get_widget('cg'+str(n)))
			self.carte_giocatore[n].connect("clicked", self.gioca, n)
			n = n+1
		n = 0
		while n < 3:
			self.carte_computer.append(self.gladeFile.get_widget('cc'+str(n)))
			n = n+1
		#le gtk.Images vengono settate trasparenti
		for immagine in self.carte_terra:
			immagine.set_from_file(self.percorso+immagini[0][0])
		for immagine in self.carte_computer:
			immagine.set_from_file(self.percorso+immagini[0][0])
		self.cpc.set_from_file(self.percorso+immagini[0][0])
		self.cpg.set_from_file(self.percorso+immagini[0][0])
		self.sc.set_from_file(self.percorso+immagini[0][0])
		self.sg.set_from_file(self.percorso+immagini[0][0])
		#caricamento tipi di carte
		self.tipi_di_carte = []
		for cartella in os.listdir(percorso_carte):
			if cartella[0] != '.':
				self.tipi_di_carte.append(cartella)
		self.tipi_di_carte.sort()
		for tipo in self.tipi_di_carte:
			self.combo_tipo_carte.append_text(tipo)
			self.combo_tipo_carte1.append_text(tipo)
		for variante in varianti:
			self.combo_variante.append_text(variante)
		self.main_win.show_all()
		#caricamento immagine di sfondo
		pixbuf = gtk.gdk.pixbuf_new_from_file(percorso+'tappeti/tappeto.png')
		self.pixmap, mask = pixbuf.render_pixmap_and_mask()
		width, height = self.pixmap.get_size()
		self.main_win.set_app_paintable(True)
		self.main_win.window.set_back_pixmap(self.pixmap, False)
		self.win_scelta_presa.set_app_paintable(True)
		#mostra la finestra inizio partita
		self.nuova_partita()
	#la funzione viene chiamata dal segnale omonimo e termina il programma
	def on_main_win_destroy(self, widget, data=None):
		gtk.main_quit()
	def carica(self):
		import pickle
		try:
			config = open(os.path.expanduser('~')+"/.scopy/config.pck", 'r')
			self.default = pickle.load(config)
			config.close()
		except:
			config = open(os.path.expanduser('~')+"/.scopy/config.pck", 'w')
			pickle.dump({
				'nome': 'Giocatore',
				'carte': 'Napoletane',
				'speed': 3,
				'variante': 'Classica'
			}, config)
			config.close()
			self.carica()
	def salva(self):
		import pickle
		config = open(os.path.expanduser('~')+"/.scopy/config.pck", 'w')
		pickle.dump(self.default, config)
		config.close()
	def nuova_partita(self, widget=None, data=None):
		self.carica()
		self.entry.set_text(self.default['nome'])
		self.entry.select_region(0,-1)
		self.hscale.set_value(self.default['speed'])
		self.combo_tipo_carte.set_active(self.tipi_di_carte.index(self.default['carte']))
		try:
			self.combo_variante.set_active(varianti.index(self.default['variante']))
		except:
			self.default['variante'] = 'Classica'
			self.salva()
		self.inizio.show_all()
	def impostazioni(self, widget=None, data=None):
		self.carica()
		self.hscale1.set_value(self.default['speed'])
		self.combo_tipo_carte1.set_active(self.tipi_di_carte.index(self.default['carte']))
		self.modifica.show_all()
	def chiudi(self, finestra=None, data=None):
		finestra.hide()
		return True
	def about(self, widget=None, data=None):
		self.aboutdialog.show_all()
	def about_close(self, widget=None, data=None):
		self.aboutdialog.hide()
	def crea_partita(self, variante, nome):
		if variante == None:
			import classica
			self.partita = classica.partita(nome)
		if variante == 'Classica':
			import classica
			self.partita = classica.partita(nome)
		if variante == 'Cirulla':
			import cirulla
			self.partita = cirulla.partita(nome)
		if variante == 'Cucita':
			import cucita
			self.partita = cucita.partita(nome)
		if variante == 'Re Bello':
			import re_bello
			self.partita = re_bello.partita(nome)
	#la funzione crea un oggetto partita e da inizio alla partita
	@yieldsleep
	def gioca_partita(self, widget, data=None):
		if self.combo_tipo_carte.get_active_text() == None:
			carte = self.default['carte']
		else:
			carte = self.combo_tipo_carte.get_active_text()
		self.percorso = percorso_carte + carte+'/'
		nome = self.entry.get_text()
		variante = self.combo_variante.get_active_text()
		self.crea_partita(variante, nome)
		speed = int(self.hscale.get_value())
		self.speed = velocit[speed]
		self.default = {
			'nome': nome,
			'carte': carte,
			'speed': speed,
			'variante': variante
		}
		self.salva()
		self.inizio.hide()
		if self.partita.ide == 1:
			self.comunica("Comincio io")
		else:
			self.comunica("Cominci tu")
		yield 2
		self.comunicazione.hide()
		if self.partita.ide == 0:
			self.gioca_giocatore()
		else:
			self.gioca_computer()
	def modifica_impostazioni(self, widget, data=None):
		if self.combo_tipo_carte1.get_active_text() == None:
			carte = self.default['carte']
		else:
			carte = self.combo_tipo_carte1.get_active_text()
		self.percorso = percorso_carte + carte+'/'
		speed = int(self.hscale1.get_value())
		self.speed = velocit[speed]
		self.default['carte'] = carte
		self.default['speed'] = speed
		self.salva()
		self.stampa()
		self.modifica.hide()
	def gioca_giocatore(self):
		self.control2 = 0
		if len(self.partita.giocatore[0].mano.carte) == 0 and len(self.partita.giocatore[1].mano.carte) == 0:
			if len(self.partita.mazzo.carte) == 0:
				self.riepiloga()
			dichiarazione = self.partita.dai_carte()
			self.dichiara(dichiarazione)
		self.stampa()
	@yieldsleep
	def gioca_computer(self):
		if len(self.partita.giocatore[0].mano.carte) == 0 and len(self.partita.giocatore[1].mano.carte) == 0:
			if len(self.partita.mazzo.carte) == 0:
				self.riepiloga()
			dichiarazione = self.partita.dai_carte()
			self.dichiara(dichiarazione)
		self.stampa()
		yield 1
		giocata = self.partita.gioca_computer()
		self.carte_terra[len(self.partita.carte_terra.carte)].set_from_file(self.percorso+immagini[self.partita.giocatore[1].mano.carte[giocata[0]].palo][self.partita.giocatore[1].mano.carte[giocata[0]].valore])
		self.carte_computer[giocata[0]].set_from_file(self.percorso+immagini[0][0])
		if len(giocata[1]) != 0:
			yield self.speed
		self.partita.gioca_carta(1, giocata[0], giocata[1])
		self.stampa()
		self.gioca_giocatore()
	@yieldsleep
	def gioca(self, widget, ide_carta):
		if self.control2 == 0:
			self.control2 = 1
			self.carte_terra[len(self.partita.carte_terra.carte)].set_from_file(self.percorso+immagini[self.partita.giocatore[0].mano.carte[ide_carta].palo][self.partita.giocatore[0].mano.carte[ide_carta].valore])
			immagine = gtk.Image()
			immagine.set_from_file(self.percorso+immagini[0][0])
			self.carte_giocatore[ide_carta].set_image(immagine)
			yield 1
			prese_possibili = self.partita.gioca_giocatore(ide_carta)
			if len(prese_possibili) == 0:
				self.partita.gioca_carta(0, ide_carta, prese_possibili)
				self.stampa()
				self.gioca_computer()
			elif len(prese_possibili) == 1:
				self.partita.gioca_carta(0, ide_carta, prese_possibili[0])
				self.stampa()
				self.gioca_computer()
			else:
				self.scelta_presa(prese_possibili, ide_carta)
	#la funzione permette di visualizzare tutte le carte interessate nella partita nella gtk.Window
	def stampa(self):
		#mostra i turni restanti e i punti
		self.turni.set_markup(
			'<span foreground="white">Turni restanti: '
			+str(len(self.partita.mazzo.carte)/6)
			+' \n\nComp.  '+str(self.partita.giocatore[1].punti)
			+'\n'+self.partita.giocatore[0].nome+'  '
			+str(self.partita.giocatore[0].punti)
			+'</span>'
			)
		#mostra le carte a terra
		for immagine in self.carte_terra:
			immagine.set_from_file(self.percorso+immagini[0][0])
		n = 0
		while n < len(self.partita.carte_terra.carte):
			self.carte_terra[n].set_from_file(self.percorso+immagini[self.partita.carte_terra.carte[n].palo][self.partita.carte_terra.carte[n].valore])
			n = n+1
		#mostra le carte in mano al giocatore
		for bottone in self.carte_giocatore:
			immagine = gtk.Image()
			immagine.set_from_file(self.percorso+immagini[0][0])
			bottone.set_image(immagine)
			bottone.set_sensitive(0)
		n = 0
		while n < len(self.partita.giocatore[0].mano.carte):
			immagine = gtk.Image()
			immagine.set_from_file(self.percorso+immagini[self.partita.giocatore[0].mano.carte[n].palo][self.partita.giocatore[0].mano.carte[n].valore])
			self.carte_giocatore[n].set_image(immagine)
			self.carte_giocatore[n].set_sensitive(1)
			n = n+1
		#mostra le carte in mano al computer
		for immagine in self.carte_computer:
			immagine.set_from_file(self.percorso+immagini[0][0])
		if self.partita.giocatore[1].scoperte == 1:
			n = 0
			while n < len(self.partita.giocatore[1].mano.carte):
				self.carte_computer[n].set_from_file(self.percorso+immagini[self.partita.giocatore[1].mano.carte[n].palo][self.partita.giocatore[1].mano.carte[n].valore])
				n = n+1
		else:
			n = 0
			while n < len(self.partita.giocatore[1].mano.carte):
				self.carte_computer[n].set_from_file(self.percorso+immagini[1][0])
				n = n+1
		#mostra le carte prese come un'unico retro
		if len(self.partita.giocatore[0].carte_prese.carte) > 0:
			self.cpg.set_from_file(self.percorso+immagini[2][0])
		else:
			self.cpg.set_from_file(self.percorso+immagini[0][0])
		if len(self.partita.giocatore[1].carte_prese.carte) > 0:
			self.cpc.set_from_file(self.percorso+immagini[2][0])
		else:
			self.cpc.set_from_file(self.percorso+immagini[0][0])
		#mostra l'ultima scopa
		self.sc.set_from_file(self.percorso+immagini[self.partita.giocatore[1].ult_scopa[0]][self.partita.giocatore[1].ult_scopa[1]])
		self.sg.set_from_file(self.percorso+immagini[self.partita.giocatore[0].ult_scopa[0]][self.partita.giocatore[0].ult_scopa[1]])
	def scelta_presa(self, prese_possibili, ide_carta):
		prese_possibili = prese_possibili
		ide_carta = ide_carta
		self.win_scelta_presa.show()
		self.win_scelta_presa.window.set_back_pixmap(self.pixmap, False)
		self.bot_prese = []
		n = 0
		while n < 4:
			self.bot_prese.append(self.gladeFile.get_widget('p'+str(n)))
			self.bot_prese[n].connect("clicked", self.scelta, prese_possibili, ide_carta, n)
			n = n+1
		for bottone in self.bot_prese:
			bottone.hide()
		n = 0
		while n < len(prese_possibili):
			self.bot_prese[n].show()
			n = n+1
		for lista_immagini in self.prese:
			for immagine in lista_immagini:
				immagine.hide()
		n = 0
		while n < len(prese_possibili):
			i = 0
			while i < len(prese_possibili[n]):
				self.prese[n][i].set_from_file(self.percorso+immagini[self.partita.carte_terra.carte[prese_possibili[n][i]].palo][self.partita.carte_terra.carte[prese_possibili[n][i]].valore])
				self.prese[n][i].show()
				i = i+1
			n = n+1
		return
	@yieldsleep
	def scelta(self, widget, prese_possibili, ide_carta, ide_presa):
		if self.control1 > 0:
			self.control1 = self.control1-1
		else:
			self.control0 = self.control0+1
			self.control1 = self.control0
			self.win_scelta_presa.hide()
			self.partita.gioca_carta(0, ide_carta, prese_possibili[ide_presa])
			yield 1
			self.gioca_computer()
	def riepiloga(self):
		punti = self.partita.conta_punti()
		colonne = ['\n',self.partita.giocatore[0].nome+'\n','Comp.'+'\n']
		for voce in punti:
			if voce != 'Parziale':
				colonne[0] = colonne[0] + voce + '\n'
				colonne[1] = colonne[1] + str(punti[voce][0]) + '\n'
				colonne[2] = colonne[2] + str(punti[voce][1]) + '\n'
		colonne[0] = colonne[0] + 'Parziale' + '\n'
		colonne[1] = colonne[1] + str(punti['Parziale'][0]) + '\n'
		colonne[2] = colonne[2] + str(punti['Parziale'][1]) + '\n'
		colonne[0] = colonne[0] + 'Punti'
		colonne[1] = colonne[1] + str(self.partita.giocatore[0].punti)
		colonne[2] = colonne[2] + str(self.partita.giocatore[1].punti)
		self.rie_1.set_text(colonne[0])
		self.rie_2.set_text(colonne[1])
		self.rie_3.set_text(colonne[2])
		self.riepilogo.show_all()
	@yieldsleep
	def fine_partita(self, widget, data=None):
		self.riepilogo.hide()
		self.stampa()
		if self.partita.giocatore[0].punti >= self.partita.punti_vit or self.partita.giocatore[1].punti >= self.partita.punti_vit and self.partita.giocatore[0].punti != self.partita.giocatore[1].punti:
			if self.partita.giocatore[0].punti > self.partita.giocatore[1].punti:
				self.comunica("Hai vinto!")
			else:
				self.comunica("Ho vinto!")
			yield 3
			self.comunicazione.hide()
			self.inizio.show_all()
			return
		self.partita.azzera()
		if self.partita.ide == 1:
			self.comunica("Comincio io")
		else:
			self.comunica("Cominci tu")
		yield 2
		self.comunicazione.hide()
		if self.partita.ide == 0:
			self.gioca_giocatore()
		else:
			self.gioca_computer()
	#mostra le strighe contenute nella lista 'testi' nella finestra 'comunicazione'
	def comunica(self, testo):
		self.com_text.set_markup('\n   '+testo+'   \n')
		self.comunicazione.show()
		return
	@yieldsleep
	def dichiara(self, dichiarazione):
		if dichiarazione != None:
			n=0
			while n < 2:
				if dichiarazione[n] != '':
					self.dic_texts[n].show()
					self.dic_texts[n].set_markup('<span foreground="white">'+dichiarazione[n]+'</span>')
				n = n + 1
			yield 5
			for dic in self.dic_texts:
				dic.set_text('')
			return
	def main(self):
		gtk.main()
def altro(ide):
	if ide == 0:
		return 1
	else:
		return 0

mainwin = main_win()
mainwin.main()
