# coding: utf-8
"""
Main window creation code.
"""
import sys
import gi

gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')

from gi.repository import Adw, Gtk, Gio

@Gtk.Template(resource_path='/org/dithernet/lapel/window.ui')
class LapelWindow(Adw.ApplicationWindow):
	"""Main window for the program."""
	__gtype_name__ = 'LapelWindow'

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

@Gtk.Template(resource_path='/org/dithernet/lapel/about.ui')
class AboutDialog(Gtk.AboutDialog):
	"""Main about dialog for Assistant."""
	__gtype_name__ = 'AboutDialog'

	def __init__(self, parent):
		Gtk.AboutDialog.__init__(self)
		self.props.version = "0.1.0"
		self.set_transient_for(parent)

class Application(Adw.Application):
	def __init__(self):
		super().__init__(
			application_id='org.dithernet.lapel',
			flags=Gio.ApplicationFlags.FLAGS_NONE
		)

	def do_activate(self):
		win = self.props.active_window
		if not win:
			win = LapelWindow(application=self)
		self.create_action('about', self.on_about_action)
		win.present()

	def on_about_action(self, widget, _):
		about = AboutDialog(self.props.active_window)
		about.present()

	def on_preferences_action(self, widget, _):
		print('app.preferences action activated')

	def create_action(self, name, callback):
		"""Add an action and connect it to a callback."""
		action = Gio.SimpleAction.new(name, None)
		action.connect("activate", callback)
		self.add_action(action)

def main(version):
	app = Application()
	return app.run(sys.argv)
