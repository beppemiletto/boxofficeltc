'''
Created on 02 ott 2017

to use with pre OS command
ssh -n -N -f -L 3306:127.0.0.1:3306 ltc@teatrocambiano.sytes.net
for tunneling connection to mysql server if used from remote location

@author: beppe
'''
# Simple enough, just import everything from tkinter.
import gi  # @UnusedImport
##gi.require_version('Gtk', '3.0')
##gi.require_version('Atspi', '2.0')
# from gi.repository import Gtk, Gdk

from tkinter import Tk,Frame,Label,Listbox,Entry, Toplevel, Button,Text,Menu
from tkinter import BOTH,CENTER,NW,S,W,N,E,END,LEFT
from tkinter import DISABLED,NORMAL,RAISED,FLAT,RIDGE,SUNKEN,BROWSE,X,Y  # @UnusedImport
from tkinter import messagebox
from tkinter.ttk import Treeview
import MySQLdb

#download and install pillow:
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
from PIL import ImageTk
from PIL import Image
from button_array_location import rows_name,seats  # @UnresolvedImport
from datetime import timedelta
from collections import defaultdict,Counter
from decimal import Decimal
import time, pytz
import pickle
import os.path
from escpos.printer import Usb, Dummy
import sys




# from tunneling_mysql import MySQL_Ssh_Tunnel  # @UnresolvedImport
## GLOBAL SETTINGS AND VARIABLE

# FONTS FOR GUI
HUGE_FONT = ("DejaVuSansMono", 12)
LARGE_FONT = ("DejaVuSansMono", 10)
NORM_FONT = ("DejaVuSansMono", 8)
MEDIUM_FONT = ("DejaVuSansMono", 7)
SMALL_FONT = ("DejaVuSansMono", 6)
# HUGE_FONT = ("Verdana", 16)
# LARGE_FONT = ("Verdana", 12)
# NORM_FONT = ("Verdana", 9)
# SMALL_FONT = ("Verdana", 7)

# SEATS STATUS CODE
UNAVAILABLE = '0'
AVAILABLE 	= '1'
BOOKED 		= '2'
SOLD		= '3'
UNDER_BOOK	= '5'

# PROCES CODES
FREE_PRICE 		= 0
REDUCED_PRICE 	= 1
FULL_PRICE 		= 2

# MNEMONIC TICKET NAME
TICKET = ['GRATUITO', 'RIDOTTO',  'INTERO']


# RUNNING MODE SET
DEVELOPMENT = 1
PRODUCTION  = 0
running_mode = PRODUCTION

#mode for Windows INIT
INIT 		= 1
REINIT		= 2

# modes for toggle seat buttons
REQUEST_CHANGE = 4
TOGGLE 		= 3
DISABLE 	= 2
SELECT 		= 1
DESELECT 	= 0

# modes for TopLevel actions with selection
SELLABOOK 	= 4
SELL 		= 3
BOOK 		= 2
CLEAR 		= 0

# modes for Totalizers Refresh
OPENING		= 1
SESSION		= 2
FULL		= 3

# modes for BookingSoldStatusManager function
CHECK 		= 1
SOLD_CHECK 	= 2
UPDATE 		= 3

class BookingCodeError(LookupError):
	'''Errore nel formato del codice di prenotazione letto.'''
	
# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window(Frame):

	# Define settings upon initialization. Here you can specify
	def __init__(self, master=None):
		## Instantiate the buffer of selected seat for operations like
		## booking, selling, change status,
		self.SelectionBuffer=[]
		## Instantiate the flag of Event data changed compared to frozen session
		## used for checking session data not saved
		self.EventDataChanged=False
		## Instantiate the session open flag used to check the session status
		## Initialize to False, become true at event open, False again when event session is closed clear
		self.session_open = False

		## Initialize total counters for ticket sells
		self.TotalSoldFullPrice= 0
		self.TotalSoldReducedPrice=0
		self.TotalFreePrice=0
		self.TotalSellsOperations=0
		
		# Initialize the ESCPOS printer
		try:
			self.escprinter = Usb(0x0471, 0x0055,timeout=0,in_ep=0x82, out_ep=0x02)
			print('Trovata stampante ESCPOS')
		except:
			print("Errore stampante ESCPOS: '{}'. Controllare la stampante".format(sys.exc_info()[0]))
			self.escprinter = Dummy()
			print('Procedo con Dummy driver.')
			
			
		
		# parameters that you want to send through the Frame class.
		Frame.__init__(self, master)

		#reference to the master widget, which is the tk window
		self.master = master

		#with that, we want to then run init_window, which doesn't yet exist
		self.init_window(mode=INIT)



	#Creation of init_window
	def init_window(self, mode=None):

		if mode==INIT:
			self.BookingFrameGUI=Frame(self.master,bg='lightgrey')
			# allowing the widget to take the full space of the root window
			self.BookingFrameGUI.pack(fill=BOTH, expand=1)
			# changing the title of our master widget
			self.master.title("LTC-BoxOffice")
		elif mode == REINIT:
			self.BookingFrameGUI.destroy()
			self.BookingFrameGUI=None
			if self.AAAed is not None:
				self.AAAed=None
			self.BookingFrameGUI=Frame(self.master,bg='lightgrey')
			# allowing the widget to take the full space of the root window
			self.BookingFrameGUI.pack(fill=BOTH, expand=1)
			# changing the title of our master widget
			self.master.title("LTC-BoxOffice")



		## CREATE THE FRAME FOR EVENT INFO DISPLAY
		##

		self.FrameEventInfos=Frame(self.BookingFrameGUI,bg='cornsilk2')
		self.FrameEventInfos.grid(row=1,column=1,padx=(5,5),pady=(5,5))

		self.LblEvent_Frametitle=Label(self.FrameEventInfos,bg='cornsilk3',height=1,text="Evento aperto",
								width=40,font=HUGE_FONT,anchor=CENTER)
		self.LblEvent_Frametitle.grid(row=1,column=1,padx=(5,5),pady=(5,5),columnspan=3)

		self.LblEvent_company=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Compagnia",
								width=45,font=LARGE_FONT,anchor=NW)
		self.LblEvent_company.grid(row=2,column=1,padx=(5,5),pady=(5,5),columnspan=3)

		self.LblEvent_title=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Titolo dello spettacolo",
								width=45,font=LARGE_FONT,anchor=NW)
		self.LblEvent_title.grid(row=3,column=1,padx=(5,5),pady=(5,5),columnspan=3)

		self.LblEvent_date=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Data",
								width=30,font=LARGE_FONT,anchor=NW)
		self.LblEvent_date.grid(row=4,column=1,padx=(5,5),pady=(5,5),columnspan=2)

		self.LblEvent_time=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Time",
								width=15,font=LARGE_FONT,anchor=NW)
		self.LblEvent_time.grid(row=4,column=3,padx=(5,5),pady=(5,5),columnspan=1)

		self.LblEvent_price=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Prezzo Ingressi €",
								width=15,font=LARGE_FONT,anchor=NW)
		self.LblEvent_price.grid(row=5,column=1,padx=(5,5),pady=(5,5),columnspan=1)

		self.LblEvent_price_full=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Intero =",
								width=15,font=LARGE_FONT,anchor=NW)
		self.LblEvent_price_full.grid(row=5,column=2,padx=(5,5),pady=(5,5),columnspan=1)

		self.LblEvent_price_reduced=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Ridotto =",
								width=15,font=LARGE_FONT,anchor=NW)
		self.LblEvent_price_reduced.grid(row=5,column=3,padx=(5,5),pady=(5,5),columnspan=1)

		self.LblEvent_season=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Stagione Teatrale ",
								width=30,font=LARGE_FONT,anchor=NW)
		self.LblEvent_season.grid(row=6,column=1,padx=(5,5),pady=(5,5),columnspan=2)

		self.LblEvent_season_code=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Codice stagione ",
								width=15,font=LARGE_FONT,anchor=NW)
		self.LblEvent_season_code.grid(row=6,column=3,padx=(5,5),pady=(5,5),columnspan=1)

		self.LblEvent_show_code=Label(self.FrameEventInfos,bg='cornsilk2',height=1,text="Codice spettacolo ",
								width=45,font=HUGE_FONT,anchor=NW)
		self.LblEvent_show_code.grid(row=7,column=1,padx=(5,5),pady=(5,5),columnspan=3,sticky=S)




		"""
		# 		self.AAAed['show']['id']=data[0]
		# 		self.AAAed['show']['company']=data[1]
		# 		self.AAAed['show']['title']=data[2]
		# 		self.AAAed['show']['text']=data[3]
		# 		self.AAAed['show']['season_year_id']=data[4]
		# 		self.AAAed['show']['debut_date']=data[5]
		# 		self.AAAed['show']['director']=data[6]
		# 		self.AAAed['show']['cast']=data[7]
		# 		self.AAAed['show']['shw_code']=data[8]



		# 		self.AAAed['event']['event_date']=data[2]
		# 		self.AAAed['event']['booking_status']=data[3]
		# 		self.AAAed['event']['booking_user']=data[4]
		# 		self.AAAed['event']['booking_price']=data[5]
		# 		self.AAAed['event']['booking_datetime']=data[6]
		# 		self.AAAed['event']['price_full']=data[7]
		# 		self.AAAed['event']['price_reduced']=data[8]
		# 		self.AAAed['event']['author_id']=data[9]
		# 		self.AAAed['event']['show_id']=data[10]
		# 		self.AAAed['event']['change']=data[11]
				#Comando per richiamare una prenotazione con il codice

		# 		self.booking_btn = Button(self.FrameEventInfos,font=NORM_FONT,text='Prenotazione',
		# 												width=15,activebackground='white',activeforeground='red',
		# 												command= self.booking_code_window)
		# 		self.booking_btn.grid(row=1,column=1,padx=(5,5),pady=(5,5))
		"""

		## CREATE THE FRAME FOR Selection Actions
		##

		self.FrameSelectionActions=Frame(self.BookingFrameGUI,bg='lightgreen')
		self.FrameSelectionActions.grid(row=1,column=2,padx=(5,5),pady=(5,5))
		self.FrameSelectionActions.grid(columnspan=1)

		# Finestra con i posti selezionati
		self.SelectionBufferText= Text(self.FrameSelectionActions,height = 16,width=30)
		self.SelectionBufferText.grid(row=1,column=2,padx=(5,5),pady=(5,5),rowspan=4)
		self.SelectionBufferText.insert(END,"Posti selezionati")

		#Comando per vendere i posti selezionati
		self.sell_selection_btn = Button(self.FrameSelectionActions,font=NORM_FONT,text='Vendita',
												width=10,activebackground='white',activeforeground='red',
												command= self.sell_selections)
		self.sell_selection_btn.grid(row=1,column=1,padx=(5,5),pady=(5,5))
		#Comando per prenotare  i posti selezionati
		self.book_selection_btn = Button(self.FrameSelectionActions,font=NORM_FONT,text='Prenota',
												width=10,activebackground='white',activeforeground='red',
												command= self.book_selections)
		self.book_selection_btn.grid(row=2,column=1,padx=(5,5),pady=(5,5))
		#Comando per altre azioni sui posti selezionati
		self.spare_selection_btn = Button(self.FrameSelectionActions,font=NORM_FONT,text='Spare',
												width=10,activebackground='white',activeforeground='red',
												command= self.spare_selections)
		self.spare_selection_btn.grid(row=3,column=1,padx=(5,5),pady=(5,5))

		# Pulsante per reset delle selezioni dei posti

		self.SelectionReset=Button(self.FrameSelectionActions,font=NORM_FONT,text='{}'.format("RESET SEL"),
												width=10,activebackground='red',activeforeground='yellow',
												command= self.resetSelection)
		self.SelectionReset.grid(row=4,column=1,columnspan=1,rowspan=1)

		## CREATE THE FRAME FOR SEATS GRID
		##

		self.FrameSeatGrid=Frame(self.BookingFrameGUI,bg='white')
		self.FrameSeatGrid.grid(row=2,column=1,padx=(5,5),pady=(5,5))
		self.FrameSeatGrid.grid(columnspan=2)
		# creating the grid of button for seats

		self.btn = [0 for x in range(263)]  # @UnusedVariable
		self.seat_name=['' for x in range(263)]  # @UnusedVariable
		btn_seat_index = 0
		for y_num,row in enumerate(rows_name):

			for x_num,seat in enumerate(seats[row]):
				if seat:
					if x_num==0:
						padxl=25
						padxr=2
					elif x_num==9 or x_num==19:
						padxl=2
						padxr=25
					else:
						padxl=2
						padxr=2

					if row=='A':
						padyt=25
						padyb=2
					elif row=='H' or row=='Q':
						padyt=2
						padyb=25
					else:
						padyt=2
						padyb=2

					self.btn[btn_seat_index]=Button(self.FrameSeatGrid,font=SMALL_FONT,text='{}{}'.format(row,str(x_num+1)),state=DISABLED,
												width=2,activebackground='white',activeforeground='red', bg='lightgrey',relief=RAISED,
												command= lambda idx=btn_seat_index : self.toggle_status(idx,mode=SELECT))
					self.btn[btn_seat_index].grid(row=y_num,column=x_num,padx=(padxl,padxr),pady=(padyt,padyb))
