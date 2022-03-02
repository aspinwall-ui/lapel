# coding: utf-8
"""
Code for the assistant view.
"""
from gi.repository import Gtk
import sys

from .daemon import get_daemon
from .message import MessageView

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/speechview.ui')
class SpeechView(Gtk.Box):
	"""Box that shows the microphone volume when speaking to Mycroft."""
	__gtype_name__ = 'SpeechView'

	@Gtk.Template.Callback()
	def close(self, *args):
		self.get_parent().set_reveal_flap(False)
		get_daemon().stop_record()

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/assistant.ui')
class AssistantContent(Gtk.Box):
	"""Main window for the program."""
	__gtype_name__ = 'AssistantContent'

	content_flap = Gtk.Template.Child()
	message_list = Gtk.Template.Child()
	scroll_down_button = Gtk.Template.Child()

	speech_view = Gtk.Template.Child()

	input_container = Gtk.Template.Child()
	input_entry = Gtk.Template.Child()

	vadjustment = Gtk.Template.Child()
	prev_upper = 0

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.daemon = get_daemon()
		self.daemon.client.on('recognizer_loop:wakeword', self.start_record)
		self.daemon.client.on('recognizer_loop:record_end', self.speech_timeout)
		self.store = self.daemon.messages

		self.message_list.bind_model(self.store, self.create_message_view, None)
		self.message_list.set_adjustment(self.vadjustment)

		self.input_entry.set_icon_from_icon_name(
			Gtk.EntryIconPosition.SECONDARY,
			'document-send-symbolic'
		)
		self.input_entry.connect('icon-release', self.send_message)
		self.content_flap.connect('notify::reveal-flap', self.speech_flap_closed)

	def create_message_view(self, message, *args):
		self.content_flap.set_reveal_flap(False)
		return MessageView(message, self)

	def speech_timeout(self, *args):
		self.content_flap.set_reveal_flap(False)

	def speech_flap_closed(self, *args):
		"""Stops recording mode."""
		if self.content_flap.get_reveal_flap() is False:
			self.daemon.stop_record()

	@Gtk.Template.Callback()
	def send_message(self, entry, *args):
		"""Sends the message from the entry."""
		text = entry.get_text()
		if text:
			self.daemon.send_message(text)
			entry.set_text('')

	@Gtk.Template.Callback()
	def start_record(self, *args):
		"""Starts to record the voice for voice recognition."""
		self.content_flap.set_reveal_flap(True)
		self.daemon.start_record()

	@Gtk.Template.Callback()
	def list_page_size_changed(self, adjustment, *args):
		"""Callback for the scroll view adjustment."""
		size = adjustment.get_page_size()
		value = adjustment.get_value()
		upper = adjustment.get_upper()

		prev_upper = self.prev_upper
		self.prev_upper = upper

		if prev_upper < upper:
			return

		if (upper - size) <= sys.float_info.epsilon:
			return

		if (upper - value) < size * 1.15:
			adjustment.set_value(upper)

		self.list_adjustment_value_changed(adjustment)

	@Gtk.Template.Callback()
	def list_adjustment_value_changed(self, adjustment, *args):
		"""Callback for the scroll view adjustment."""
		size = adjustment.get_page_size()
		value = adjustment.get_value()
		upper = adjustment.get_upper()

		if (upper - value) > size + 1.0:
			self.scroll_down_button.set_visible(True)
		else:
			self.scroll_down_button.set_visible(False)

		if size < 0.1:
			self.scroll_down_button.hide()

	@Gtk.Template.Callback()
	def scroll_to_bottom(self, *args):
		"""Scrolls to the bottom of the message list."""
		self.vadjustment.set_value(self.vadjustment.get_upper())
		self.scroll_down_button.hide()
