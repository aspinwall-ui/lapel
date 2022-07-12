# coding: utf-8
"""
Code for the assistant popup.
"""
from gi.repository import Adw, Gtk
from ..daemon import get_daemon

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/popup.ui')
class AssistantPopup(Adw.Window):
	"""Popup window that appears when Mycroft hears its wakeword."""
	__gtype_name__ = 'AssistantPopup'

	flap = Gtk.Template.Child()

	def __init__(self, app):
		super().__init__()
		self.app = app
		self.flap.connect('notify::reveal-progress', self.handle_reveal_progress)
		self.daemon = get_daemon()
		self.daemon.on('mycroft.mic.listen', self._show)
		self.daemon.on('recognizer_loop:record_end', self._hide)

	def _show(self, *args):
		active_window = self.app.get_active_window()
		if active_window and active_window.get_visible():
			return

		self.set_visible(True)
		self.present()
		self.fullscreen()
		self.flap.set_reveal_flap(True)

	def _hide(self, *args):
		self.flap.set_reveal_flap(False)

	def handle_reveal_progress(self, flap, *args):
		progress = flap.get_reveal_progress()
		if progress == 0:
			self.set_visible(False)
			self.daemon.stop_record()

	def close(self, *args):
		# stub
		pass
