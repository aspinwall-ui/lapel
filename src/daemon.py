# coding: utf-8
"""
Contains code for the message bus daemon.
"""
from mycroft.util.signal import create_signal
from mycroft_bus_client import MessageBusClient, Message
from gi.repository import Gio
import threading

from .types.message import LapelMessage
from .types.skill import LapelSkill
from .config import config

daemon = None

class MessageBusDaemon:
	"""
	Convenience class that sets up the MessageBus handler and its
	callbacks.
	"""
	error_handler_func = None

	def __init__(self):
		"""Sets up the MessageBus handler."""
		self.client = MessageBusClient(host=config['websocket-address'], port=config['websocket-port'])
		self.client.run_in_thread()

		self.messages = Gio.ListStore(item_type=LapelMessage)
		self.skills = Gio.ListStore(item_type=LapelSkill)

		self.client.on('speak', self.to_message)
		self.client.on('recognizer_loop:utterance', self.to_message)

	def start_record(self):
		"""Starts recording the message for voice recognition."""
		self.client.emit(Message('mycroft.mic.listen'))

	def stop_record(self):
		"""Stops recording the current voice recognition message."""
		self.client.emit(Message('mycroft.stop'))
		create_signal('buttonPress')

	def to_message(self, message):
		"""
		Turns the provided Message to a LapelMessage and adds it to the daemon's
		message list.
		"""
		print(message, message.msg_type, message.data, message.context)
		self.messages.append(LapelMessage(message))

	def _send_message(self, message, reply_to=None):
		"""Sends a text message to the daemon."""
		if not reply_to:
			self.client.emit(Message('recognizer_loop:utterance',
				{"utterances": [message], "lang": 'en-us'})
			)
		else:
			try:
				context = {"source": reply_to.context["destination"],
					"destination": reply_to.context["source"]}
			except KeyError:
				context = {}
			self.client.emit(Message('recognizer_loop:utterance',
				{"utterances": [message], "lang": 'en-us'}, context
			))

	def send_message(self, message, reply_to=None):
		"""Starts a thread to send a text message to the daemon."""
		send_thread = threading.Thread(target=self._send_message,
			args=[message, reply_to]
		)
		send_thread.start()

	def set_error_handler(self, handler):
		"""Sets the function to be called when an error occurs."""
		self.error_handler_func = handler

	# Skills
	def refresh_skills(self, *args):
		"""Sends a signal to refresh the skills list."""
		if self.skills.get_n_items() > 0:
			self.skills.remove_all()
		t = threading.Thread(target=self.client.emit, args=[Message('skillmanager.list')])
		t.start()

	def add_skill(self, skill_id, data=None):
		"""Adds a skill to the skill store."""
		self.skills.append(LapelSkill(skill_id, data))

	def remove_skill(self, skill_id):
		"""Removes a skill from the skill store."""
		skills = list(self.skills)
		for skill in skills:
			if skill.id == skill_id:
				self.skills.remove(skill)
				return

def get_daemon():
	"""Returns the currently running MessageBus handler."""
	global daemon
	return daemon

def start_daemon():
	"""Starts a MessageBusDaemon."""
	global daemon
	if daemon:
		print("Message bus daemon already exists")
		return
	else:
		daemon = MessageBusDaemon()