# 					self.btn[btn_seat_index].place(x=seat_posX[x_num],y=y_row)
					self.seat_name[btn_seat_index]='{}{}'.format(row,str(x_num+1))
					btn_seat_index+=1




		## CREATE THE FRAME FOR Booking Controls
		##

		self.FrameBooking=Frame(self.BookingFrameGUI,bg='lightgreen')
		self.FrameBooking.grid(row=1,column=3,padx=(5,5),pady=(5,5))
		self.FrameBooking.grid(columnspan=1,rowspan=3,sticky=N+E)

		# Finestra con le prenotazioni attive
		self.BookingTitle= Label(self.FrameBooking,height = 1,width=30,font=LARGE_FONT,text="Prenotazioni evento")
		self.BookingTitle.grid(row=1,column=1,padx=(0,0),pady=(0,0),columnspan=4,sticky=N)
		self.BookingBarCodebtn=Button(self.FrameBooking,font=NORM_FONT,text='Lettura Barcode',state=NORMAL,
					width=15,activebackground='white',activeforeground='red', bg='lightgrey',relief=RAISED,
					command= self.booking_code_window)
		self.BookingBarCodebtn.grid(row=1,column=6,padx=2,pady=2,rowspan=2)

		## CREATE THE FRAME FOR TOTALIZERS ###################################
		##

		self.FrameTotalizers=Frame(self.BookingFrameGUI,bg='lightgreen')
		self.FrameTotalizers.grid(row=3,column=1,padx=(5,5),pady=(5,0))
		self.FrameTotalizers.grid(columnspan=2,rowspan=1,sticky=N+E)

		#  Tabella Totalizzatori
		self.TotalizersTitle= Label(self.FrameTotalizers,height = 1,width=30,font=LARGE_FONT,text="Totalizzatori")
		self.TotalizersTitle.grid(row=1,column=2,padx=(0,0),pady=(0,0),columnspan=5,sticky=E+N)

		TotalizersTv= Treeview(self.FrameTotalizers)
		TotalizersTv['columns'] = ('full_price', 'reduced_price', 'free_price','revenue')
		TotalizersTv.heading("#0", text='Frazione', anchor='w')
		TotalizersTv.column("#0", anchor="w")
		TotalizersTv.heading('full_price', text='Interi')
		TotalizersTv.column('full_price', anchor='center', width=100)
		TotalizersTv.heading('reduced_price', text='Ridotti')
		TotalizersTv.column('reduced_price', anchor='center', width=100)
		TotalizersTv.heading('free_price', text='Gratuiti')
		TotalizersTv.column('free_price', anchor='center', width=100)
		TotalizersTv.heading('revenue', text='Incasso')
		TotalizersTv.column('revenue', anchor='center', width=100)
		TotalizersTv.grid(row=1,column=1,sticky = (N,S,W,E))
		self.Totalizers = TotalizersTv
		self.grid_rowconfigure(0, weight = 1)
		self.grid_columnconfigure(0, weight = 1)
		self.TotalizersOpening=self.Totalizers.insert('', 'end', text="Apertura", values=(0,0,0,Decimal('0.00')))
		self.TotalizersSession=self.Totalizers.insert('', 'end', text="Sessione cassa", values=(0,0,0,Decimal('0.00')))
		self.TotalizersTotals=self.Totalizers.insert('', 'end', text="TOTALE", values=(0,0,0,Decimal('0.00')))


		## CREATING A MENU FOR ROOT WINDOW ####################################
		## FILE AND EDIT
		self.menubar = Menu(self.master)
		self.master.config(menu=self.menubar)

		# create the file object)
		self.file = Menu(self.menubar)

		# adds a command to the menu option, calling it exit, and the
		self.file.add_command(label="Apri_evento", state=NORMAL, command=self.OpenEvent)
		self.file.add_command(label="Chiudi_evento", state= DISABLED,  command=self.CloseEvent)
		
		self.file.add_separator()


		# adds a command to the menu option, calling it exit, and the
		# command it runs on event is client_exit
		self.file.add_command(label="Uscita", command=self.client_exit)


		#added "file" to our menu
		self.menubar.add_cascade(label="File", menu=self.file)


		# create the edit object)
		self.edit = Menu(self.menubar)

		# adds a command to the menu option, calling it exit, and the
		# command it runs on event is client_exit
		self.edit.add_command(label="Show Img", command=self.showImg)
		#edit.add_command(label="Show Text", command=self.showText)

		#added "file" to our menu
		self.menubar.add_cascade(label="Edit", menu=self.edit)
		if mode==INIT:
			if os.path.exists("session_dumpdata.dat"):
				message= """ Ho trovato un file con dati di una sessione precedente non chiusa correttamente.
				Vuoi caricare i dati della sessione salvata sul disco?
				"""
				if messagebox.askyesno("Trovato un file dati di sessione non chiusa", message):
	
					self.session_open = True
					try:
						with open("session_dumpdata.dat", "rb") as f:
							self.AAAed=pickle.load(f)
					except (pickle.PickleError) as e:
						messagebox.showerror("Errore nella lettura della sessione", "Il programma ha trovato questo errore:/n {}/n Non è consentito il proseguimento./nIl programma verrà terminato. Premi OK per terminare".format(e))
						exit(2)
					## Main refresh of application data for event opening
					self.RefreshSeats(mode='full')
					self.RefreshEventInfo(mode='full')
					self.RefreshBooking(mode='full')
					self.RefreshTotalizers(mode=OPENING)
					self.file.entryconfig("Chiudi", state=NORMAL)
				
				
		## Open the MySQL connection using the tunnel
		# tunneling must be operative before and managed outside this code
		try:
			try:
				self.mysql= MySQLdb.connect("127.0.0.1","ltc","ltc","ltcsite")
				self.mysqlcursor=self.mysql.cursor()
				self.mysqlcursor.execute("SELECT VERSION()")
			except (MySQLdb.Error,MySQLdb.Warning) as e:  # @UndefinedVariable
				print(e)
				self.mysql_active=False
				exit(1)

			self.mysql_active=True
			data,=self.mysqlcursor.fetchone()
			print("Version of mysql opened ={}".format(data))

		finally:
			if self.mysql_active:
				print("OK ---> Connection to MySqlDb establish!")
			else:
				print("KO ---> Connection to MySqlDb cannot be established!")

		sql_cmd="USE ltcsite;"
		self.mysqlcursor.execute(sql_cmd)



	def showImg(self):
		load = Image.open("chat.png")
		render = ImageTk.PhotoImage(load)

		# labels can be text or images
		img = Label(self, image=render)
		img.image = render
		img.place(x=0, y=0)

	def sell_selections(self):
		print("Vendo posti selezionati, operazione vendita numero {}".format(self.TotalSellsOperations+1))
		if len(self.SelectionBuffer):
			self.ActionOnSelection(mode=SELL)
		else:
			messagebox.showerror("NESSUN POSTO SELEZIONATO","Hai richiesto l'azione di VENDITA \nche prevede di aver selezionato dei posti su cui affettuarla.\n")
	def book_selections(self):
		print("Prenoto posti selezionati")
		if len(self.SelectionBuffer):
			self.ActionOnSelection(mode=BOOK)
		else:
			messagebox.showerror("NESSUN POSTO SELEZIONATO","Hai richiesto l'azione di PRENOTAZIONE \nche prevede di aver selezionato dei posti su cui affettuarla.\n")


	def spare_selections(self):
		print("Do something posti selezionati")


	def ActionOnSelection(self,mode):
		def choose(evt):
			w=evt.widget
			idx=self.ASPriceLstb.index(w)
			print(w," con indice %d"%idx)
			try:
				self.index = int(w.curselection()[0])
				self.value = w.get(self.index)
			except IndexError:
				print("Index error")
			finally:
				self.ASPriceLbl[idx].config(text=self.prices[self.index])
				print("Scelta : Prezzo = {} all'indice {}".format(self.value,self.index))
				pass

			ActSelUpdateTotalSell()
