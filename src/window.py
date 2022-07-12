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

		self.daemon.bind_property(
			'available', self.no_connection, 'reveal-child',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.daemon.bind_property(
			'available', self.no_connection, 'receives-default',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.daemon.bind_property(
			'available', self.no_connection, 'can-target',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.daemon.bind_property(
			'available', self.view_switcher, 'sensitive',
			GObject.BindingFlags.SYNC_CREATE
		)
		self.daemon.bind_property(
			'available', self.content_stack, 'sensitive',
			GObject.BindingFlags.SYNC_CREATE
		)

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
		self.assistant_page.get_child().content_flap.set_reveal_flap(False)

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/about.ui')
class AboutDialog(Gtk.AboutDialog):
	"""Main about dialog for Assistant."""
	__gtype_name__ = 'AboutDialog'

	def __init__(self, parent):
		Gtk.AboutDialog.__init__(self)
		self.props.version = "0.1.0"
		self.set_transient_for(parent)
