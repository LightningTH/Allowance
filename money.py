import sys, os
import cherrypy
import string
import datetime
import math
import db
import hashlib
import binascii
from i2clibraries import i2c_lcd_smbus
from RPi import GPIO
import time

global lcd

#main display entry
Headline = "Samantha's Money"

#password, following bit of code used to generate. Would be wise to use bcrypt but haven't swapped to it yet
#Password = "mypassword"
#for i in xrange(10):
#   Password = hashlib.sha1("money" + Password).digest()
#print binascii.b2a_hex(Password)
Password = binascii.a2b_hex("1234567890abcdef1234567890abcdef12345678")
	
#io port to watch for the doorbell button to activate display
DoorbellIO = 18

class Money:
	@cherrypy.expose
	def stop(self):
		global DoorbellIO
		GPIO.remove_event_detect(DoorbellIO)
		sys.exit(0)

	@cherrypy.expose
	def index(self, **params):
		global Headline
		global Password

		HTML = """
		<html>
		<body>
		<center>%s</center><br>
		""" % (Headline)

		HTMLFoot = """
		</body>
		</html>
		"""

		HTMLData = ""

		in_password = ""
		if("password" in params):
			in_password = params.pop("password")
			for i in xrange(10):
				in_password = hashlib.sha1("money" + in_password).digest()

		if(in_password == Password):
			if len(params):
				startdate = params["startdate"]
				enddate = params["enddate"]
				amount = params["amount"]

				try:
					Date = params["startdate"].split("/")
					NewDate = "%02d/%02d/%04d" % (int(Date[0]), int(Date[1]), int(Date[2]))
					startdate = datetime.datetime.strptime(NewDate, "%m/%d/%Y")
				except Exception, ex:
					return (HTML + "Error converting start date" + HTMLFoot)

				try:
					Date = params["enddate"].split("/")
					NewDate = "%02d/%02d/%04d" % (int(Date[0]), int(Date[1]), int(Date[2]))
					enddate = datetime.datetime.strptime(NewDate, "%m/%d/%Y")
				except Exception, ex:
					return (HTML + "Error converting end date" + HTMLFoot)

				try:
					amount = str("%0.2f" % (float(amount)))
				except:
					return (HTML + "Error reading amount" + HTMLFoot)

				db.execute(cherrypy.thread_data.conn,"insert into money(startdate, enddate, amount) values(datetime(?), datetime(?), ?)", (startdate.strftime("%Y-%m-%d 00:00"), enddate.strftime("%Y-%m-%d 00:00"), amount))
				HTMLData = HTMLData + "<center>Money updated</center><br>"
		elif(in_password != ""):
			HTMLData += "<center>Invalid password</center><br>"

		(ret, MoneyLines) = db.fetchAll(cherrypy.thread_data.conn,"select m.startdate [timestamp], m.enddate [timestamp], m.amount from money m order by m.startdate")
		HTMLData += "<form action='/' method='POST'>"
		HTMLData +=	"""
					<table border=0 align=center>
					<tr>
						<td>Start Date</td><td>End Date</td><td>Amount</td>
					</tr>
				"""

		TotalAmount = 0.0
		for (startdate, enddate, amount) in MoneyLines:
			HTMLData = HTMLData + "<tr><td>" + startdate.strftime("%m/%d/%Y") + "</td><td>" + enddate.strftime("%m/%d/%Y") + "</td><td>" + "%0.2f" % (amount) + "</td></tr>"
			TotalAmount += amount

		HTMLData += "<tr><td></td><td>Total</td><td>" + "%0.2f" % (TotalAmount) + "</td></tr>"
		HTMLData += "<tr><td>&nbsp;</td></tr>"

		startofweek = datetime.datetime.now()
		startofweek = startofweek - datetime.timedelta((startofweek.weekday() + 1) % 7)
		endofweek = startofweek  + datetime.timedelta(7)
		HTMLData = HTMLData + """
					<tr><td><input type=text size=10 name=startdate value='%s'></td><td><input type=text size=10 name=enddate value='%s'></td><td><input type=text size=4 name=amount value='%s'></td>
					<tr><td>&nbsp;</td></tr>
					<tr>
						<td>Password:</td>
						<td><input type='password' name='password'></td>
					</tr>
					<tr>
						<td colspan=3 align=left><input type='submit' value="Submit"></td>
					</tr>
				</table>
			</form>
			""" % (startofweek.strftime("%m/%d/%Y"), endofweek.strftime("%m/%d/%Y"), "1.00")

		UpdateLCD()
		return HTML + HTMLData + HTMLFoot

def UpdateLCD():
	global lcd
	(ret, row) = db.fetchOne(cherrypy.thread_data.conn,"select sum(amount) from money")
	(Amount,) = row
	lcd.clear()
	lcd.home()
	lcd.writeString("Samantha's Money")
	lcd.setPosition(2, 0)
	lcd.writeString("%0.2f" % (Amount))

def handle_errors():
	cherrypy.response.status=500
	cherrypy.response.body = ['<html><body>An error occurred</body></html>']

def error_page(status, message, traceback, version):
	return "<html><body>An error occurred:" + message + "<br>" + traceback + "</body></html>"

def TurnOnDisplay(channel):
	global lcd
	lcd.backLightOn()
	time.sleep(3)
	lcd.backLightOff()

def make_connect(thread_index):
	global lcd, DoorbellIO

	cherrypy.thread_data.conn = db.make_connect()
	lcd = i2c_lcd_smbus.i2c_lcd(0x3f, 1, 2, 1, 0, 4, 5, 6, 7, 3)
	cherrypy.thread_data.lcd = lcd

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(DoorbellIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(DoorbellIO, GPIO.FALLING, callback=TurnOnDisplay, bouncetime=1000)

	UpdateLCD()
	TurnOnDisplay(DoorbellIO)
	
current_dir = os.path.dirname(os.path.abspath(__file__))
config = {
	'/':
	{
		'tools.trailing_slash.on': False,
		'tools.sessions.on': True,
		'tools.sessions.storage_type': 'ram',
		'tools.sessions.timeout': 60,
		'tools.sessions.name': 'Money',
	},
}
cherrypy.tree.mount(Money(), "/", config=config)

cherrypy.config.update({
		'request.error_response': handle_errors,
		'error_page.default': error_page,
		'server.socket_host': '',
		'server.socket_port': 80})

cherrypy.engine.subscribe('start_thread',make_connect)
cherrypy.server.start()