# 			self.TotalPrice=Decimal('0.00')
# 			for wl in self.ASPriceLbl:
# 				self.TotalPrice+=Decimal(wl.cget('text'))
# 			self.ASTotalAmountLbl.config(text=self.TotalPrice)
# 
# 
# 			self.TotalTransactionFullPrice= 0
# 			self.TotalTransactionReducedPrice=0
# 			self.TotalTransactionFreePrice=0
# 			for w in self.ASPriceLstb:
# 				if w.curselection()[0]== FULL_PRICE:
# 					self.TotalTransactionFullPrice+=1
# 				elif w.curselection()[0]== REDUCED_PRICE:
# 					self.TotalTransactionReducedPrice+=1
# 				elif w.curselection()[0]== FREE_PRICE:
# 					self.TotalTransactionFreePrice+=1
# 			self.ASTotalFullPriceLbl.config(text=self.TotalTransactionFullPrice)
# 			self.ASTotalReducedPriceLbl.config(text=self.TotalTransactionReducedPrice)
# 			self.ASTotalFreePriceLbl.config(text=self.TotalTransactionFreePrice)
		
		def ActSelUpdateTotalSell():
			self.TotalPrice=Decimal('0.00')
			for idx,wl in enumerate(self.ASPriceLbl):
				if self.ASPSeatEnabledBool[idx]:
					self.TotalPrice+=Decimal(wl.cget('text'))
			self.ASTotalAmountLbl.config(text=self.TotalPrice)


			self.TotalTransactionFullPrice= 0
			self.TotalTransactionReducedPrice=0
			self.TotalTransactionFreePrice=0
			for idx,w in enumerate(self.ASPriceLstb):
				if self.ASPSeatEnabledBool:
						
					if w.curselection()[0]== FULL_PRICE:
						self.TotalTransactionFullPrice+=1
					elif w.curselection()[0]== REDUCED_PRICE:
						self.TotalTransactionReducedPrice+=1
					elif w.curselection()[0]== FREE_PRICE:
						self.TotalTransactionFreePrice+=1
			self.ASTotalFullPriceLbl.config(text=self.TotalTransactionFullPrice)
			self.ASTotalReducedPriceLbl.config(text=self.TotalTransactionReducedPrice)
			self.ASTotalFreePriceLbl.config(text=self.TotalTransactionFreePrice)
		
		def ActSelTLSellABook():
			if True in self.ASPSeatEnabledBool:
				from builtins import str
				users_tmp= self.AAAed['event']['booking_user'].split(',')
	# 			price_tmp= self.AAAed['event']['booking_price'].split(',')
				datetime_tmp= self.AAAed['event']['booking_datetime'].split(',')
				#Initialize the SEATS PRINT STRING FOR PRINTER
				pr_str_hdr="LABORATORIO TEATRALE DI CAMBIANO \nAssociazione Teatrale\nPIAZZA INNOVAZONE snc - 10020 CAMBIANO (TO)\nPI=CF 09762270016\n"
				pr_str_hdr += "Data e ora: {}\n\n".format(time.strftime('%d-%m-%Y %H:%M:%S'))
				pr_str_hdr += "Spettacolo: '{}'\n".format(self.AAAed['show']['title'])
				pr_str_hdr += "Riscontro vendita numero {}\n".format(self.TotalSellsOperations+1)
				
				this_ticket_total= Decimal('0.00')
				this_ticket_counters=[0, 0, 0]
				pr_str_seats = "Posto     Ingresso  Prezzo    \n"
				pr_str_hdr+=   "-----     --------  ------    \n"
				string_for_booking_update=''
				for idx,seat in enumerate(self.SelectionBuffer):
					if self.ASPSeatEnabledBool[idx]:
	
						string_for_booking_update+='1,'
						self.AAAed['seat_status'][seat]=SOLD
						users_tmp[seat]= '2'
						self.AAAed['seat_prices'][seat]= str(self.ASPriceLstb[idx].curselection()[0])
						datetime_tmp[seat] = time.strftime('%Y-%m-%d %H:%M:%S')
						if int(self.AAAed['seat_prices'][seat])==FULL_PRICE:
							this_price=self.AAAed['event']['price_full']
						elif int(self.AAAed['seat_prices'][seat])==REDUCED_PRICE:
							this_price=self.AAAed['event']['price_reduced']
						else:
							this_price=Decimal('0.00')
						this_ticket_counters[int(self.AAAed['seat_prices'][seat])] +=1
						this_ticket_total +=this_price
						pr_str_seats +="\n{:<10}{:<10}{:<10}\n".format(self.seat_name[seat],TICKET[int(self.AAAed['seat_prices'][seat])], this_price )
					else:
						string_for_booking_update+='{},'.format(self.ListSoldStatus[idx])
				string_for_booking_update=string_for_booking_update.rstrip(',')					
				pr_str_seats +="------------------------------- \n"
				
				pr_str_totals ="\n**** TOTALI *************\n"
				pr_str_totals += "****   Interi:_____{0:02}\n".format(this_ticket_counters[FULL_PRICE])
				pr_str_totals += "****  Ridotti:_____{0:02}\n".format(this_ticket_counters[REDUCED_PRICE])
				pr_str_totals += "**** Gratuiti:_____{0:02}\n".format(this_ticket_counters[FREE_PRICE])
				pr_str_totals += "\n"
				pr_str_totals += "**** TOTALE EURO___{}\n".format(this_ticket_total)
				

				transaction_data={}
				transaction_data['seats_sold']="{},{},{}".format(this_ticket_counters[FREE_PRICE],this_ticket_counters[REDUCED_PRICE],this_ticket_counters[FULL_PRICE])
				transaction_data['amount']=this_ticket_total

	
				self.AAAed['event']['booking_status']=','.join(self.AAAed['seat_status'])
				self.AAAed['event']['booking_user']=','.join(users_tmp)
				self.AAAed['event']['booking_price']=','.join(self.AAAed['seat_prices'])
				self.AAAed['event']['booking_datetime']=','.join(datetime_tmp)
	
				self.escprinter.image('logo_bn.png')
				self.escprinter.set(align='center', font='a',  width=1, height=1)
				self.escprinter.text(pr_str_hdr)
				self.escprinter.set(align='right', font='b',  width=2, height=2)
				self.escprinter.text(pr_str_seats)
				self.escprinter.set(align='right', font='a',  width=1, height=1)
				self.escprinter.text(pr_str_totals)
				self.escprinter.set(align='center', font='b',  width=3, height=3)
				self.escprinter.text("Buona visione!")
				self.escprinter.cut(mode=u'FULL')
				
	
				del users_tmp,datetime_tmp, this_price
	
	
				sql_cmd = """UPDATE `booking_event`
				SET `booking_status`='{}',
				`booking_user`='{}',
				`booking_price`='{}',`booking_datetime`='{}'
				WHERE `booking_event`.`id` = {};""".format(self.AAAed['event']['booking_status'],self.AAAed['event']['booking_user'],self.AAAed['event']['booking_price'],self.AAAed['event']['booking_datetime'],self.AAAed['event']['id'])
	
				self.EventDataChanged=True
				try:
					self.mysqlcursor.execute(sql_cmd)
					self.mysql.commit()
					self.EventDataChanged=False
				except:
					self.mysql.rollback()
	
				try:
					if self.SellingBookingCode:
						sql_cmd = """UPDATE `booking_booking`
						SET `book_sold`= '{}'
						WHERE `booking_booking`.`id` = {};""".format(string_for_booking_update ,self.AAAed['booking'][self.SellingBookingCode][0])
	
						print(sql_cmd)
						self.EventDataChanged=True
						try:
							self.mysqlcursor.execute(sql_cmd)
							self.mysql.commit()
							self.EventDataChanged=False
						except:
							self.mysql.rollback()
						finally:
							try:
								sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.AAAed['event']['id']))
								result=self.mysqlcursor.execute(sql_cmd)
								if result < 1:
									self.AAAed['booking']['quantity']=result
								else:
									self.AAAed['booking']['quantity']=result
									for idx in range(result):  # @UnusedVariable
										data=self.mysqlcursor.fetchone()
										self.AAAed['booking'][str(data[0]).zfill(6)]=data
										print(self.AAAed['booking'][str(data[0]).zfill(6)])
	
									self.RefreshBooking(mode='full')
							except:
								pass
							print("Mysql executed")
				except:
					pass
	
				# Update the Totalizer for current session and related Totals
				self.TotalSoldFullPrice+=self.TotalTransactionFullPrice
				self.TotalSoldReducedPrice+=self.TotalTransactionReducedPrice
				self.TotalFreePrice+=self.TotalTransactionFreePrice
	
				self.AAAed['Totals']['session_price']=Counter({str(FULL_PRICE):self.TotalSoldFullPrice,
																str(REDUCED_PRICE):self.TotalSoldReducedPrice,
																str(FREE_PRICE):self.TotalFreePrice})
				self.AAAed['Totals']['session_revenue']+=self.TotalPrice
	
				self.AAAed['Totals']['totals_price'][str(FULL_PRICE)]=self.AAAed['Totals']['open_price'][str(FULL_PRICE)]+self.TotalSoldFullPrice
				self.AAAed['Totals']['totals_price'][str(REDUCED_PRICE)]=self.AAAed['Totals']['open_price'][str(REDUCED_PRICE)]+self.TotalSoldReducedPrice
				self.AAAed['Totals']['totals_price'][str(FREE_PRICE)]=self.AAAed['Totals']['open_price'][str(FREE_PRICE)]+self.TotalFreePrice
	
				self.AAAed['Totals']['totals_revenue']=self.AAAed['Totals']['open_revenue']+self.AAAed['Totals']['session_revenue']
	
				self.TotalSellsOperations+=1
	
				self.RecordTransaction(transaction_data)
	
				self.RefreshSeats(mode='full', idx=None)
				self.SelectionBuffer=[]
				self.UpdateSelectionBufferText()
				self.RefreshTotalizers(mode=SESSION)
	
				## Finally exit from TopLevel and Destroy it
				ActSelTLExit()
			else:
				print("nessun posto vendibile")
				message= "Stai tentando di effettuare una vendita da una prenotazione ma nessun posto è selezionato. Rivedi la selezione dei posti."
				messagebox.showerror("Vendita vuota!!!", message)
				
	
		def ActSelTLSell():
			from builtins import str
			users_tmp= self.AAAed['event']['booking_user'].split(',')
# 			price_tmp= self.AAAed['event']['booking_price'].split(',')
			datetime_tmp= self.AAAed['event']['booking_datetime'].split(',')
			#Initialize the SEATS PRINT STRING FOR PRINTER
			pr_str_hdr="LABORATORIO TEATRALE DI CAMBIANO \nAssociazione Teatrale\nPIAZZA INNOVAZONE snc - 10020 CAMBIANO (TO)\nPI=CF 09762270016\n"
			pr_str_hdr += "Data e ora: {}\n\n".format(time.strftime('%d-%m-%Y %H:%M:%S'))
			pr_str_hdr += "Spettacolo: '{}'\n".format(self.AAAed['show']['title'])
			pr_str_hdr += "Riscontro vendita numero {}\n".format(self.TotalSellsOperations+1)
			
			this_ticket_total= Decimal('0.00')
			this_ticket_counters=[0, 0, 0]
			pr_str_seats = "Posto     Ingresso  Prezzo    \n"
			pr_str_hdr+=   "-----     --------  ------    \n"
			
			for idx,seat in enumerate(self.SelectionBuffer):
				self.AAAed['seat_status'][seat]=SOLD
				users_tmp[seat]= '2'
				self.AAAed['seat_prices'][seat]= str(self.ASPriceLstb[idx].curselection()[0])
				datetime_tmp[seat] = time.strftime('%Y-%m-%d %H:%M:%S')
				if int(self.AAAed['seat_prices'][seat])==FULL_PRICE:
					this_price=self.AAAed['event']['price_full']
				elif int(self.AAAed['seat_prices'][seat])==REDUCED_PRICE:
					this_price=self.AAAed['event']['price_reduced']
				else:
					this_price=Decimal('0.00')
				this_ticket_counters[int(self.AAAed['seat_prices'][seat])] +=1
				this_ticket_total +=this_price
				pr_str_seats +="\n{:<10}{:<10}{:<10}\n".format(self.seat_name[seat],TICKET[int(self.AAAed['seat_prices'][seat])], this_price )
			pr_str_seats +="------------------------------- \n"
			
			pr_str_totals ="\n**** TOTALI *************\n"
			pr_str_totals += "****   Interi:_____{0:02}\n".format(this_ticket_counters[FULL_PRICE])
			pr_str_totals += "****  Ridotti:_____{0:02}\n".format(this_ticket_counters[REDUCED_PRICE])
			pr_str_totals += "**** Gratuiti:_____{0:02}\n".format(this_ticket_counters[FREE_PRICE])
			pr_str_totals += "\n"
			pr_str_totals += "**** TOTALE EURO___{}\n".format(this_ticket_total)
			
			transaction_data={}
			transaction_data['seats_sold']="{},{},{}".format(this_ticket_counters[FREE_PRICE],this_ticket_counters[REDUCED_PRICE],this_ticket_counters[FULL_PRICE])
			transaction_data['amount']=this_ticket_total

			self.AAAed['event']['booking_status']=','.join(self.AAAed['seat_status'])
			self.AAAed['event']['booking_user']=','.join(users_tmp)
			self.AAAed['event']['booking_price']=','.join(self.AAAed['seat_prices'])
			self.AAAed['event']['booking_datetime']=','.join(datetime_tmp)

			self.escprinter.image('logo_bn.png')
			self.escprinter.set(align='center', font='a',  width=1, height=1)
			self.escprinter.text(pr_str_hdr)
			self.escprinter.set(align='right', font='b',  width=2, height=2)
			self.escprinter.text(pr_str_seats)
			self.escprinter.set(align='right', font='a',  width=1, height=1)
			self.escprinter.text(pr_str_totals)
			self.escprinter.set(align='center', font='b',  width=3, height=3)
			self.escprinter.text("Buona visione!")
			self.escprinter.cut(mode=u'FULL')
			

			del users_tmp,datetime_tmp, this_price


			sql_cmd = """UPDATE `booking_event`
			SET `booking_status`='{}',
			`booking_user`='{}',
			`booking_price`='{}',`booking_datetime`='{}'
			WHERE `booking_event`.`id` = {};""".format(self.AAAed['event']['booking_status'],self.AAAed['event']['booking_user'],self.AAAed['event']['booking_price'],self.AAAed['event']['booking_datetime'],self.AAAed['event']['id'])

			self.EventDataChanged=True
			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
				self.EventDataChanged=False
			except:
				self.mysql.rollback()

