'''
Created on 02 ott 2017

to use with pre OS command
ssh -n -N -f -L 3306:127.0.0.1:3306 ltc@teatrocambiano.sytes.net
for tunneling connection to mysql server if used from remote location

@author: beppe
'''
# Simple enough, just import everything from tkinter.
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Atspi', '2.0')
# from gi.repository import Gtk, Gdk

from tkinter import *
from tkinter import messagebox
import MySQLdb


#download and install pillow:
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow
from PIL import ImageTk
from PIL import Image

from button_array_location import rows_name,seats  # @UnresolvedImport
from datetime import timedelta
# from orca.scripts import self_voicing
from collections import defaultdict
from dicttoxml import dicttoxml
# from time import sleep
# import code
# from orca.scripts import self_voicing
from decimal import Decimal
import time, pytz


# from tunneling_mysql import MySQL_Ssh_Tunnel  # @UnresolvedImport
## GLOBAL SETTINGS AND VARIABLE

# FONTS FOR GUI
HUGE_FONT = ("DejaVuSansMono", 16)
LARGE_FONT = ("DejaVuSansMono", 12)
NORM_FONT = ("DejaVuSansMono", 9)
SMALL_FONT = ("DejaVuSansMono", 7)
# HUGE_FONT = ("Verdana", 16)
# LARGE_FONT = ("Verdana", 12)
# NORM_FONT = ("Verdana", 9)
# SMALL_FONT = ("Verdana", 7)

# SEATS STATUS CODE
UNAVAILABLE = '0'
AVAILABLE 	= '1'
BOOKED 		= '2'
SOLD		= '3'

# PROCES CODES
FREE_PRICE = 0
REDUCED_PRICE = 1
FULL_PRICE = 2


# RUNNING MODE SET 
DEVELOPMENT = 1
PRODUCTION  = 0

running_mode = DEVELOPMENT

# modes for toggle seat buttons
DISABLE 	= 2
SELECT 		= 1
DESELECT 	= 0

# modes for TopLevel actions with selection
SELL = 3
BOOK = 2
CLEAR = 0



class MsgDialog:

	def __init__(self, parent,title,message):

		top = self.top = Toplevel(parent)

		Label(top, text=title).pack()
		Label(top, text=message).pack()

		b = Button(top, text="Close", command=self.close)
		b.pack(pady=5)

	def close(self):

		self.top.destroy()

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
		## Instantiate the event data dictionary to keep event's data for session
		## structure:
		## ['event'] = dictionary of event info 
		self.ed= defaultdict(dict)
		# 		# Open the ssh tunnel on port 3306 for MySQL connection	
# 		self.ssh_tunnel=MySQL_Ssh_Tunnel('teatrocambiano.sytes.net')
# 		self.ssh_tunnel.ssh_start()
		
		

		
		# parameters that you want to send through the Frame class. 
		Frame.__init__(self, master)   

		#reference to the master widget, which is the tk window				 
		self.master = master
		
