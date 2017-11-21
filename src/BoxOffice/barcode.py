from escpos.printer import Usb
from escpos import *
from time import sleep

# Adapt to your needs
p = Usb(0x0471, 0x0055,timeout=0,in_ep=0x82, out_ep=0x02)
#~ p = escpos.Escpos(0x0471, 0x0055,0)
# Print software and then hardware barcode with the same content
# p.soft_barcode('code39', '123456')

for idx in range(1):
	p.set(align='center', font='b',  width=2, height=2)
	p.text('Ricevuta numero {}\n'.format(idx+1))
	p.text('\n')
	p.text('Hello world\n')
	p.image('chat.png')
	p.text('Boxoffice LTC\n')
	p.barcode('123456', 'CODE39')
#~ p.print_and_feed(n=2)
	p.text('\n')
	p.qr("Prenotazione 00056")
	p.text('\n')

	sleep(1)
	p.cut(mode=u'FULL')
