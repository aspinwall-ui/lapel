# coding: utf-8
"""
Contains code for the message bus daemon.
"""
from mycroft_bus_client import MessageBusClient, Message
from gi.repository import Gio, GObject

from .message import LapelMessage

daemon = None

class MessageBusDaemon:
	"""
	Convenience class that sets up the MessageBus handler and its
	callbacks.
	"""
	def __init__(self):
		"""Sets up the MessageBus handler."""
		self.client = MessageBusClient()
		self.client.run_in_thread()

		self.messages = Gio.ListStore(item_type=LapelMessage)

		self.client.on('speak', self.to_message)
		self.client.on('recognizer_loop:utterance', self.to_message)

	def to_message(self, message):
		"""
		Turns the provided Message to a LapelMessage and adds it to the daemon's
		message list.
		"""
		self.messages.append(LapelMessage(message))

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