## 	BUG FIXED 04/02/2018 : operated Update on booling_booking when a normal sell happened
#			try: 
# 				if self.SellingBookingCode:
# 					sql_cmd = """UPDATE `booking_booking`
# 					SET `book_sold`= '1'
# 					WHERE `booking_booking`.`id` = {};""".format(self.AAAed['booking'][self.SellingBookingCode][0])
# 
# 					print(sql_cmd)
# 					self.EventDataChanged=True
# 					try:
# 						self.mysqlcursor.execute(sql_cmd)
# 						self.mysql.commit()
# 						self.EventDataChanged=False
# 					except:
# 						self.mysql.rollback()
# 					finally:
# 						try:
# 							sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.AAAed['event']['id']))
# 							result=self.mysqlcursor.execute(sql_cmd)
# 							if result < 1:
# 								self.AAAed['booking']['quantity']=result
# 							else:
# 								self.AAAed['booking']['quantity']=result
# 								for idx in range(result):  # @UnusedVariable
# 									data=self.mysqlcursor.fetchone()
# 									self.AAAed['booking'][str(data[0]).zfill(6)]=data
# 									print(self.AAAed['booking'][str(data[0]).zfill(6)])
# 
# 								self.RefreshBooking(mode='full')
# 						except:
# 							pass
# 						print("Mysql executed")

			# Update the Totalizer for current session and related Totals
			self.TotalSoldFullPrice+=self.TotalTransactionFullPrice
			self.TotalSoldReducedPrice+=self.TotalTransactionReducedPrice
			self.TotalFreePrice+=self.TotalTransactionFreePrice

			self.AAAed['Totals']['session_price']=Counter({str(FULL_PRICE):self.TotalSoldFullPrice,
															str(REDUCED_PRICE):self.TotalSoldReducedPrice,
															str(FREE_PRICE):self.TotalFreePrice})
			self.AAAed['Totals']['session_revenue']+=self.TotalPrice

			self.AAAed['Totals']['totals_price'][str(FULL_PRICE)]=self.AAAed['Totals']['open_price'][str(FULL_PRICE)]+self.TotalSoldFullPrice
			self.AAAed['Totals']['totals_price'][str(REDUCED_PRICE)]=self.AAAed['Totals']['open_price'][str(REDUCED_PRICE)]+self.TotalSoldReducedPrice
			self.AAAed['Totals']['totals_price'][str(FREE_PRICE)]=self.AAAed['Totals']['open_price'][str(FREE_PRICE)]+self.TotalFreePrice

			self.AAAed['Totals']['totals_revenue']=self.AAAed['Totals']['open_revenue']+self.AAAed['Totals']['session_revenue']

			self.TotalSellsOperations+=1

			self.RecordTransaction(transaction_data)

			self.RefreshSeats(mode='full', idx=None)
			self.SelectionBuffer=[]
			self.UpdateSelectionBufferText()
			self.RefreshTotalizers(mode=SESSION)

			## Finally exit from TopLevel and Destroy it
			ActSelTLExit()



		def ActSelTLBook():
			##check whether the Surname at least has been provided for recording
			## the Booking in case no Surname in Entry will go back
			cstr_surname = self.ASSurnameEnt.get()
			if len(cstr_surname)< 2:
				if len(cstr_surname)==0:
					message= "Non hai introdotto nessun Cognome di riferimento per la prenotazione. Il Cognome va inserito obbligatoriamente."
				else:
					message= "Il valore '{}' per il Cognome di riferimento per la prenotazione non e' valido. Almeno le iniziali Cognome Nome.".format(cstr_surname)
				messagebox.showerror("Indicazioni per la prenotazione insufficienti", message)
				ActSelTLExit()
				return


			## booking_event data change for booking
			"""
				self.AAAed['event']['booking_user']=data[4]
				self.AAAed['event']['booking_price']=data[5]
				self.AAAed['event']['booking_datetime']=data[6]
			"""
			users_tmp= self.AAAed['event']['booking_user'].split(',')