# 		# Open the MySQL connection using the tunnel
# 		try:
# 			try:
# 				self.mysql= MySQLdb.connect("127.0.0.1","ltc","ltc","ltcsite")
# 				self.mysqlcursor=self.mysql.cursor()
# 				self.mysqlcursor.execute("SELECT VERSION()")
# 			except (MySQLdb.Error,MySQLdb.Warning) as e:  # @UndefinedVariable
# 				print(e)
# 				self.mysql_active=False
# 				exit(1)
# 		
# 			self.mysql_active=True
# 			data,=self.mysqlcursor.fetchone()
# 			print("Version of mysql opened ={}".format(data))
# 			sqlcomm="SHOW TABLES;"
# 			self.mysqlcursor.execute(sqlcomm)
# 			lines= self.mysqlcursor.fetchall()
# 			for line, in lines:
# 				print("Table {}".format(line))
# 			
# 		finally:
# 			if self.mysql_active:
# 				print("OK ---> Connection to MySqlDb establish!")
# 			else:
# 				print("KO ---> Connection to MySqlDb cannot be established!")


		#with that, we want to then run init_window, which doesn't yet exist
		self.init_window()
		
		

	#Creation of init_window
	def init_window(self):
		
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
		# 		self.ed['show']['id']=data[0]
		# 		self.ed['show']['company']=data[1]
		# 		self.ed['show']['title']=data[2]
		# 		self.ed['show']['text']=data[3]
		# 		self.ed['show']['season_year_id']=data[4]
		# 		self.ed['show']['debut_date']=data[5]
		# 		self.ed['show']['director']=data[6]
		# 		self.ed['show']['cast']=data[7]
		# 		self.ed['show']['shw_code']=data[8]
				
				
				
		# 		self.ed['event']['event_date']=data[2]
		# 		self.ed['event']['booking_status']=data[3]
		# 		self.ed['event']['booking_user']=data[4]
		# 		self.ed['event']['booking_price']=data[5]
		# 		self.ed['event']['booking_datetime']=data[6]
		# 		self.ed['event']['price_full']=data[7]
		# 		self.ed['event']['price_reduced']=data[8]
		# 		self.ed['event']['author_id']=data[9]
		# 		self.ed['event']['show_id']=data[10]
		# 		self.ed['event']['change']=data[11]
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
		self.SelectionBufferText= Text(self.FrameSelectionActions,height = 20,width=30)
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
					elif row=='I' or row=='Q':
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
		self.FrameBooking.grid(columnspan=1,rowspan=2)
		
		# Finestra con le prenotazioni attive
		self.BookingTitle= Label(self.FrameBooking,height = 1,width=30,font=HUGE_FONT,text="Prenotazioni attive")
		self.BookingTitle.grid(row=1,column=1,padx=(0,0),pady=(0,0),columnspan=5,sticky=N)		

		## CREATING A MENU FOR ROOT WINDOW ####################################
		## FILE AND EDIT
		menu = Menu(self.master)
		self.master.config(menu=menu)

		# create the file object)
		file = Menu(menu)

		# adds a command to the menu option, calling it exit, and the

		file.add_command(label="Apri evento", command=self.OpenEvent)


		# adds a command to the menu option, calling it exit, and the
		# command it runs on event is client_exit
		file.add_command(label="Uscita", command=self.client_exit)
		

		#added "file" to our menu
		menu.add_cascade(label="File", menu=file)


		# create the edit object)
		edit = Menu(menu)

		# adds a command to the menu option, calling it exit, and the
		# command it runs on event is client_exit
		edit.add_command(label="Show Img", command=self.showImg)
		edit.add_command(label="Show Text", command=self.showText)

		#added "file" to our menu
		menu.add_cascade(label="Edit", menu=edit)
	def showText(self):
		pass
	def showImg(self):
		load = Image.open("chat.png")
		render = ImageTk.PhotoImage(load)

		# labels can be text or images
		img = Label(self, image=render)
		img.image = render
		img.place(x=0, y=0)
		
	def sell_selections(self):
		print("Vendo posti selezionati")
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
			
			self.TotalPrice=Decimal('0.00')
			for wl in self.ASPriceLbl:
				self.TotalPrice+=Decimal(wl.cget('text'))
			self.ASTotalAmountLbl.config(text=self.TotalPrice)
			
			
			self.TotalFullPrice= 0
			self.TotalReducedPrice=0
			self.TotalFreePrice=0
			for w in self.ASPriceLstb:
				if w.curselection()[0]== FULL_PRICE:
					self.TotalFullPrice+=1
				elif w.curselection()[0]== REDUCED_PRICE:
					self.TotalReducedPrice+=1
				elif w.curselection()[0]== FREE_PRICE:
					self.TotalFreePrice+=1
			self.ASTotalFullPriceLbl.config(text=self.TotalFullPrice)
			self.ASTotalReducedPriceLbl.config(text=self.TotalReducedPrice)
			self.ASTotalFreePriceLbl.config(text=self.TotalFreePrice)
		
		# begin definition of window

		def ActSelTLBook():
			
			## booking_event data change for booking 
			"""
				self.ed['event']['booking_user']=data[4]
				self.ed['event']['booking_price']=data[5]
				self.ed['event']['booking_datetime']=data[6]
			"""
			users_tmp= self.ed['event']['booking_user'].split(',')
			price_tmp= self.ed['event']['booking_price'].split(',')
			datetime_tmp= self.ed['event']['booking_datetime'].split(',')
			for idx,seat in enumerate(self.SelectionBuffer):
				self.ed['seat_status'][seat]=BOOKED
				users_tmp[seat]= '2'
				price_tmp[seat]= str(self.ASPriceLstb[idx].curselection()[0])
				datetime_tmp[seat] = time.strftime('%Y-%m-%d %H:%M:%S')
				
			self.ed['event']['booking_status']=','.join(self.ed['seat_status'])
			self.ed['event']['booking_user']=','.join(users_tmp)
			self.ed['event']['booking_price']=','.join(price_tmp)
			self.ed['event']['booking_datetime']=','.join(datetime_tmp)
			
			del users_tmp,datetime_tmp
			
			sql_cmd = """UPDATE `booking_event` 
			SET `booking_status`='{}',
			`booking_user`='{}',
			`booking_price`='{}',`booking_datetime`='{}'
			WHERE `booking_event`.`id` = {};""".format(self.ed['event']['booking_status'],self.ed['event']['booking_user'],self.ed['event']['booking_price'],self.ed['event']['booking_datetime'],self.ed['event']['id'])
			
			
			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
			except:
				self.mysql.rollback()

			
			## booking_booking data get for insert new record

			self.ed['booking']['quantity']+=1
			created_date_tmp = time.strftime('%Y-%m-%d %H:%M:%S')
			seats_booked_tmp = ''
			for idx,seat in enumerate(self.SelectionBuffer):
				seats_booked_tmp+='{}${},'.format(self.seat_name[seat],price_tmp[idx])
			cstr_name = self.ASNameEnt.get()
			cstr_surname = self.ASSurnameEnt.get()
			cstr_email = self.ASEmailEnt.get()
			cstr_phone = self.ASPhoneEnt.get()
			event_tmp = self.ed['event']['id']
			
			self.EventDataChanged=True
			
			#INSERT INTO `booking_booking`(`id`, `created_date`, `seats_booked`, `customer_name`, `customer_surname`, `customer_email`, `event_id`, `user_id_id`, `customer_phone`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7],[value-8],[value-9])
			sql_cmd = """
			INSERT INTO `booking_booking`
			( `created_date`, `seats_booked`, `customer_name`, `customer_surname`, `customer_email`, `event_id`, `user_id_id`, `customer_phone`)
			VALUES ('{}','{}','{}','{}','{}',{},{},'{}')
			;
			""".format(created_date_tmp,seats_booked_tmp,cstr_name,cstr_surname,cstr_email,event_tmp,2,cstr_phone)
			print(sql_cmd)
			try:
				self.mysqlcursor.execute(sql_cmd)
				self.mysql.commit()
			except:
				self.mysql.rollback()
			finally:
				try:
					sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.ed['event']['id']))
					result=self.mysqlcursor.execute(sql_cmd)
					if result < 1:
						self.ed['booking']['quantity']=result	
					else:
						self.ed['booking']['quantity']=result
						for idx in range(result):  # @UnusedVariable
							data=self.mysqlcursor.fetchone()
							self.ed['booking'][str(data[0]).zfill(6)]=data	
							print(self.ed['booking'][str(data[0]).zfill(6)])
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
			if self.SelectionReset['state']==DISABLED:
				self.SelectionReset.config(state=NORMAL)
		
			self.ActSelTL.destroy()
		
		## DECLARE , INSTANTIATE AND POPULATE THE TOP LEVEL FRAME FOR SELL, BOOK
		## or other actions on the selected seats
		
		## LIST OF SEAT SELECTED , PRICES AND TYPES
		self.ActSelTL=Toplevel(  background='lavender', borderwidth=1, container = 0, height = 800,takefocus=True,  width=600)
		self.prices=[Decimal('0.00'),self.ed['event']['price_reduced'],self.ed['event']['price_full']]
		gridrow=1
		if mode == BOOK:
			self.ActSelTL.title("Finestra per la prenotazione dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')
			self.price=[self.prices[0] for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		elif mode == SELL:
			self.ActSelTL.title("Finestra per la vendita dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')
			self.price=[self.prices[0] for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		else:
			self.ActSelTL.title("Finestra per SPARE dei posti selezionati")
			self.ActSelTL.config(bg='khaki1')
			
		self.ASTitleLbl=Label(self.ActSelTL,text="Posti selezionati",font = LARGE_FONT)
		self.ASTitleLbl.grid(row=gridrow,column=1,columnspan=3,padx=(5,5),pady=(5,5))
		
		self.ASSeatLbl=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		self.ASPriceLstb=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		self.ASPriceLbl=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
# 		self.price=[0 for x in range(len(self.SelectionBuffer))]  # @UnusedVariable
		gridrow+=2
		for idx in range(len(self.SelectionBuffer)):
			self.ASSeatLbl[idx]=Label(self.ActSelTL,font=LARGE_FONT,text=self.seat_name[self.SelectionBuffer[idx]])
			self.ASSeatLbl[idx].grid(row=gridrow,column=1,columnspan=1,padx=(5,5),pady=(5,5))
			
			self.ASPriceLstb[idx]=Listbox(self.ActSelTL,selectmode=BROWSE)
			self.ASPriceLstb[idx].insert(END,"Gratuito")
			self.ASPriceLstb[idx].insert(END,"Ridotto")
			self.ASPriceLstb[idx].insert(END,"Intero")
			
			
	# 		self.EvChEventLbx.bind("<Double-Button-1>", self.ok)
			default_price=FULL_PRICE
			self.ASPriceLstb[idx].grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
			self.ASPriceLstb[idx].config(height=3,width=8,font=NORM_FONT,exportselection=False)
			self.ASPriceLstb[idx].select_set(default_price)
			self.ASPriceLstb[idx].bind('<<ListboxSelect>>', choose)
			
			self.ASPriceLbl[idx]=Label(self.ActSelTL,font=LARGE_FONT,text=self.prices[default_price])
			self.ASPriceLbl[idx].grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
			
			
			self.toggle_status(self.SelectionBuffer[idx], DISABLE)
			self.SelectionReset.config(state=DISABLED)
			
			gridrow+=1
			
		gridrow+=1
		self.ASTotalAmountTitle=Label(self.ActSelTL,font=LARGE_FONT,text="Totale prezzo ingressi")
		self.ASTotalAmountTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		
		self.TotalPrice= self.prices[default_price]*len(self.SelectionBuffer)
		
		
		self.ASTotalAmountLbl=Label(self.ActSelTL,font=LARGE_FONT,text=self.TotalPrice)
		self.ASTotalAmountLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
		
		gridrow+=2
		
		self.TotalFullPrice= 0
		self.TotalReducedPrice=0
		self.TotalFreePrice=0
		
		
		for w in self.ASPriceLstb:
			if w.curselection()[0]== FULL_PRICE:
				self.TotalFullPrice+=1
			elif w.curselection()[0]== REDUCED_PRICE:
				self.TotalReducedPrice+=1
			elif w.curselection()[0]== FREE_PRICE:
				self.TotalFreePrice+=1
				
		
		self.ASTotalFullPriceTitle=Label(self.ActSelTL,font=LARGE_FONT,text="Totale ingressi INTERI")
		self.ASTotalFullPriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalFullPriceLbl=Label(self.ActSelTL,font=LARGE_FONT,text=self.TotalFullPrice)
		self.ASTotalFullPriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
		gridrow+=1
		self.ASTotalReducedPriceTitle=Label(self.ActSelTL,font=LARGE_FONT,text="Totale ingressi RIDOTTI")
		self.ASTotalReducedPriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalReducedPriceLbl=Label(self.ActSelTL,font=LARGE_FONT,text=self.TotalReducedPrice)
		self.ASTotalReducedPriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))
		gridrow+=1
		self.ASTotalFreePriceTitle=Label(self.ActSelTL,font=LARGE_FONT,text="Totale ingressi GRATUITI")
		self.ASTotalFreePriceTitle.grid(row=gridrow,column=1,columnspan=2,padx=(5,5),pady=(5,5))
		self.ASTotalFreePriceLbl=Label(self.ActSelTL,font=LARGE_FONT,text=self.TotalFreePrice)
		self.ASTotalFreePriceLbl.grid(row=gridrow,column=3,columnspan=1,padx=(5,5),pady=(5,5))


		
		gridrow+=2
		self.ASBookBtn=Button(self.ActSelTL,font=LARGE_FONT,text='Conferma',state=NORMAL,
							width=6,activebackground='red',activeforeground='yellow',
							bg='green',fg='snow',command= ActSelTLBook)
		self.ASBookBtn.grid(row=gridrow,column=2,columnspan=1,padx=(5,5),pady=(5,5))
		self.ASexitBtn=Button(self.ActSelTL,font=LARGE_FONT,text='Esci',state=NORMAL,
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
			
			self.ASSurnameLbl=Label(self.ActSelTL,font=LARGE_FONT,width=10,text="Cognome")
			self.ASSurnameLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))
			
			gridrow+=1
			self.ASNameLbl=Label(self.ActSelTL,font=LARGE_FONT,width=10,text="Nome")
			self.ASNameLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow+=1
			self.ASEmailLbl=Label(self.ActSelTL,font=LARGE_FONT,width=10,text="Email")
			self.ASEmailLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow+=1
			self.ASPhoneLbl=Label(self.ActSelTL,font=LARGE_FONT,width=10,text="Telefono")
			self.ASPhoneLbl.grid(row=gridrow,column=4,columnspan=1,padx=(15,5),pady=(5,5))

			gridrow=1
			
			gridrow+=2
			
			self.ASSurnameEnt=Entry(self.ActSelTL,font=LARGE_FONT,width=30,text="Cognome")
			self.ASSurnameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
			
			gridrow+=1
			self.ASNameEnt=Entry(self.ActSelTL,font=LARGE_FONT,width=30,text="Nome")
			self.ASNameEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

			gridrow+=1
			self.ASEmailEnt=Entry(self.ActSelTL,font=LARGE_FONT,width=30,text="Email")
			self.ASEmailEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))

			gridrow+=1
			self.ASPhoneEnt=Entry(self.ActSelTL,font=LARGE_FONT,width=30,text="Telefono")
			self.ASPhoneEnt.grid(row=gridrow,column=5,columnspan=1,padx=(5,5),pady=(5,5))
		

		
	def toggle_status(self,idx,mode=None):
		if mode == SELECT:
			if idx not in self.SelectionBuffer:
				print('Selezionato posto {}.'.format(self.seat_name[idx]))
				self.btn[idx].config(relief=SUNKEN,bg='yellow')
				self.SelectionBuffer.append(idx)
				self.UpdateSelectionBufferText()
				# FLAT , RAISED, SUNKEN, GROOVE, RIDGE
			else:
				print('Posto {} gia selezionato. Nessuna azione'.format(self.seat_name[idx]))
		elif mode== DESELECT:
			self.RefreshSeats('one', idx)
		elif mode==DISABLE:
			self.btn[idx].config(state=DISABLED)
	
	def booking_code_window(self):
		self.booking_code_w = Toplevel(self)
		self.label = Label(self.booking_code_w, text="Prenotazione")
		self.label.pack(fill=X)
		self.booking_code = Entry(self.booking_code_w)
		self.booking_code.pack(fill=X)
		self.booking_code.focus_set()
		self.go= Button(self.booking_code_w,text="Procedi",command= self.insert_booking)
		self.go.pack(fill=X)
		
	def insert_booking(self):
		print(self.booking_code.get())
		self.booking_code_w.destroy()
		
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
			
			self.msg_w=MsgDialog(self,'Apertura evento',"Apro l'evento scelto")


			print("Evento scelto e in apertura = {}".format(self.event))
			if self.EventDataChanged:
				pass
			else:
				# query booking_event - heavy priority data
				# putting information on ed (event dictionary) in the inner event dictionary
				sql_cmd="SELECT * FROM booking_event where booking_event.id = {};".format(int(self.ev_id))
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.ed['event']['id']=data[0]
				self.ed['event']['creation_date']=data[1]
				self.ed['event']['event_date']=data[2]
				self.ed['event']['booking_status']=data[3]
				self.ed['event']['booking_user']=data[4]
				self.ed['event']['booking_price']=data[5]
				self.ed['event']['booking_datetime']=data[6]
				self.ed['event']['price_full']=data[7]
				self.ed['event']['price_reduced']=data[8]
				self.ed['event']['author_id']=data[9]
				self.ed['event']['show_id']=data[10]
				self.ed['event']['change']=data[11]
				print(self.ed['event'])
				
				# crea una list per uso diretto senza dover ripetere operazione di split tutte le volte
				self.ed['seat_status']=self.ed['event']['booking_status'].split(',')

				# query booking_show - low priority data
				# putting information on ed (event dictionary) in the inner show dictionary
				
				sql_cmd="SELECT * FROM booking_show where booking_show.id = {};".format(self.ed['event']['show_id'])
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.ed['show']['id']=data[0]
				self.ed['show']['company']=data[1]
				self.ed['show']['title']=data[2]
				self.ed['show']['text']=data[3]
				self.ed['show']['season_year_id']=data[4]
				self.ed['show']['debut_date']=data[5]
				self.ed['show']['director']=data[6]
				self.ed['show']['cast']=data[7]
				self.ed['show']['shw_code']=data[8]
				print(self.ed['show'])
				
				# query booking_bookingseason - low priority data
				# putting information on ed (event dictionary) in the inner season dictionary
				
				sql_cmd="SELECT * FROM booking_bookingseason where booking_bookingseason.id = {};".format(self.ed['show']['season_year_id'])
				self.mysqlcursor.execute(sql_cmd)
				data=self.mysqlcursor.fetchone()
				self.ed['season']['id']=data[0]
				self.ed['season']['label']=data[1]
				self.ed['season']['start_date']=data[2]
				self.ed['season']['end_date']=data[3]
				self.ed['season']['booking_enabled']=data[4]
				self.ed['season']['ssn_code']=data[5]
				print(self.ed['season'])	
				
				# query booking_booking - high priority data
				# putting information on ed (event dictionary) in the inner bookings dictionary
				
				sql_cmd="SELECT * FROM booking_booking where booking_booking.event_id = {};".format(int(self.ed['event']['id']))
				result=self.mysqlcursor.execute(sql_cmd)
				if result < 1:
					self.ed['booking']['quantity']=result	
				else:
					self.ed['booking']['quantity']=result
					for idx in range(result):  # @UnusedVariable
						data=self.mysqlcursor.fetchone()
						self.ed['booking'][str(data[0]).zfill(6)]=data	
						print(self.ed['booking'][str(data[0]).zfill(6)])
