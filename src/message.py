# coding: utf-8
"""
Code for storing information about messages.
"""
from gi.repository import Gtk, GObject
import time
import threading

from .wrappers import dialog_wrapper_for

class LapelMessage(GObject.Object):
	"""
	GObject wrapper for Mycroft messages.
	"""
	__gtype_name__ = 'LapelMessage'

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
		return self.message.msg_type

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def data(self):
		"""Message data."""
		return self.message.data

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/messageview.ui')
class MessageView(Gtk.ListBoxRow):
	"""
	GTK widget for displaying the data of a message contained in a
	LapelMessage object.
	"""
	__gtype_name__ = 'MessageView'

	message_date = Gtk.Template.Child()
	utterance_label = Gtk.Template.Child()
	dialog_wrapper = Gtk.Template.Child()

	def __init__(self, message=None, parent=None):
		"""
		Creates an empty MessageView. You can bind it to a LapelMessage
		with the MessageView.bind_to_message function.
		"""
		super().__init__()
		if message:
			self.bind_to_message(message)

		self.message_date = time

		if parent:
			self.parent = parent
			self.connect('realize', self.scroll_to_bottom)

	def scroll_to_bottom(self, *args):
		"""Scrolls the parent container to the bottom."""
		self.parent.scroll_to_bottom()

	def bind_to_message(self, message):
		"""Binds the MessageView to a message."""
		self.message = message
		self.message_date.set_label(time.strftime('%H:%M'))
		if message.type == 'recognizer_loop:utterance':
			self.is_sent()
			self.utterance_label.set_label(' '.join(message.data['utterances']))
			return
		else:
			self.is_received()
			self.utterance_label.set_label(message.data['utterance'])

		if message.data:
			if 'meta' in message.data.keys() and 'dialog' in message.data['meta'].keys():
				dialog = message.data['meta']['dialog']
				if dialog == 'unknown':
					self.utterance_label.add_css_class('error')
				self.set_wrapper(dialog_wrapper_for(dialog))

	def is_sent(self):
		"""
		Actions to perform when the message received contains information
		about a sent message.
		"""
		self.add_css_class('sent')
		self.set_halign(Gtk.Align.END)
		self.utterance_label.set_halign(Gtk.Align.END)
		self.message_date.set_halign(Gtk.Align.END)

	def is_received(self):
		"""
		Actions to perform when the message received contains information
		about a received message.
		"""
		self.add_css_class('received')
		self.set_halign(Gtk.Align.START)
		self.utterance_label.set_halign(Gtk.Align.START)
		self.message_date.set_halign(Gtk.Align.START)

	def set_wrapper(self, wrapper):
		"""Sets the dialog wrapper for the message."""
		if not wrapper:
			return None

		self.dialog_wrapper.set_visible(True)
		self.dialog_wrapper.set_child(wrapper)
