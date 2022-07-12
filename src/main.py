# coding: utf-8
"""
Main application creation code.
"""
import sys
import gi

gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')

from gi.repository import Adw, Gio
from .daemon import start_daemon, get_daemon

from .views.preferences import LapelPreferences
from .window import LapelWindow, AboutDialog

class Application(Adw.Application):
	def __init__(self):
		super().__init__(
			application_id='org.dithernet.lapel',
			flags=Gio.ApplicationFlags.FLAGS_NONE,
			resource_base_path='/org/dithernet/lapel/'
		)
		start_daemon()

	def do_activate(self):
		win = self.props.active_window
		if not win:
			win = LapelWindow(application=self)
		self.create_action('about', self.on_about_action)
		self.create_action('preferences', self.on_preferences_action)
		self.daemon = win.daemon
		win.present()

	def on_about_action(self, widget, _):
		about = AboutDialog(self.props.active_window)
		about.present()

	def on_preferences_action(self, widget, _):
		preferences = LapelPreferences()
		preferences.present()

	def create_action(self, name, callback):
		"""Add an action and connect it to a callback."""
		action = Gio.SimpleAction.new(name, None)
		action.connect("activate", callback)
		self.add_action(action)

def main(version):
	app = Application()
	return app.run(sys.argv)
