# coding: utf-8
"""
Code for storing information about messages.
"""
from gi.repository import Gtk, GObject

class LapelMessage(GObject.Object):
	"""
	GObject wrapper for Mycroft messages.
	"""
	__gtype_name__ = 'Message'

	def __init__(self, message):
		"""Initializes a LapelMessage object."""
		super().__init__()
		self.message = message

	def to_mycroft_message(self):
		"""Returns the Mycroft message stored by the LapelMessage object."""
		return self.message

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def type(self):
		"""Type of message."""
		return self.message.type

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def data(self):
		"""Message data."""
		return self.message.data

class MessageView(Gtk.Box):
	"""
	GTK widget for displaying the data of a message contained in a
	LapelMessage object.
	"""
	__gtype_name__ = 'MessageView'

	def __init__(self, message=None):
		"""
		Creates an empty MessageView. You can bind it to a LapelMessage
		with the MessageView.bind_to_message function.
		"""
		super().__init__()
		if message:
			self.bind_to_message(message)

	def bind_to_message(self, message):
		"""Binds the MessageView to a message."""
		print(message)
		self.append(Gtk.Label(label=message.data['utterance']))
