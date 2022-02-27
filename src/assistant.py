# coding: utf-8
"""
Code for the assistant view.
"""
from gi.repository import Gtk

from .daemon import get_daemon
from .message import MessageView

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/assistant.ui')
class AssistantContent(Gtk.Box):
	"""Main window for the program."""
	__gtype_name__ = 'AssistantContent'

	message_list = Gtk.Template.Child()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.daemon = get_daemon()
		self.store = self.daemon.messages

		self.message_list.bind_model(self.store, self.create_message_view, None)

	def create_message_view(self, message, *args):
		self.message_list.append(MessageView(message))

	@Gtk.Template.Callback()
	def send_message(self, entry, *args):
		"""Sends the message from the entry."""
		self.daemon.send_message(entry.get_text())
		entry.set_text('')

	@Gtk.Template.Callback()
	def start_record(self, *args):
		"""Starts to record the voice for voice recognition."""
		self.daemon.start_record()