# 			sleep(5)						
			
			self.msg_w.close()
			## Main refresh of application data for event opening
			self.RefreshSeats(mode='full')
			self.RefreshEventInfo(mode='full')
			self.RefreshBooking(mode='full')
			self.session_open = True
												
								
				
				
				
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
				status=self.ed['seat_status'][idx]
				setseat(idx,status)
		elif mode=='one':
			status=self.ed['seat_status'][idx]
			setseat(idx,status)
				
	def RefreshEventInfo(self,mode=None):

		
		self.LblEvent_company.config(text="Compagnia: {}".format(self.ed['show']['company']))

		self.LblEvent_title.config(text="Titolo: {}".format(self.ed['show']['title']))
		
		date_aware=rome.localize(self.ed['event']['event_date']+timedelta(hours=2))		
		self.LblEvent_date.config(text="Data: {}".format(date_aware.strftime('%A, %d/%m/%y ')))
		
		self.LblEvent_time.config(text="Ora: {}".format(date_aware.strftime( '%H:%M')))
		
		self.LblEvent_price_full.config(text="Intero = {}".format(self.ed['event']['price_full']))
		
		self.LblEvent_price_reduced.config(text="Ridotto = {}".format(self.ed['event']['price_reduced']))

		self.LblEvent_season.config(text="Stagione Teatrale {}".format(self.ed['season']['label']))

		self.LblEvent_season_code.config(text="Codice {}".format(self.ed['season']['ssn_code']))

		self.LblEvent_show_code.config(text="Codice spettacolo = {}".format(self.ed['show']['shw_code']))
	
	def SelectEvent(self):
		pass
		

	def RefreshBooking(self, mode=None):
		if self.ed['booking']['quantity']:
			self.LblBookingCodeTitle= Label(self.FrameBooking,height = 1,width=8,font=SMALL_FONT,text="Codice")
			self.LblBookingCodeTitle.grid(row=2,column=1,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingSurnameTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Cognome")
			self.LblBookingSurnameTitle.grid(row=2,column=2,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingNameTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Nome")
			self.LblBookingNameTitle.grid(row=2,column=3,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingPhoneTitle= Label(self.FrameBooking,height = 1,width=15,font=SMALL_FONT,text="Telefono")
			self.LblBookingPhoneTitle.grid(row=2,column=4,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingDateTitle= Label(self.FrameBooking,height = 1,width=12,font=SMALL_FONT,text="Data")
			self.LblBookingDateTitle.grid(row=2,column=5,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			self.LblBookingSeatsTitle= Label(self.FrameBooking,height = 1,width=20,font=SMALL_FONT,text="Posti")
			self.LblBookingSeatsTitle.grid(row=2,column=6,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
			
			self.BtnBookingCode=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingSurname=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingName=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingPhone=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingDate=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			self.LblBookingSeats=[0 for x in range(self.ed['booking']['quantity'])]  # @UnusedVariable
			idx=0	
			for key,booking in sorted(self.ed['booking'].items()):
				if not key== 'quantity':
					self.BtnBookingCode[idx]= Button(self.FrameBooking,height = 1,width=8,
												font=SMALL_FONT,text=key,command = lambda code=key : self.GetBooking(code,mode=SELECT))
					self.BtnBookingCode[idx].grid(row=3+3*idx,column=1,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSurname[idx]= Label(self.FrameBooking,height = 1,width=15,
												font=SMALL_FONT,text=booking[4])
					self.LblBookingSurname[idx].grid(row=3+3*idx,column=2,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingName[idx]= Label(self.FrameBooking,height = 1,width=15,
												font=SMALL_FONT,text=booking[3])
					self.LblBookingName[idx].grid(row=3+3*idx,column=3,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingPhone[idx]= Label(self.FrameBooking,height = 1,width=15,
												font=SMALL_FONT,text=booking[8])
					self.LblBookingPhone[idx].grid(row=3+3*idx,column=4,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingDate[idx]= Label(self.FrameBooking,height = 1,width=12,
												font=SMALL_FONT,text=booking[1].strftime('%d/%m/%Y'))
					self.LblBookingDate[idx].grid(row=3+3*idx,column=5,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					self.LblBookingSeats[idx]= Label(self.FrameBooking,height = 3,width=20,
												font=SMALL_FONT,text=booking[2])
					self.LblBookingSeats[idx].grid(row=3+3*idx,column=6,padx=(0,0),pady=(0,0),columnspan=1,sticky=W)
					
					idx+=1
		else:
			self.LblBookingCodeTitle= Label(self.FrameBooking,height = 3,width=25,font=NORM_FONT,text="Non ci sono \nprenotazioni attive \nper questo evento")
			self.LblBookingCodeTitle.grid(row=2,column=1,padx=(0,0),pady=(0,0),columnspan=4,sticky=W)
	def GetBooking(self,code,mode=None):
		print("Elaboro la prenotazione codice {}".format(code))
		pass

	def client_exit(self):
		try:
			self.mysql.close()
			print("OK ---> MySQL connection closed!!!")
		except:
			print("OK ---> MySQL was not open. No action taken closing.")
		print("Shutting down GUI. Good bye. Come back soon!")
		exit()
		
if __name__ == '__main__':
	
	# La timezone UTC e' gia' pronta
	utc = pytz.utc
	
	# Crea una time zone
	rome = pytz.timezone("Europe/Rome")	
	
	# root window created. Here, that would be the only window, but
	# you can later have windows within windows.
	root = Tk()
	
	root.geometry("1380x900")
	
	#creation of an instance
	app = Window(root)
	
	
	#mainloop 
	root.mainloop() 