# 			price_tmp= self.AAAed['seat_prices']
			datetime_tmp= self.AAAed['event']['booking_datetime'].split(',')
			for idx,seat in enumerate(self.SelectionBuffer):
				self.AAAed['seat_status'][seat]=BOOKED
				users_tmp[seat]= '2'
				self.AAAed['seat_prices'][seat]= str(self.ASPriceLstb[idx].curselection()[0])
				datetime_tmp[seat] = time.strftime('%Y-%m-%d %H:%M:%S')

			self.AAAed['event']['booking_status']=','.join(self.AAAed['seat_status'])
			self.AAAed['event']['booking_user']=','.join(users_tmp)
			self.AAAed['event']['booking_price']=','.join(self.AAAed['seat_prices'])
			self.AAAed['event']['booking_datetime']=','.join(datetime_tmp)

			del users_tmp,datetime_tmp

			sql_cmd = """UPDATE `booking_event`
			SET `booking_status`='{}',
			`booking_user`='{}',
			`booking_price`='{}',`booking_datetime`='{}'
			WHERE `booking_event`.`id` = {};""".format(self.AAAed['event']['booking_status'],self.AAAed['event']['booking_user'],self.AAAed['event']['booking_price'],self.AAAed['event']['booking_datetime'],self.AAAed['event']['id'])


			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
			except:
				self.mysql.rollback()


			## booking_booking data get for insert new record

			self.AAAed['booking']['quantity']+=1
			created_date_tmp = time.strftime('%Y-%m-%d %H:%M:%S')
			seats_booked_tmp = ''
			book_sold= ''
			for idx,seat in enumerate(self.SelectionBuffer):
				seats_booked_tmp+='{}${},'.format(self.seat_name[seat],self.AAAed['seat_prices'][seat])
				book_sold +='0,'
			book_sold= book_sold.rstrip(',')
			seats_booked_tmp=seats_booked_tmp.rstrip(',')
			

			cstr_name = self.ASNameEnt.get()
			cstr_email = self.ASEmailEnt.get()
			cstr_phone = self.ASPhoneEnt.get()
			cstr_note = self.ASNoteEnt.get()
			event_tmp = self.AAAed['event']['id']

			self.EventDataChanged=True

			#INSERT INTO `booking_booking`(`id`, `created_date`, `seats_booked`, `customer_name`, `customer_surname`, `customer_email`, `event_id`, `user_id_id`, `customer_phone`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7],[value-8],[value-9])
			sql_cmd = """
			INSERT INTO `booking_booking`
			( `created_date`, `seats_booked`, `customer_name`, `customer_surname`, `customer_email`, `event_id`, `user_id_id`, `customer_phone`,`book_sold`,`customer_notes`)
			VALUES ('{}','{}','{}','{}','{}',{},{},'{}','{}','{}')
			;
			""".format(created_date_tmp,seats_booked_tmp,cstr_name,cstr_surname,cstr_email,event_tmp,2,cstr_phone,book_sold,cstr_note)
			print(sql_cmd)
			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
			except:
				self.mysql.rollback()
			finally:
				try:
					sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.AAAed['event']['id']))
					result=self.mysqlcursor.execute(sql_cmd)
					if result < 1:
						self.AAAed['booking']['quantity']=result
					else:
						self.AAAed['booking']['quantity']=result
						for idx in range(result):  # @UnusedVariable
							data=self.mysqlcursor.fetchone()
							self.AAAed['booking'][str(data[0]).zfill(6)]=data
							print(self.AAAed['booking'][str(data[0]).zfill(6)])
						self.EventDataChanged=False
				except:
					pass
				print("Mysql executed")

			self.RefreshSeats(mode='full', idx=None)
			self.RefreshBooking(mode='full')
			self.SelectionBuffer=[]
			self.UpdateSelectionBufferText()

			
			## Here we are 20171027 1904

			## Finally exit from TopLevel and Destroy it
			ActSelTLExit()



		def ActSelTLExit():
			if self.EventDataChanged:
				print('I dati della sessione non sono stati aggiornati sul database!!!')
				pass
			if self.SelectionReset['state']==DISABLED:
				self.SelectionReset.config(state=NORMAL)
			## Refresh the data dump for sessio backup
			try:
				with open("session_dumpdata.dat", "wb") as f:
					pickle.dump(self.AAAed,f, protocol=pickle.HIGHEST_PROTOCOL)
			except (pickle.PickleError) as e:
				messagebox.showerror("Errore nel salvataggio della sessione", "Il programma ha trovato questo errore:/n {}/n Non è consentito il proseguimento./nIl programma verrà terminato. Premi OK per terminare".format(e))
				exit(1)
			self.resetSelection()
			self.ActSelTL.destroy()

		## DECLARE , INSTANTIATE AND POPULATE THE TOP LEVEL FRAME FOR SELL, BOOK
		## or other actions on the selected seats
		
		def ActSelToggleBbookseat(position,mode):
			print("Command on button toggle seat booked got for position {} and mode {}".format(position, mode))
			if mode== TOGGLE:
				if self.ASPSeatEnabledBool[position]:
					self.ASPSeatEnabledBool[position]=False
					self.ASSeatBtn[position].config(bg='indian red',fg='ivory',relief=FLAT)
					
				else:
					self.ASPSeatEnabledBool[position]=True
					self.ASSeatBtn[position].config( bg='pale green',fg='gray2',relief=RAISED)
				
			print("Situazione posti da vendere aggiornata: {}".format(self.ASPSeatEnabledBool))		
			ActSelUpdateTotalSell()			
			
		

		
		#=======================================================================
		# ## LIST OF SEAT SELECTED , PRICES AND TYPES
		#=======================================================================
		self.ActSelTL=Toplevel(  background='lavender', borderwidth=1, container = 0, height = 800,takefocus=True,  width=600)
		self.ActSelTL.protocol('WM_DELETE_WINDOW', lambda window=self: ActSelTLExit)
		self.prices=[Decimal('0.00'),self.AAAed['event']['price_reduced'],self.AAAed['event']['price_full']]
		# clean up the data in previous widget instantiates
		for widget in self.ActSelTL.winfo_children():
			widget.destroy()

		gridrow=1
		if mode == BOOK:
			self.ActSelTL.title("Finestra per la prenotazione dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')
			self.price=[self.prices[0] for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		elif mode == SELL:
			self.ActSelTL.title("Finestra per la vendita dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')
			self.price=[self.prices[0] for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		elif mode == SELLABOOK:
			self.ActSelTL.title("Finestra per la vendita dei posti prenotati")
			self.ActSelTL.config(bg='khaki1')
			self.price=[self.prices[0] for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		else:
			self.ActSelTL.title("Finestra per SPARE dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')

		if mode == SELL or mode == SELLABOOK:
			txt_lbl= "Operazione di vendita numero {}".format(self.TotalSellsOperations+1)
		else:
			txt_lbl= "Posti selezionati"

		self.ASTitleLbl=Label(self.ActSelTL,text=txt_lbl,font = LARGE_FONT)
		self.ASTitleLbl.grid(row=gridrow,column=1,columnspan=3,padx=(5,5),pady=(5,5))

		
		self.ASPriceLstb=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		self.ASPriceLbl=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		if mode == SELLABOOK:
			self.ASSeatBtn=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		else:
			self.ASSeatLbl=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		self.ASPSeatEnabledBool=[True for x in range(len(self.SelectionBuffer))]  # @UnusedVariable]
		print("Situazione posti da vendere init: {}".format(self.ASPSeatEnabledBool))

# 		self.price=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		gridrow+=2

		for idx in range(len(self.SelectionBuffer)):
			if mode==SELLABOOK:
				buttonstatus  = int(self.ListSoldStatus[idx])
				
				if not buttonstatus:
					self.ASSeatBtn[idx]=Button(self.ActSelTL,font=NORM_FONT,text=self.seat_name[self.SelectionBuffer[idx]],state=NORMAL,
							width=2,activeforeground='red', bg='pale green',fg='gray2',relief=RAISED,
							command= lambda position =idx : ActSelToggleBbookseat(position,mode=TOGGLE))
					self.ASPSeatEnabledBool[idx]=True
				else:
					self.ASSeatBtn[idx]=Button(self.ActSelTL,font=NORM_FONT,text=self.seat_name[self.SelectionBuffer[idx]],state=NORMAL,
							width=2, bg='red',fg='gray2',relief=SUNKEN ,
							command= lambda position =idx : ActSelToggleBbookseat(position,mode=REQUEST_CHANGE))
					self.ASPSeatEnabledBool[idx]=False
				self.ASSeatBtn[idx].grid(row=gridrow,column=1,columnspan=1,padx=(5,5),pady=(5,5))
				pass
			else:
				self.ASSeatLbl[idx]=Label(self.ActSelTL,font=NORM_FONT,text=self.seat_name[self.SelectionBuffer[idx]])
				self.ASSeatLbl[idx].grid(row=gridrow,column=1,columnspan=1,padx=(5,5),pady=(5,5))

			self.ASPriceLstb[idx]=Listbox(self.ActSelTL,selectmode=BROWSE)
			self.ASPriceLstb[idx].insert(END,"Gratuito")
			self.ASPriceLstb[idx].insert(END,"Ridotto")
			self.ASPriceLstb[idx].insert(END,"Intero")


	# 		self.EvChEventLbx.bind("<Double-Button-1>", self.ok)
			if mode == SELL or mode == BOOK:
				default_price=FULL_PRICE
			elif mode == SELLABOOK:
				default_price=self.booking_prices[idx]

			self.ASPriceLstb[idx].grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
			self.ASPriceLstb[idx].config(height=3,width=8,font=MEDIUM_FONT,exportselection=False)
			self.ASPriceLstb[idx].select_set(default_price)
			self.ASPriceLstb[idx].bind('<<ListboxSelect>>', choose)

			self.ASPriceLbl[idx]=Label(self.ActSelTL,font=NORM_FONT,text=self.prices[default_price])
			self.ASPriceLbl[idx].grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))


			self.toggle_status(self.SelectionBuffer[idx], DISABLE)
			self.SelectionReset.config(state=DISABLED)
		

			gridrow+=1
		
		print("Situazione posti da vendere caricamento finestra: {}".format(self.ASPSeatEnabledBool))
		
		gridrow+=1
		self.ASTotalAmountTitle=Label(self.ActSelTL,font=LARGE_FONT,text="Totale prezzo ingressi")
		self.ASTotalAmountTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))

		self.TotalPrice= self.prices[default_price]*len(self.SelectionBuffer)


		self.ASTotalAmountLbl=Label(self.ActSelTL,font=LARGE_FONT,text=self.TotalPrice)
		self.ASTotalAmountLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))

		gridrow+=2

		self.TotalTransactionFullPrice= 0
		self.TotalTransactionReducedPrice=0
		self.TotalTransactionFreePrice=0


		for w in self.ASPriceLstb:
			if w.curselection()[0]== FULL_PRICE:
				self.TotalTransactionFullPrice+=1
			elif w.curselection()[0]== REDUCED_PRICE:
				self.TotalTransactionReducedPrice+=1
			elif w.curselection()[0]== FREE_PRICE:
				self.TotalTransactionFreePrice+=1


		self.ASTotalFullPriceTitle=Label(self.ActSelTL,font=NORM_FONT,text="Totale ingressi INTERI")
		self.ASTotalFullPriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalFullPriceLbl=Label(self.ActSelTL,font=NORM_FONT,text=self.TotalTransactionFullPrice)
		self.ASTotalFullPriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
		gridrow+=1
		self.ASTotalReducedPriceTitle=Label(self.ActSelTL,font=NORM_FONT,text="Totale ingressi RIDOTTI")
		self.ASTotalReducedPriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalReducedPriceLbl=Label(self.ActSelTL,font=NORM_FONT,text=self.TotalTransactionReducedPrice)
		self.ASTotalReducedPriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
		gridrow+=1
		self.ASTotalFreePriceTitle=Label(self.ActSelTL,font=NORM_FONT,text="Totale ingressi GRATUITI")
		self.ASTotalFreePriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalFreePriceLbl=Label(self.ActSelTL,font=NORM_FONT,text=self.TotalTransactionFreePrice)
		self.ASTotalFreePriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))



		gridrow+=2
		if mode == SELL:
			btn_text = 'Conferma Vendita'
			self.ASSellBtn=Button(self.ActSelTL,font=NORM_FONT,text=btn_text,state=NORMAL,
					width=25,activebackground='red',activeforeground='yellow',
					bg='green',fg='snow',command= ActSelTLSell)
			self.ASSellBtn.grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
		elif mode == BOOK:
			btn_text = 'Registra Prenotazione'
			self.ASBookBtn=Button(self.ActSelTL,font=NORM_FONT,text=btn_text,state=NORMAL,
								width=25,activebackground='red',activeforeground='yellow',
								bg='green',fg='snow',command= ActSelTLBook)
			self.ASBookBtn.grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
		elif mode== SELLABOOK:
			btn_text = 'Conferma Vendita Prenotazione'
			self.ASSellBtn=Button(self.ActSelTL,font=NORM_FONT,text=btn_text,state=NORMAL,
					width=25,activebackground='red',activeforeground='yellow',
					bg='green',fg='snow',command= ActSelTLSellABook)
			self.ASSellBtn.grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
			
		self.ASexitBtn=Button(self.ActSelTL,font=NORM_FONT,text='Esci',state=NORMAL,
							width=6,activebackground='red',activeforeground='yellow',
												bg='snow4',fg='snow',
							command= ActSelTLExit)
		self.ASexitBtn.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))


		## GENERALITIES ENTRY WIDGETS FOR BOOKING MODE
		if mode == BOOK:
			gridrow=1
			self.ASGeneralitiesTitleLbl=Label(self.ActSelTL,text="Riferimenti prenotazione",font = LARGE_FONT)
			self.ASGeneralitiesTitleLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))

			gridrow+=2

			self.ASSurnameLbl=Label(self.ActSelTL,font=NORM_FONT,width=10,text="Cognome")
			self.ASSurnameLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow+=1
			self.ASNameLbl=Label(self.ActSelTL,font=NORM_FONT,width=10,text="Nome")
			self.ASNameLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow+=1
			self.ASEmailLbl=Label(self.ActSelTL,font=NORM_FONT,width=10,text="Email")
			self.ASEmailLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow+=1
			self.ASPhoneLbl=Label(self.ActSelTL,font=NORM_FONT,width=10,text="Telefono")
			self.ASPhoneLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))
			
			gridrow+=1
			self.ASNoteLbl=Label(self.ActSelTL,font=NORM_FONT,width=10,text="Note")
			self.ASNoteLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow=1

			gridrow+=2

			self.ASSurnameEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Cognome")
			self.ASSurnameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

			gridrow+=1
			self.ASNameEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Nome")
			self.ASNameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

			gridrow+=1
			self.ASEmailEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Email")
			self.ASEmailEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

			gridrow+=1
			self.ASPhoneEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Telefono")
			self.ASPhoneEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
			
			gridrow+=1
			self.ASNoteEnt=Entry(self.ActSelTL,font=NORM_FONT,width=60,text="Note")
			self.ASNoteEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

		elif mode==SELLABOOK:
			try:
				self.ASGeneralitiesTitleLbl.destroy()
			except:
				pass
				
			gridrow=1
			self.ASGeneralitiesTitleLbl=Label(self.ActSelTL,text="Riferimenti prenotazione {}".format(self.SellingBookingCode),font = LARGE_FONT)
			self.ASGeneralitiesTitleLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))

			gridrow+=2
			self.ASSurnameLbl=Label(self.ActSelTL,font=NORM_FONT,width=60,justify=LEFT,text="Cognome: {}".format(self.AAAed['booking'][self.SellingBookingCode][4]))
			self.ASSurnameLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5),sticky=W)

			gridrow+=1
			self.ASNameLbl=Label(self.ActSelTL,font=NORM_FONT,width=60,justify=LEFT,text="Nome: {}".format(self.AAAed['booking'][self.SellingBookingCode][3]))
			self.ASNameLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))

			gridrow+=1
			
			if self.AAAed['booking'][self.SellingBookingCode][5] is not None:
				email_txt =self.AAAed['booking'][self.SellingBookingCode][5]
			else:
				email_txt = 'n.d.'
			
			self.ASEmailLbl=Label(self.ActSelTL,font=NORM_FONT,width=60,justify=LEFT,text="Email: {}".format(email_txt))
			self.ASEmailLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))

			gridrow+=1
			
			if self.AAAed['booking'][self.SellingBookingCode][8] is not None:
				phone_txt = self.AAAed['booking'][self.SellingBookingCode][8]
			else:
				phone_txt = 'n.d.'

			self.ASPhoneLbl=Label(self.ActSelTL,font=NORM_FONT,width=60,justify=LEFT,text="Telefono: {}".format(phone_txt))
			self.ASPhoneLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))
			
			gridrow+=1
			
			if self.AAAed['booking'][self.SellingBookingCode][10] is not None:
				note_txt = self.AAAed['booking'][self.SellingBookingCode][10]
			else:
				note_txt = 'n.d.'			
			self.ASNoteLbl=Label(self.ActSelTL,font=NORM_FONT,width=60, wraplength=400,height=6,justify=LEFT,text="Note: {}".format(note_txt))
			self.ASNoteLbl.grid(row=gridrow,column=4,columnspan=2,padx=(15,5),pady=(5,5))
			
			del note_txt,email_txt,phone_txt


			#--------------------------------------------------------- gridrow=1
