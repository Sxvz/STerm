from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import serial

class STermApp(App):
	connected = False
	ser = serial.Serial()
	memory = 100

	def build(self):
		layout = BoxLayout(orientation='vertical')
		sendPanel = BoxLayout(orientation='horizontal',  size=(200,30), size_hint=(1, None))
		sendBtn = Button(text='Send', size_hint=(0.2, 1))
		sendBtn.bind(on_press=self.send)
		input = TextInput(multiline=False)
		input.bind(on_text_validate=self.send)
		input.bind(focus=self.focusHandler)
		input.focus = True
		screen = TextInput(readonly=True, is_focusable=False)
		sendPanel.add_widget(input)
		sendPanel.add_widget(sendBtn)
		layout.add_widget(screen)
		layout.add_widget(sendPanel)
		self.sendBtn = sendBtn
		self.input = input
		self.screen = screen
		
		Clock.schedule_interval(self.update, 1.0/60.0)
		
		return layout
		
	def focusHandler(self, instance, value):
		if not value:
			self.input.focus = True

	def send(self, arg):
		text = self.input.text
		if text != '':
			if self.handleCommand(text):
				if self.ser.is_open:
					self.screen.text += '<< ' + text + '\n'
				else:
					self.screen.text += 'not connected --- use \'connect <port> [baudrate]\' to connect\n'
			self.input.text = ''

	def update(self, dt):
		if self.connected:
			if self.ser.inWaiting() > 0:
				self.screen.text += '>> ' + self.ser.readline()
				self.ser.reset_input_buffer()
				
		parts = self.screen.text.split('\n')
		if len(parts) > self.memory:
			parts = parts[1:]
			txt = ''
			for part in parts:
				if part != '':
					txt += part + '\n'
			self.screen.text = txt
		
		pass
	
	def handleCommand(self, c):
		parts = c.split()
		ser = self.ser
		if parts[0] == 'connect':
			if (len(parts) < 2) or (len(parts) > 3):
				self.screen.text += 'usage: \'connect <port> [baudrate]\'\n'
				return False
			try:
				ser.port = parts[1]
				if len(parts) == 2:
					ser.baudrate = 9600
				else:
					ser.baudrate = parts[2]
				ser.open()
				self.screen.text += 'connected to ' + parts[1] + '\n'
				self.connected = True
			except Exception:
				self.screen.text += 'failed to connect to ' + parts[1] + '\n'
		elif parts[0] == 'disconnect':
			if ser.is_open:
				self.connected = False
				ser.close()
				self.screen.text += 'disconnected from ' + ser.name + '\n'
		elif parts[0] == 'clear':
			self.screen.text = ''
		elif parts[0] == 'help':
			self.screen.text += 'available commands:\n  connect\n  disconnect\n  clear\n  help\n'
		else:
			return True
			
		return False
		
STermApp().run()