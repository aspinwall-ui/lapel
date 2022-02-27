# coding: utf-8
"""
Code for the assistant view.
"""
from gi.repository import Gtk

from .daemon import get_daemon
from .message import MessageView

@Gtk.Template(resource_path='/org/dithernet/lapel/assistant.ui')
class AssistantContent(Gtk.Box):
	"""Main window for the program."""
	__gtype_name__ = 'AssistantContent'

	message_list = Gtk.Template.Child()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.store = get_daemon().messages

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.message_setup)
		factory.connect('bind', self.message_bind)

		self.message_list.set_model(Gtk.SingleSelection(model=self.store))
		self.message_list.set_factory(factory)

	def message_setup(self, factory, list_item):
		list_item.set_child(MessageView())

	def message_bind(self, factory, list_item):
		message = list_item.get_item()
		list_item.get_child().bind_to_message(message)
