# coding: utf-8
"""
Common wrappers.
"""
from mycroft_bus_client import Message
from gi.repository import Gtk

class DialogWrapper(Gtk.Box):
	"""
	GTK widget that shows options for a Mycroft skill dialog.
	"""
	__gtype_name__ = 'DialogWrapper'

	def __init__(self, message):
		"""Initializes a DialogWrapper."""
		super().__init__()
		self.message = message

class SuggestionWrapper(DialogWrapper):
	"""
	DialogWrapper widget that provides suggestion buttons.
	"""
	def __init__(self, message):
		"""Initializes a SuggestionWrapper."""
		super().__init__(message)
		# Imported here to avoid dependency loop
		from ..daemon import get_daemon
		self.daemon = get_daemon()
		self.daemon.on('speak', self.hide_buttons)
		self.daemon.on('recognizer_loop:utterance', self.hide_buttons)

		self.button_revealer = Gtk.Revealer(reveal_child=True, hexpand=True)

		scroll = Gtk.ScrolledWindow(hexpand=True)
		scroll.set_policy(
			Gtk.PolicyType.AUTOMATIC,
			Gtk.PolicyType.NEVER
		)

		self.buttons = Gtk.Box(spacing=6)
		scroll.set_child(self.buttons)

		self.button_revealer.set_child(scroll)
		self.append(self.button_revealer)

	def add_button(self, answer, label=None):
		"""Adds a button to the SuggestionWrapper."""
		if not label:
			label = answer

		button = Gtk.Button(label=label)
		button.connect('clicked', self.do_suggestion, answer)
		button.add_css_class('pill')
		button.add_css_class('suggestion-button')
		self.buttons.append(button)

	def do_suggestion(self, button, answer):
		"""Sends a message from a suggestion."""
		self.daemon.client.emit(Message('active_skill_request'))
		self.daemon.send_message(answer, reply_to=self.message)
		self.hide_buttons()

	def hide_buttons(self, *args):
		"""Hides the buttons."""
		self.button_revealer.set_reveal_child(False)

class ConfirmDialog(SuggestionWrapper):
	"""
	SuggestionWrapper with Confirm and Cancel buttons.
	"""
	def __init__(self, message):
		super().__init__(message)
		# TRANSLATORS: "Confirm" button, used for Confirm/Cancel dialogs
		self.add_button(_('Confirm').lower(), _('Confirm'))
		# TRANSLATORS: "Cancel" button, used for Confirm/Cancel dialogs
		self.add_button(_('Cancel').lower(), _('Cancel'))