#------------------------------------------------------------------------------ 
			#-------------------------------------------------------- gridrow+=2
# # 			self.ASSurnameEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Cognome")
#----------------------------------- # 			self.ASSurnameEnt.config(state=NORMAL)
#----------------------------------------- # 			self.ASSurnameEnt.delete(0, END)
# # 			self.ASSurnameEnt.insert(END, self.AAAed['booking'][self.SellingBookingCode][4])
#--------------------------------- # 			self.ASSurnameEnt.config(state=DISABLED)
# # 			self.ASSurnameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
#------------------------------------------------------------------------------ 
			#-------------------------------------------------------- gridrow+=1
#--------------------------------------------------------------------- # 			try:
#------------------------------------------------ # 				self.ASNameEnt.destroy()
#------------------------------------------------------------------ # 			except:
#-------------------------------------------------------------------- # 				pass
#-- # 			self.ASNameEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Nome")
#-------------------------------------- # 			self.ASNameEnt.config(state=NORMAL)
#-------------------------------------------- # 			self.ASNameEnt.delete(0, END)
# # 			self.ASNameEnt.insert(END, self.AAAed['booking'][self.SellingBookingCode][3])
#------------------------------------ # 			self.ASNameEnt.config(state=DISABLED)
# # 			self.ASNameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
#------------------------------------------------------------------------------ 
			#-------------------------------------------------------- gridrow+=1
#--------------------------------------------------------------------- # 			try:
#----------------------------------------------- # 				self.ASEmailEnt.destroy()
#------------------------------------------------------------------ # 			except:
#-------------------------------------------------------------------- # 				pass
# # 			self.ASEmailEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Email")
#------------------------------------- # 			self.ASEmailEnt.config(state=NORMAL)
#------------------------------------------- # 			self.ASEmailEnt.delete(0, END)
#-------- # 			if self.AAAed['booking'][self.SellingBookingCode][5] is not None:
#------------ # 				email_txt =self.AAAed['booking'][self.SellingBookingCode][5]
#-------------------------------------------------------------------- # 			else:
#------------------------------------------------------ # 				email_txt = 'n.d.'
#----------------------------------- # 			self.ASEmailEnt.insert(END, email_txt)
#----------------------------------- # 			self.ASEmailEnt.config(state=DISABLED)
# # 			self.ASEmailEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
#------------------------------------------------------------------------------ 
			#-------------------------------------------------------- gridrow+=1
#--------------------------------------------------------------------- # 			try:
#----------------------------------------------- # 				self.ASPhoneEnt.destroy()
#------------------------------------------------------------------ # 			except:
#-------------------------------------------------------------------- # 				pass
# # 			self.ASPhoneEnt=Entry(self.ActSelTL,font=NORM_FONT,width=30,text="Telefono")
#------------------------------------- # 			self.ASPhoneEnt.config(state=NORMAL)
#------------------------------------------- # 			self.ASPhoneEnt.delete(0, END)
#-------- # 			if self.AAAed['booking'][self.SellingBookingCode][8] is not None:
#----------- # 				phone_txt = self.AAAed['booking'][self.SellingBookingCode][8]
#-------------------------------------------------------------------- # 			else:
#------------------------------------------------------ # 				phone_txt = 'n.d.'
#----------------------------------- # 			self.ASPhoneEnt.insert(END, phone_txt)
#----------------------------------- # 			self.ASPhoneEnt.config(state=DISABLED)
# # 			self.ASPhoneEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
#------------------------------------------------------------------------------ 
			#-------------------------------------------------------- gridrow+=1
#--------------------------------------------------------------------- # 			try:
#------------------------------------------------ # 				self.ASNoteEnt.destroy()
#------------------------------------------------------------------ # 			except:
#-------------------------------------------------------------------- # 				pass
#-- # 			self.ASNoteEnt=Entry(self.ActSelTL,font=NORM_FONT,width=50,text="Note")
#-------------------------------------- # 			self.ASNoteEnt.config(state=NORMAL)
#-------------------------------------------- # 			self.ASNoteEnt.delete(0, END)
#------- # 			if self.AAAed['booking'][self.SellingBookingCode][10] is not None:
#----------- # 				note_txt = self.AAAed['booking'][self.SellingBookingCode][10]
#-------------------------------------------------------------------- # 			else:
#------------------------------------------------------- # 				note_txt = 'n.d.'
#------------------------------------- # 			self.ASNoteEnt.insert(END, note_txt)
#------------------------------------ # 			self.ASNoteEnt.config(state=DISABLED)
# # 			self.ASNoteEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
		

		ActSelUpdateTotalSell()

	def toggle_status(self,idx,mode=None):
		if mode == SELECT:
			if len(self.SelectionBuffer)<16:
				if idx not in self.SelectionBuffer:
					print('Selezionato posto {}.'.format(self.seat_name[idx]))
					self.btn[idx].config(relief=SUNKEN,bg='yellow')
					self.SelectionBuffer.append(idx)
					self.UpdateSelectionBufferText()
					# FLAT , RAISED, SUNKEN, GROOVE, RIDGE
				else:
					messagebox.showwarning('Posto selezionato in precedenza', 'Hai riselezionato un posto. Se desideri deselezionarlo usa il pulsante Reset Selezione.')
			else:
				messagebox.showwarning('Massimo dei posti selezionati', 'Non puoi effettuare selezioni maggiori di 16 posti.')
		elif mode== DESELECT:
			self.RefreshSeats('one', idx)
		elif mode==DISABLE:
			self.btn[idx].config(state=DISABLED)

	def booking_code_window(self):
		def insert_booking(event):
			print(self.BCWbooking_code.get())
			raw_code= self.BCWbooking_code.get()
			self.booking_code_w.destroy()
			print('rawcode read = {}'.format(raw_code))
			try:
				code_season_year_id = int(raw_code[3:4])
				print('rawcode read = {}'.format(raw_code))
				print('code_season_year_id read = {}'.format(code_season_year_id))
				if code_season_year_id != self.AAAed['show']['season_year_id']:
					raise BookingCodeError({"message":"Codice stagione della prenotazione non coerente.", "season":self.AAAed['show']['season_year_id']})
				code_show_id=int(raw_code[5:7])
				print('code_show_id read = {} == {}'.format(code_show_id,self.AAAed['event']['show_id']))
				if code_show_id!= self.AAAed['event']['show_id']:
					raise BookingCodeError({"message":"Codice spettacolo della prenotazione non coerente.", "show":self.AAAed['event']['show_id']})
			except:
				messagebox.showerror("ERRORE DI LETTURA DEL BARCODE","Il codice a barre letto non è coerente con una prenotazione o non è per lo spettacolo in corso.")
			try:
				booking_id = int(raw_code[8:12])
				print('booking_id read = {} '.format(booking_id))
			except ValueError:
				messagebox.showerror("ERRORE DI LETTURA DEL BARCODE","Il codice a barre letto non è coerente con una prenotazione o non è per lo spettacolo in corso.")
			booking_id_code = str(booking_id).zfill(6)
			print('booking_id_code read = {} == {}'.format(booking_id_code,self.AAAed['booking'][booking_id_code]))
			if booking_id_code in self.AAAed['booking']:
				booking_obj= self.AAAed['booking'][booking_id_code]
				if '0' in booking_obj[9]:
					self.GetBooking(booking_id_code,mode=SELECT)
				else:
					messagebox.showwarning('Errore Prenotazione', 'La prenotazione relativa al codice letto dal codice a barre risulta essere già stata venduta! CONTROLLARE LA SITUAZIONE DELLA SALA.')
		def clear_BCW():
			self.booking_code_w.destroy()
		
		self.booking_code_w = Toplevel(self)
		self.BCWlabel = Label(self.booking_code_w, text="Scannerizza il QR o Barcode della prenotazione")
		self.BCWlabel.pack(fill=X)
		self.BCWbooking_code = Entry(self.booking_code_w, width= 20)
		self.BCWbooking_code.pack(fill=X)
		self.BCWbooking_code.focus_set()
		self.BCWgo= Button(self.booking_code_w,bg='green', fg='white',text="Procedi",command= insert_booking)
		self.BCWgo.pack(fill=X)
		self.BCWcancel= Button(self.booking_code_w,bg='red', fg='yellow', text="Esci",command= clear_BCW)
		self.BCWcancel.pack(fill=X)
		self.BCWgo.bind('<Button-1>',insert_booking)
		self.booking_code_w.bind('<Return>',insert_booking)
		
			



	def resetSelection(self):
		for idx in self.SelectionBuffer:
			self.toggle_status(idx,mode=DESELECT)
