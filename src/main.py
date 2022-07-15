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
from .views.popup import AssistantPopup
from .window import LapelWindow, AboutDialog

class Application(Adw.Application):
	win = None
	assistant_popup = None

	def __init__(self):
		super().__init__(
			application_id='org.dithernet.lapel',
			flags=Gio.ApplicationFlags.FLAGS_NONE,
			resource_base_path='/org/dithernet/lapel/'
		)

	def do_activate(self):
		# FIXME: get_is_remote doesn't work sometimes? checking for self.win
		# is a workaround for that
		if not self.get_is_remote() and not self.win:
			if not get_daemon():
				start_daemon()
			self.daemon = get_daemon()

			if not self.assistant_popup:
				self.assistant_popup = AssistantPopup(self)

				# HACK: without this, showing the window results in:
				# gdk_gl_context_make_current() failed
				self.assistant_popup.present()
				self.assistant_popup.hide()

			# Keep running in the background
			self.hold()

		self.show_window()

	def show_window(self, *args):
		active_window = self.get_active_window()
		if active_window and type(active_window) == LapelWindow:
			active_window.present()
			return

		if not self.win:
			self.win = LapelWindow(application=self)
			self.win.connect('close-request', self.close_window)

		self.create_action('about', self.on_about_action)
		self.create_action('preferences', self.on_preferences_action)
		self.create_action('quit', self.on_quit_action)
		self.win.present()

	def close_window(self, *args):
		self.win = None
		return False

	def on_about_action(self, widget, _):
		about = AboutDialog(self.props.active_window)
		about.present()

	def on_preferences_action(self, widget, _):
		preferences = LapelPreferences()
		preferences.present()

	def on_quit_action(self, widget, _):
		for window in self.get_windows():
			window.close()
		self.release()
		self.quit()

	def create_action(self, name, callback):
		"""Add an action and connect it to a callback."""
		action = Gio.SimpleAction.new(name, None)
		action.connect("activate", callback)
		self.add_action(action)

def main(version):
	app = Application()
	return app.run(sys.argv)
