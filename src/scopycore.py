
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

#ScoPy Core 2.0 'uid'

import random

pali = [0, 1, 2, 3]
pali_str = ["denari", "coppe", "bastoni", "spade"]
valori = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
valori_str = ["", "asso", "2", "3", "4", "5", "6", "7", "donna", "cavallo" ,"re"]
valori_set = [0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10]

#classe base: crea oggetti carta che hanno attributi palo e valore, interi che definiscono la carta univocamente
class carta():
	def __init__(self, palo, valore):
		self.palo = palo
		self.valore = valore
		self.uid = int(str(palo)+str(valore))
	def __add__(self, carta):
		return self.valore + carta.valore
	def __str__(self):
		return(valori_str[self.valore] + " di " + pali_str[self.palo])
sette = carta(1,7)
#classe che crea oggetti mazzo che hanno attributo carte, una lista di oggetti carta. La oggetto mazzo e' utilizzato
#sia per il mazzo che per le carte in mano, a terra e prese
class mazzo():
	def __init__(self, n=0):
		if n == 40:
			self.carte = gen_mazzo()
			self.mischia()
		else:
			self.carte =[]
	def mischia(self):
		num_carte = len(self.carte)
		for i in range(num_carte):
			j = random.randrange(0, num_carte)
			self.carte[i], self.carte[j] = self.carte[j], self.carte[i]
	def __getitem__(self, uid):
		for carta in self.carte:
			if carta.uid == uid:
				return carta
	def togli_carta(self, uid):
		carta_da_togliere = self[uid]
		for carta in self.carte:
			if carta.uid == uid:
				del self.carte[self.carte.index(carta)]
		return carta_da_togliere

#la classe crea oggetti giocatore, che hanno gli attributi nome(stringa), mano(oggetto mazzo che contiene le carte in mano),
#carte_prese(oggetto mazzo che contiene le carte prese)
class giocatore():
	def __init__(self, nome):
		if nome == '':
			self.nome = 'Giocatore'
		else:
			self.nome = nome
		self.mano = mazzo()
		self.carte_prese = mazzo()
		self.punti = 0
		self.scope = 0
		self.ult_scopa = [0,0]
		self.scoperte = 0
class ai():
	def __init__(self, nome):
		if nome == '':
			self.nome = 'Ai'
		else:
			self.nome = nome
		self.mano = mazzo()
		self.carte_prese = mazzo()
		self.punti = 0
		self.scope = 0
		self.ult_scopa = [0,0]
		self.scoperte = 0
		self.memoria = {}
