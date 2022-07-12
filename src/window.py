# coding: utf-8
"""
Main window creation code.
"""
from gi.repository import Adw, Gtk, GObject

from .views.assistant import AssistantContent # noqa: F401
from .views.skills import SkillsContent # noqa: F401
from .views.pair import LapelPairingDialog
from .daemon import get_daemon

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/window.ui')
class LapelWindow(Adw.ApplicationWindow):
	"""Main window for the program."""
	__gtype_name__ = 'LapelWindow'

	content_stack = Gtk.Template.Child()
	skill_search_button = Gtk.Template.Child()
	assistant_page = Gtk.Template.Child()

	no_connection = Gtk.Template.Child()
	no_connection_status = Gtk.Template.Child()

	skills_content = Gtk.Template.Child()
	view_switcher = Gtk.Template.Child()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.daemon = get_daemon()
		if not self.daemon.is_paired():
			LapelPairingDialog(parent=self).present()

		self.daemon.client.on('error', self.handle_error)
		self.daemon.client.on('mycroft.ready', self.ready)
		self.no_connection.hide()

		self.daemon.refresh_skills()

		self.content_stack.connect('notify::visible-child', self.show_search_icon)
		self.skill_search_button.bind_property(
			'active',
			self.skills_content.search_bar, 'search-mode-enabled',
			flags=GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
		)

	def show_search_icon(self, *args):
		"""
		Shows/hides the search icon based on whether the skill list is shown or not.
		"""
		if self.content_stack.get_visible_child_name() == 'skills':
			vadjust = self.skills_content.skills_list.get_vadjustment()
			vadjust.set_value(vadjust.get_lower())
			self.skill_search_button.set_visible(True)
		else:
			self.skills_content.selection.set_selected(0)
			self.skill_search_button.set_visible(False)
			self.skill_search_button.set_active(False)

	def handle_error(self, error):
		"""Handles errors."""
		print(error)
		self.no_connection.show()
		self.no_connection.set_reveal_child(True)
		self.assistant_page.get_child().content_flap.set_reveal_flap(False)
		self.view_switcher.set_sensitive(False)

	def ready(self, *args):
		"""Recovers after an error."""
		self.no_connection.set_receives_default(False)
		self.no_connection.set_reveal_child(False)
		self.no_connection.hide()
		self.view_switcher.set_sensitive(True)
		self.daemon.refresh_skills()

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/about.ui')
class AboutDialog(Gtk.AboutDialog):
	"""Main about dialog for Assistant."""
	__gtype_name__ = 'AboutDialog'

	def __init__(self, parent):
		Gtk.AboutDialog.__init__(self)
		self.props.version = "0.1.0"
		self.set_transient_for(parent)
