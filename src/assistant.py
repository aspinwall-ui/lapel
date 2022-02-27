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
		self.store = get_daemon().messages

		self.message_list.bind_model(self.store, self.create_message_view, None)

	def create_message_view(self, message, *args):
		self.message_list.append(MessageView(message))