class partita():
	def __init__(self, nome, nc):
		self.giocatore = [giocatore(nome), giocatore(nc)]
		self.mazzo = mazzo(40)
		self.carte_terra = mazzo()
		self.mano = 0
		self.ide = random.randrange(2)
		self.ult_prende = 0
		self.punti_vit = 11
	#trasferisce il numero di carte indicato dal mazzo a un giocatore o a terra
	def trasf_carte(self, num_carte, a, ide = 0):
		if a == "giocatore":
			n = 0
			while n < num_carte:
				self.giocatore[ide].mano.carte.append(self.mazzo.carte.pop())
				n = n + 1
		if a == "terra":
			n = 0
			while n < num_carte:
				self.carte_terra.carte.append(self.mazzo.carte.pop())
				n = n + 1
	#da' le carte ai giocatori e a terra se e' la prima mano
	def dai_carte(self):
		if len(self.mazzo.carte) != 0:
			self.trasf_carte(3, "giocatore", 0)
			self.trasf_carte(3, "giocatore", 1)
			if self.mano == 0:
				self.trasf_carte(4, "terra")
			self.mano = self.mano+1
	#gioca la carta indicata del giocatore indicato e prende le carte indicate da terra
	def gioca_carta(self, ide, uid_carta, uid_carte):
		#se non si prende niente
		if uid_carte == []:
			self.carte_terra.carte.append(self.giocatore[ide].mano.togli_carta(uid_carta))
		#se si prende qualcosa
		else:
			self.ult_prende = ide
			carta_giocata = self.giocatore[ide].mano.togli_carta(uid_carta)
			self.giocatore[ide].carte_prese.carte.append(carta_giocata)
			n = 0
			#verifica se si fa scopa
			if len(self.mazzo.carte) == 0 and len(self.giocatore[0].mano.carte)==0 and len(self.giocatore[1].mano.carte)==0:
				pass
			else:
				if len(uid_carte) == len(self.carte_terra.carte):
					self.giocatore[ide].scope = self.giocatore[ide].scope + 1
					self.giocatore[ide].ult_scopa = [carta_giocata.palo, carta_giocata.valore]
			#prende le carte da terra
			for uid in uid_carte:
				self.giocatore[ide].carte_prese.carte.append(self.carte_terra.togli_carta(uid))
	#valuta la migliore presa che il computer puo' fare
	def gioca_computer(self):
		carte_mano = self.giocatore[1].mano.carte
		carte_terra = self.carte_terra.carte
		giocate = []
		no_prese = 1
		n = 0
		i = 0
		while n < len(carte_mano):
			prese_possibili = self.prese(carte_mano[n])
			if prese_possibili != [[]]:
				no_prese = 0
			for presa in prese_possibili:
				giocate.append([n, presa])
			n = n+1
		#se solo 1 giocata possibile
		if len(giocate) == 1:
			giocate[0][0] = carte_mano[giocate[0][0]].uid
			n=0
			while n < len(giocate[0][1]):
				giocate[0][1][n] = carte_terra[giocate[0][1][n]].uid
				n=n+1
			return giocate[0]
		#se non si puo' prendere
		elif no_prese == 1:
			ide_carte = range(len(carte_mano))
			migliore = [0,[],-20]
			for ide_carta in ide_carte:
				valore = 0
				n = 0
				#2 carte uguali
				for carta in carte_mano:
					if carta.valore == carte_mano[ide_carta].valore:
						n = n + 1
				if n >= 2:
					valore = valore + 1
				#non denari
				if carte_mano[ide_carta].palo != 0:
					valore = valore + 1
				#non 7
				if carte_mano[ide_carta].valore != 7:
					valore = valore + 1
				n = 0
				#carta piu' bassa
				for carta in carte_mano:
					if carta.valore > carte_mano[ide_carta].valore:
						n = n + 1
				if n == len(carte_mano):
					valore = valore + 1
				#non 7 a terra
				if len(self.prese(sette)) != 0:
					valore = valore - 1
				#presa dopo
				for carta in carte_mano:
					if carta != carte_mano[ide_carta]:
						if len(self.prese(carta)) != 0:
							valore = valore + 1
				#scopa avversario
				valore_terra = 0
				for carta in carte_terra:
					valore_terra = valore_terra + carta.valore
				valore_terra = valore_terra + carte_mano[ide_carta].valore
				if valore_terra <= 10:
					valore = valore - 6
				if valore > migliore[2]:
					migliore[0], migliore[2] = ide_carta, valore
			migliore[0] = carte_mano[migliore[0]].uid
			n=0
			while n < len(migliore[1]):
				migliore[1][n] = carte_terra[migliore[1][n]].uid
				n=n+1
			return migliore[0:2]
		else:
			migliore = [0,[],-20]
			for giocata in giocate:
				valore = 0
				#scopa
				if len(giocata[1]) == len(carte_terra):
					valore = valore + 20
				valore_terra = 0
				#scopa avversario
				for ide_carta in range(len(carte_terra)):
					if not ide_carta in giocata[1]:
						valore_terra = valore_terra + carte_terra[ide_carta].valore
				if giocata[1] == []:
					valore_terra = valore_terra + carte_mano[giocata[0]].valore
				if valore_terra <= 10:
					valore = valore - 6
				if giocata[1] == []:
					#non denaro
					if carte_mano[giocata[0]].palo != 0:
						valore = valore + 1
					#non 7
					if carte_mano[giocata[0]].valore != 7:
						valore = valore + 1
					n = 0
					#carta piu' bassa
					for carta in carte_mano:
						if carta.valore > carte_mano[giocata[0]].valore:
							n = n + 1
					if n == len(carte_mano):
						valore = valore + 1
				else:
					carte_da_prendere=[]
					carte_da_prendere.append(carte_mano[giocata[0]])
					for ide_carta in giocata[1]:
						carte_da_prendere.append(carte_terra[ide_carta])	
					valore = valore + len(carte_da_prendere)
					for carta in carte_da_prendere:
						if carta.palo == 0:
							valore = valore + 3
						if carta.valore == 7:
							valore = valore + 4
							if carta.palo == 0:
								valore = valore + 20
						if carta.valore == 6:
							valore = valore + 2
						if carta.valore == 1:
							valore = valore + 1
				if valore > migliore[2]:
					migliore[0], migliore[1], migliore[2] = giocata[0], giocata[1], valore
			migliore[0] = carte_mano[migliore[0]].uid
			n=0
			while n < len(migliore[1]):
				migliore[1][n] = carte_terra[migliore[1][n]].uid
				n=n+1
			return migliore[0:2]
	def gioca_giocatore(self, uid):
		carta_giocata = self.giocatore[0].mano[uid]
		prese_possibili = self.prese(carta_giocata)
		for presa in prese_possibili:
			n=0
			while n < len(presa):
				presa[n] = self.carte_terra.carte[presa[n]].uid
				n=n+1
		return prese_possibili
	def combinazioni(self, lista):
		import itertools
		combinazioni = []
		i = 2
		while i <= len(lista)+1:
			lista_combinazioni = itertools.combinations(lista, i)
			for combinazione in lista_combinazioni:
				combinazione_list = []
				for elemento in combinazione:
					combinazione_list.append(elemento)
				combinazioni.append(combinazione_list)
			i=i+1
		return combinazioni
	def prese(self, carta, carte=0):
		if carte == 0:
			carte = self.carte_terra.carte
		prese = []
		n = 0
		while n < len(carte):
			if carta.valore == carte[n].valore:
				prese.append([n])
			n = n+1
		if len(prese) == 0:
			lista_combinazioni = self.combinazioni(range(len(carte)))
			for combinazione in lista_combinazioni:
				somma = 0
				for elemento in combinazione:
					somma = somma + carte[elemento].valore
				if somma == carta.valore:
					prese.append(combinazione)
		if prese == []:
			return [[]]
		else:			
			return prese
	#conta i punti alla fine della partita
	def conta_punti(self):
		#trasferisce le carte rimaste a terra a l'ultimo giocatore a prendere
		for carta in self.carte_terra.carte:
			self.giocatore[self.ult_prende].carte_prese.carte.append(carta)
		#conta i punti
		ritorno = {}
		#assegna le carte a lunga
		parziale = [0,0]
		if len(self.giocatore[0].carte_prese.carte) > len(self.giocatore[1].carte_prese.carte):
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif len(self.giocatore[1].carte_prese.carte) > len(self.giocatore[0].carte_prese.carte):
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Carte'] = [len(self.giocatore[0].carte_prese.carte), len(self.giocatore[1].carte_prese.carte)]
		#assegna la settanta
		valori_pali = [[0,0,0,0],[0,0,0,0]]
		n = 0
		while n < 2:
			i = 0
			while i < 4:
				for carta in self.giocatore[n].carte_prese.carte:
					if carta.palo == i:
						if valori_set[carta.valore] > valori_pali[n][i]:
							valori_pali[n][i] = valori_set[carta.valore]
				i = i+1
			n = n+1
		somma = [0,0]
		somma[0] = valori_pali[0][0]+valori_pali[0][1]+valori_pali[0][2]+valori_pali[0][3]
		somma[1] = valori_pali[1][0]+valori_pali[1][1]+valori_pali[1][2]+valori_pali[1][3]
		if somma[0] > somma[1]:
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif somma[1] > somma[0]:
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Primiera'] = somma
		#assegna il 7 bello
		for carta in self.giocatore[0].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 7:
				self.giocatore[0].punti = self.giocatore[0].punti + 1
				parziale[0] = parziale[0] + 1
				ritorno['Sette Bello'] = [1,0]
		for carta in self.giocatore[1].carte_prese.carte:
			if carta.palo == 0 and carta.valore == 7:
				self.giocatore[1].punti = self.giocatore[1].punti + 1
				parziale[1] = parziale[1] + 1
				ritorno['Sette Bello'] = [0,1]
		#assegna i denari
		denari = [0,0]
		n = 0
		while n < 2:
			for carta in self.giocatore[n].carte_prese.carte:
				if carta.palo == 0 :
					denari[n] = denari[n] + 1
			n = n+1
		if denari[0] > denari[1]:
			self.giocatore[0].punti = self.giocatore[0].punti + 1
			parziale[0] = parziale[0] + 1
		elif denari[1] > denari[0]:
			self.giocatore[1].punti = self.giocatore[1].punti + 1
			parziale[1] = parziale[1] + 1
		ritorno['Denari'] = denari
		#assegna le scope
		self.giocatore[0].punti = self.giocatore[0].punti + self.giocatore[0].scope
		parziale[0] = parziale[0] + self.giocatore[0].scope
		self.giocatore[1].punti = self.giocatore[1].punti + self.giocatore[1].scope
		parziale[1] = parziale[1] + self.giocatore[1].scope
		ritorno['Scope'] = [self.giocatore[0].scope, self.giocatore[1].scope]
		ritorno['Parziale'] = parziale
		return ritorno
	def get_carte_giocatore(self, ide):
		return self.giocatore[ide].mano.carte
	#azzera la partita quando si finisce il mazzo
	def azzera(self):
		self.mazzo = mazzo(40)
		self.mazzo.mischia()
		self.carte_terra = mazzo()
		for giocatore in self.giocatore:
			giocatore.mano = mazzo()
			giocatore.carte_prese = mazzo()
			giocatore.scope = 0
			giocatore.ult_scopa = [0, 0]
		self.ide = altro(self.ide)
		self.mano = 0
def gen_mazzo():
	carte = []
	for palo in pali:
		for valore in valori:
			carte.append(carta(palo,valore))
	return carte
	

def altro(ide):
	if ide == 0:
		return 1
	else:
		return 0