# 			self.btn[idx].config(relief=RAISED)
# 			self.btn[idx].config(bg='lightgrey')
		self.SelectionBuffer=[]
		self.UpdateSelectionBufferText()

	def UpdateSelectionBufferText(self):
		self.SelectionBufferText.delete('1.0', END)
		for idx in self.SelectionBuffer:
			self.SelectionBufferText.insert(END,str(idx)+'\t'+self.seat_name[idx]+'\n')

	def OpenEvent(self):

		def choose(evt):
			try:
				self.event= self.EvChEventLbx.get(self.EvChEventLbx.curselection())
				self.ev_id = self.event.split('#')[0]
			except IndexError:
				print("Index error")
			finally:

				print("Scelta : ID record evento = {} - da item {}".format(self.ev_id,self.event))
				pass
		def event_open():
			self.EvCh_TL.destroy()
			print("Evento scelto e in apertura = {}".format(self.event))
			if self.EventDataChanged:
				messagebox.showwarning('Apertura evento con dati non salvati','Stai aprendo un nuovo evento ma i dati di quello precedente non sono completamente salvati.Puoi procedere solo dopo aver salvato i dati di questa sessione')
			else:
				## Instantiate the event data dictionary to keep event's data for session
				## structure:
				## ['event'] = dictionary of event info
				try:
					self.AAAed= defaultdict(dict)
				except NameError:
					self.AAAed= defaultdict(dict)
				# query booking_event - heavy priority data
				# putting information on ed (event dictionary) in the inner event dictionary
				sql_cmd="SELECT * FROM booking_event where booking_event.id = {};".format(int(self.ev_id))
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.AAAed['event']['id']=data[0]
				self.AAAed['event']['creation_date']=data[1]
				self.AAAed['event']['event_date']=data[2]
				self.AAAed['event']['booking_status']=data[3]
				self.AAAed['event']['booking_user']=data[4]
				self.AAAed['event']['booking_price']=data[5]
				self.AAAed['event']['booking_datetime']=data[6]
				self.AAAed['event']['price_full']=data[7]
				self.AAAed['event']['price_reduced']=data[8]
				self.AAAed['event']['author_id']=data[9]
				self.AAAed['event']['show_id']=data[10]
				self.AAAed['event']['change']=data[11]
				#print(self.AAAed['event'])

				# crea una list per uso diretto senza dover ripetere operazione di split tutte le volte
				self.AAAed['seat_status']=self.AAAed['event']['booking_status'].split(',')
				self.AAAed['seat_prices']=self.AAAed['event']['booking_price'].split(',')

				# query booking_show - low priority data
				# putting information on ed (event dictionary) in the inner show dictionary

				sql_cmd="SELECT * FROM booking_show where booking_show.id = {};".format(self.AAAed['event']['show_id'])
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.AAAed['show']['id']=data[0]
				self.AAAed['show']['company']=data[1]
				self.AAAed['show']['title']=data[2]
				self.AAAed['show']['text']=data[3]
				self.AAAed['show']['season_year_id']=data[4]
				self.AAAed['show']['debut_date']=data[5]
				self.AAAed['show']['director']=data[6]
				self.AAAed['show']['cast']=data[7]
				self.AAAed['show']['shw_code']=data[8]
				#print(self.AAAed['show'])

				# query booking_bookingseason - low priority data
				# putting information on ed (event dictionary) in the inner season dictionary

				sql_cmd="SELECT * FROM booking_bookingseason where booking_bookingseason.id = {};".format(self.AAAed['show']['season_year_id'])
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.AAAed['season']['id']=data[0]
				self.AAAed['season']['label']=data[1]
				self.AAAed['season']['start_date']=data[2]
				self.AAAed['season']['end_date']=data[3]
				self.AAAed['season']['booking_enabled']=data[4]
				self.AAAed['season']['ssn_code']=data[5]
				#print(self.AAAed['season'])

				# query booking_booking - high priority data
				# putting information on ed (event dictionary) in the inner bookings dictionary

				sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.AAAed['event']['id']))
				result=self.mysqlcursor.execute(sql_cmd)
				if result < 1:
					self.AAAed['booking']['quantity']=result
				else:
					self.AAAed['booking']['quantity']=result
					for idx in range(result):  # @UnusedVariable
						data=self.mysqlcursor.fetchone()
						self.AAAed['booking'][str(data[0]).zfill(6)]=data
					#	print(self.AAAed['booking'][str(data[0]).zfill(6)])

				# Initialize opening Totalizers
				# Extract the sold seats in a temporary dictionary

				Opening_SoldSeat_prices = []
				for idx,price in enumerate(self.AAAed['seat_prices']):
					if self.AAAed['seat_status'][idx]==SOLD:
						Opening_SoldSeat_prices.append(price)
				Event_Prices=Counter(Opening_SoldSeat_prices)
				#print(Event_Prices)
				self.AAAed['Totals']['open_price']=Event_Prices
				Event_Revenue = Event_Prices[str(FULL_PRICE)]*self.AAAed['event']['price_full']+Event_Prices[str(REDUCED_PRICE)]*self.AAAed['event']['price_reduced']
				self.AAAed['Totals']['open_revenue']=Event_Revenue

				# When opening event the Totalizers Totals are set as Opning ones
				self.AAAed['Totals']['totals_price']=Event_Prices
				self.AAAed['Totals']['totals_revenue']=Event_Revenue

				# When opening event the Totalizers session are set to Zero
				self.AAAed['Totals']['session_price']=Counter({'2': 0, '1': 0, '0': 0})
				self.AAAed['Totals']['session_revenue']=Decimal('0.00')

				# Initialize the counter of selling operations in event current session

				self.TotalSellsOperations=0
				
				# Enable the File Menu Item for Close event

				self.file.entryconfig("Chiudi_evento", state=NORMAL)

				#cleaning
				del Event_Prices,Opening_SoldSeat_prices,sql_cmd, result, data, price, idx,Event_Revenue

# 			sleep(5)


			## Main refresh of application data for event opening
			self.RefreshSeats(mode='full')
			self.RefreshEventInfo(mode='full')
			self.RefreshBooking(mode='full')
			self.RefreshTotalizers(mode=OPENING)
			self.session_open = True
			try:
				with open("session_dumpdata.dat", "wb") as f:
					pickle.dump(self.AAAed,f, protocol=pickle.HIGHEST_PROTOCOL)
			except (pickle.PickleError) as e:
				messagebox.showerror("Errore nel salvataggio della sessione", "Il programma ha trovato questo errore:/n {}/n Non è consentito il proseguimento./nIl programma verrà terminato. Premi OK per terminare".format(e))
				exit(1)

		if running_mode == DEVELOPMENT:
			sql_cmd="SELECT booking_show.title,booking_event.`id`,`event_date` FROM `booking_event` JOIN booking_show ON booking_event.show_id = booking_show.id ORDER BY booking_event.`event_date`;"
		else:
			sql_cmd="SELECT booking_show.title,booking_event.`id`,`event_date` FROM `booking_event` JOIN booking_show ON booking_event.show_id = booking_show.id WHERE booking_event.`event_date` >= CURDATE() ORDER BY booking_event.`event_date`;"
		self.mysqlcursor.execute(sql_cmd)
		self.result = self.mysqlcursor.fetchall()


		self.EvCh_TL = Toplevel(self)
		self.EvCh_TL.title("Scelta dell'evento da aprire in cassa")

		self.EvCh_TL.geometry("600x450")

		self.label = Label(self.EvCh_TL, text="Evento",font=LARGE_FONT)
		self.label.grid(row=1,column=1,columnspan=2)


		self.EvChEventLbx=Listbox(self.EvCh_TL,selectmode=BROWSE)
		for row in self.result:
			date_aware=row[2]+timedelta(hours=2)
			item = "{:0>6d}# {}: '{}'".format(row[1],date_aware.strftime('%a, %d/%m/%y ore %H'),row[0])
			self.EvChEventLbx.insert(END,item)
		self.EvChEventLbx.grid(row=2,column=1,columnspan=2)
		self.EvChEventLbx.config(height=15,width=50)
		self.EvChEventLbx.bind('<<ListboxSelect>>',choose)
# 		self.EvChEventLbx.bind("<Return>", choose)
# 		self.EvChEventLbx.bind("<Double-Button-1>", choose)
# 		self.EvChEventLbx.bind("<Escape>", self._cancel)
		self.event_choice_okbtn=Button(self.EvCh_TL,font=NORM_FONT,text='{}'.format("OK"),
												width=20,activebackground='green',activeforeground='white',
												command= event_open)
		self.event_choice_okbtn.grid(row=3,column=1)
		self.event_choice_exitbtn=Button(self.EvCh_TL,font=NORM_FONT,text='{}'.format("Cancel"),
												width=20,activebackground='red',activeforeground='yellow',
												bg='snow4',fg='snow',
												command= self.EvCh_TL.destroy)
		self.event_choice_exitbtn.grid(row=3,column=2)

	def CloseEvent(self):
		print("Chiusura dell'evento {}".format(self.AAAed['event']['id']))
		if not self.EventDataChanged:
			answer=messagebox.askyesno("Richiesta chiusura evento", "Sei sicuro di voler chiudere l'evento corrente?")
			print(answer)
			if answer ==True:
				self.init_window(mode=REINIT)
		else:
			answer=messagebox.askyesno("Dati non salvati", "Ci sono dati non salvati. Sei sicuro di voler chiudere l'evento corrente?")
				
				
	
	
	def RefreshSeats(self,mode=None,idx=None):
		def setseat(seat,st):
			if st== AVAILABLE:
				self.btn[seat].config(bg='pale green',fg='gray2',state= NORMAL,relief=RAISED)
				pass
			elif st==BOOKED:
				self.btn[seat].config(bg='goldenrod',fg='ivory',state=DISABLED,relief=RIDGE)
			elif st==SOLD:
				self.btn[seat].config(bg='indian red',fg='ivory',state=DISABLED,relief=FLAT)
			else:
				pass


		print('Refreshing the Seats Grid with mode = {}'.format(mode))
		if mode=="full":
			for idx in range(263):
				status=self.AAAed['seat_status'][idx]
				setseat(idx,status)
		elif mode=='one':
			status=self.AAAed['seat_status'][idx]
			setseat(idx,status)

	def RefreshEventInfo(self,mode=None):


		self.LblEvent_company.config(text="Compagnia: {}".format(self.AAAed['show']['company']))

		self.LblEvent_title.config(text="Titolo: {}".format(self.AAAed['show']['title']))

		date_aware=rome.localize(self.AAAed['event']['event_date']+timedelta(hours=2))
		self.LblEvent_date.config(text="Data: {}".format(date_aware.strftime('%A, %d/%m/%y ')))

		self.LblEvent_time.config(text="Ora: {}".format(date_aware.strftime( '%H:%M')))

		self.LblEvent_price_full.config(text="Intero = {}".format(self.AAAed['event']['price_full']))

		self.LblEvent_price_reduced.config(text="Ridotto = {}".format(self.AAAed['event']['price_reduced']))

		self.LblEvent_season.config(text="Stagione Teatrale {}".format(self.AAAed['season']['label']))

		self.LblEvent_season_code.config(text="Codice {}".format(self.AAAed['season']['ssn_code']))

		self.LblEvent_show_code.config(text="Codice spettacolo = {}".format(self.AAAed['show']['shw_code']))

	def SelectEvent(self):
		pass


	def RefreshBooking(self, mode=None):
		for widget in self.FrameBooking.winfo_children():
			if widget ==self.BookingTitle or widget==self.BookingBarCodebtn:
				pass
			else:
				widget.destroy()

		if self.AAAed['booking']['quantity']:
			self.LblBookingCodeTitle= Label(self.FrameBooking,height = 1,width=8,font=SMALL_FONT,text="Codice")
			self.LblBookingCodeTitle.grid(row=3,column=1,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingSurnameTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Cognome")
			self.LblBookingSurnameTitle.grid(row=3,column=2,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingNameTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Nome")
			self.LblBookingNameTitle.grid(row=3,column=3,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingPhoneTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Telefono")
			self.LblBookingPhoneTitle.grid(row=3,column=4,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
# 			self.LblBookingDateTitle= Label(self.FrameBooking,height = 1,width=12,font=SMALL_FONT,text="Data")
# 			self.LblBookingDateTitle.grid(row=3,column=5,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingSeatsTitle= Label(self.FrameBooking,height = 1,width=42,font=SMALL_FONT,text="Posti")
			self.LblBookingSeatsTitle.grid(row=3,column=5,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)
			self.LblBookingNoteTitle= Label(self.FrameBooking,height = 1,width=42,font=SMALL_FONT,text="Note")
			self.LblBookingNoteTitle.grid(row=3,column=6,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)

			self.BtnBookingCode=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingSurname=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingName=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingPhone=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
# 			self.LblBookingDate=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingSeats=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingNote=[0 for x in range(self.AAAed['booking']['quantity'])]  # @UnusedVariable
			idx=0
			start_row=4
			row_spacer=0
			for key,booking in sorted(self.AAAed['booking'].items()):

				if not key== 'quantity':
					StringsBookingSold=booking[9]
					sold_check_list,StringsBookingSold,Update = self.BookingSoldStatusManager(SoldStatusString=StringsBookingSold, mode=CHECK, SeatPosition=None, SeatsString=booking[2])
					if Update:
						self.BookingSoldStatusManager(SoldStatusString=StringsBookingSold, mode=UPDATE, book_code=key)
						#BUG FIX tuple immutable violation 						self.AAAed['booking'][key][9]=StringsBookingSold
						self.Read_a_Booking(key)
					sold_check = True
					if '0' in sold_check_list:
						sold_check=False
				if not key== 'quantity' and not sold_check:
					
					if booking[10] is not None:
						max_chars = max(len(booking[2]),len(booking[10]))
					else:
						max_chars=len(booking[2])
					row_space= int(max_chars/30+0.5)+row_spacer
					
					self.BtnBookingCode[idx]= Button(self.FrameBooking,height = row_space,width=8,state=NORMAL,bg='green2',fg='blue4',
												font=SMALL_FONT,text=key,command = lambda code=key : self.GetBooking(code,mode=SELECT))
					self.BtnBookingCode[idx].grid(row=start_row,column=1,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSurname[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[4])
					self.LblBookingSurname[idx].grid(row=start_row,column=2,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingName[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[3])
					self.LblBookingName[idx].grid(row=start_row,column=3,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingPhone[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[8])
					self.LblBookingPhone[idx].grid(row=start_row,column=4,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
# 					self.LblBookingDate[idx]= Label(self.FrameBooking,height = row_space,width=12,
# 												font=SMALL_FONT,text=booking[1].strftime('%d/%m/%Y'))
# 					self.LblBookingDate[idx].grid(row=start_row,column=5,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSeats[idx]= Label(self.FrameBooking,height = row_space,width=42,
												font=SMALL_FONT,text=booking[2],wraplength=140,anchor=W,)
					self.LblBookingSeats[idx].grid(row=start_row,column=5,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)
					
					self.LblBookingNote[idx]= Label(self.FrameBooking,height = row_space,width=42,
												font=SMALL_FONT,text=booking[10],wraplength=140,anchor=W,)
					self.LblBookingNote[idx].grid(row=start_row,column=6,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)
					
					start_row+=row_space+1
					idx+=1
			
			for key,booking in sorted(self.AAAed['booking'].items()):

				
				if not key== 'quantity':
					StringsBookingSold=booking[9]
					sold_check_list,StringsBookingSold,Update = self.BookingSoldStatusManager(SoldStatusString=StringsBookingSold, mode=CHECK, SeatPosition=None, SeatsString=booking[2])
					sold_check = True
					if '0' in sold_check_list:
						sold_check=False
				if not key== 'quantity' and sold_check:
					
					if booking[10] is not None:
						max_chars = max(len(booking[2]),len(booking[10]))
					else:
						max_chars=len(booking[2])
					row_space= int(max_chars/30+0.5)+row_spacer

					self.BtnBookingCode[idx]= Button(self.FrameBooking,height = row_space,width=8,state=DISABLED,bg='IndianRed4',fg='snow2',
												font=SMALL_FONT,text=key,command = lambda code=key : self.GetBooking(code,mode=SELECT))
					self.BtnBookingCode[idx].grid(row=start_row,column=1,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSurname[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[4])
					self.LblBookingSurname[idx].grid(row=start_row,column=2,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingName[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[3])
					self.LblBookingName[idx].grid(row=start_row,column=3,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingPhone[idx]= Label(self.FrameBooking,height = row_space,width=15,
												font=SMALL_FONT,text=booking[8])
					self.LblBookingPhone[idx].grid(row=start_row,column=4,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
# 					self.LblBookingDate[idx]= Label(self.FrameBooking,height = row_space,width=12,
# 												font=SMALL_FONT,text=booking[1].strftime('%d/%m/%Y'))
# 					self.LblBookingDate[idx].grid(row=start_row,column=5,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSeats[idx]= Label(self.FrameBooking,height = row_space,width=42,wraplength=140,anchor=W,
												font=SMALL_FONT,text=booking[2])
					self.LblBookingSeats[idx].grid(row=start_row,column=5,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)
					
					self.LblBookingNote[idx]= Label(self.FrameBooking,height = row_space,width=42,
												font=SMALL_FONT,text=booking[10],wraplength=140,anchor=W,)
					self.LblBookingNote[idx].grid(row=start_row,column=6,padx=(1,1),pady=(1,1),columnspan=1,sticky=W)
					
					start_row+=row_space+1
					idx+=1
		else:
			self.LblBookingFrameTitle= Label(self.FrameBooking,height = 3,width=25,font=NORM_FONT,text="Non ci sono \nprenotazioni attive \nper questo evento")
			self.LblBookingFrameTitle.grid(row=2,column=1,padx=(0,0),pady=(0,0),columnspan=4,sticky=W)

	def RefreshTotalizers(self,mode=None):
		if mode==OPENING:
			self.Totalizers.set(self.TotalizersOpening,'full_price',self.AAAed['Totals']['open_price'][str(FULL_PRICE)])
			self.Totalizers.set(self.TotalizersOpening,'reduced_price',self.AAAed['Totals']['open_price'][str(REDUCED_PRICE)])
			self.Totalizers.set(self.TotalizersOpening,'free_price',self.AAAed['Totals']['open_price'][str(FREE_PRICE)])
			self.Totalizers.set(self.TotalizersOpening,'revenue',self.AAAed['Totals']['open_revenue'])

			self.Totalizers.set(self.TotalizersTotals,'full_price',self.AAAed['Totals']['totals_price'][str(FULL_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'reduced_price',self.AAAed['Totals']['totals_price'][str(REDUCED_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'free_price',self.AAAed['Totals']['totals_price'][str(FREE_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'revenue',self.AAAed['Totals']['totals_revenue'])

		if mode==SESSION:
			self.Totalizers.set(self.TotalizersSession,'full_price',self.AAAed['Totals']['session_price'][str(FULL_PRICE)])
			self.Totalizers.set(self.TotalizersSession,'reduced_price',self.AAAed['Totals']['session_price'][str(REDUCED_PRICE)])
			self.Totalizers.set(self.TotalizersSession,'free_price',self.AAAed['Totals']['session_price'][str(FREE_PRICE)])
			self.Totalizers.set(self.TotalizersSession,'revenue',self.AAAed['Totals']['session_revenue'])



			self.Totalizers.set(self.TotalizersTotals,'full_price',self.AAAed['Totals']['totals_price'][str(FULL_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'reduced_price',self.AAAed['Totals']['totals_price'][str(REDUCED_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'free_price',self.AAAed['Totals']['totals_price'][str(FREE_PRICE)])
			self.Totalizers.set(self.TotalizersTotals,'revenue',self.AAAed['Totals']['totals_revenue'])




# 		self.TotalizersSession=self.Totalizers.insert('', 'end', text="Sessione cassa", values=(0,0,0,Decimal('0.00')))
# 		self.TotalizersTotals=self.Totalizers.insert('', 'end', text="TOTALE", values=(0,0,0,Decimal('0.00')))



	def GetBooking(self,code,mode=None):
		self.SellingBookingCode=code

		print("Elaboro la prenotazione codice {}".format(code))
		self.booking_prices=[]
		if len(self.SelectionBuffer):
			title = "Selezione posti non vuota"
			question ="""Hai scelto di aprire una prenotazione ma hai dei posti selezionati in precedenza.
			Vuoi aggiungere i posti della prenotazione a quelli selezionati prima?"""
			answer = messagebox.askquestion(title,question )
			if answer == 'no':
				self.resetSelection()
			else:
				for seat in self.SelectionBuffer:
					self.booking_prices.append(FULL_PRICE)

		booking_seats=self.AAAed['booking'][code][2].split(',')
		self.ListSoldStatus=self.AAAed['booking'][code][9].split(',')

		for seat in booking_seats:
			if seat !='':
				seat_idx = self.seat_name.index(seat.split('$')[0])
				self.SelectionBuffer.append(seat_idx)
# 				self.RefreshSeats('one', seat_idx)
				self.booking_prices.append(int(seat.split('$')[1]))
			else:
				pass
		self.UpdateSelectionBufferText()


		self.ActionOnSelection(mode = SELLABOOK)

	def BookingSoldStatusManager(self,SoldStatusString=None,mode=None,SeatPosition = None,SeatsString=None,book_code=None):
		# modes for BookingSoldStatusManager function
# 		CHECK 		= 1
# 		SOLD_CHECK 	= 2
# 		UPDATE 		= 3
		if mode == None:
			return
		elif mode == CHECK:
			SeatList=SeatsString.rstrip(',').split(',')
			if SoldStatusString is not None:
				SoldStatusList = SoldStatusString.split(',')
				if len(SoldStatusList) != len(SeatList):
					if len(SoldStatusList) < len(SeatList):
# 						SoldStatusList=[]
						if len(SoldStatusList)==1:
							char_filler=SoldStatusList[0]
						for idx in range(len(SeatList)):
							if idx >= len(SoldStatusList):
								SoldStatusList.append(char_filler)
					else:
						TmpList = SoldStatusList[:len(SeatList)]
						SoldStatusList=TmpList
					Update = True
				else:
					Update = False
				for idx in range(len(SeatList)):
					try:
						if SoldStatusList[idx] == '0' or SoldStatusList[idx] =='1':
							pass
						else:
							SoldStatusList[idx] = '0'
					except:
						print("Errore nella definizione della stringa SoldStatus")
			else:
				SoldStatusList=[]
				for idx in range(len(SeatList)):
					SoldStatusList.append('0')
				Update=True
			if Update:
				SoldStatusString=''
				SoldStatusString=','.join(SoldStatusList)
			return SoldStatusList,SoldStatusString,Update
		elif mode ==UPDATE:
			id_record = int(book_code)
			sql_cmd = "UPDATE `booking_booking` SET `book_sold` = '{}' WHERE id = {} ;".format(SoldStatusString,id_record)
			print(sql_cmd)
			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
			except:
				self.mysql.rollback()
						
			
	def RecordTransaction(self,transaction_data):
		created_date_tmp = time.strftime('%Y-%m-%d %H:%M:%S')
		seats_sold = transaction_data['seats_sold']
		amount=transaction_data['amount']
		event_id = self.AAAed['event']['id']
		sql_cmd = "INSERT INTO `booking_boxoffice_transaction` ( `created_date`, `seats_sold`, `amount`, `event_id`) VALUES ('{}','{}','{}','{}');".format(created_date_tmp,seats_sold,amount,event_id)
		print(sql_cmd)
		try:
			self.mysqlcursor.execute(sql_cmd)
			self.mysql.commit()
		except:
			self.mysql.rollback()
		finally:
			print("Mysql executed")		
	
	def Read_a_Booking(self,booking_code):
		# query booking_booking - high priority data
		# putting information on ed (event dictionary) in the inner bookings dictionary

		sql_cmd="SELECT * FROM booking_booking where booking_booking.id = {};".format(int(booking_code))
		result=self.mysqlcursor.execute(sql_cmd)
		if result < 1:
			pass
		else:
			data=self.mysqlcursor.fetchone()
			self.AAAed['booking'][booking_code]=data

	def client_exit(self):
		try:
			self.mysql.close()
			print("OK ---> MySQL connection closed!!!")
		except:
			print("OK ---> MySQL was not open. No action taken closing.")
		if not self.EventDataChanged:
			print("Remove 'session_dumpdata.dat' on clean exit")
			os.remove("session_dumpdata.dat") if os.path.exists("session_dumpdata.dat") else None
		else:
			print("Don't remove 'session_dumpdata.dat' on not clean exit")

		print("Shutting down GUI. Good bye. Come back soon!")
		# clean up the data in previous widget instantiates
		for widget in self.BookingFrameGUI.winfo_children():
			widget.destroy()
		self.BookingFrameGUI.destroy()
		exit(0)

if __name__ == '__main__':


	# Crea una time zone
	rome = pytz.timezone("Europe/Rome")

	# root window created. Here, that would be the only window, but
	# you can later have windows within windows.
	root = Tk()

	root.geometry("1600x900")

	#creation of an instance
	app = Window(root)

	root.protocol('WM_DELETE_WINDOW', app.client_exit)  # root is your root window
	#mainloop
	root.mainloop()



