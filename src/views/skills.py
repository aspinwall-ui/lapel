# coding: utf-8
"""
Code for the skills page.
"""
from gi.repository import Gtk, GLib

from ..daemon import get_daemon
from ..types.skill import SkillView

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/skills.ui')
class SkillsContent(Gtk.Box):
	"""List of installed skills."""
	__gtype_name__ = 'SkillsContent'

	skills_list = Gtk.Template.Child()
	search_bar = Gtk.Template.Child()
	search_entry = Gtk.Template.Child()

	in_search = False

	def __init__(self):
		"""Initializes a SkillsContent object."""
		self.daemon = get_daemon()

		self.daemon.client.on('mycroft.skills.list', self.set_skills)
		# UPSTREAM BUG: These are in the docs, but are never emitted, as MSM
		# has no connection to the bus.
		self.daemon.client.on('msm.install.succeeded', self.update_skills)
		self.daemon.client.on('msm.remove.succeeded', self.update_skills)

		self.daemon.client.on('mycroft.skills.loaded', self.update_skills)

		# Set up search bar
		self.search_bar.set_key_capture_widget(self)
		self.search_bar.connect_entry(self.search_entry)

		# Set up sort model
		self.sort_model = Gtk.SortListModel(model=self.daemon.skills)
		self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
		self.sort_model.set_sorter(self.sorter)

		# Set up filter model
		self.filter_model = Gtk.FilterListModel(model=self.sort_model)
		self.filter = Gtk.CustomFilter.new(self.filter_func, self.filter_model)
		self.filter_model.set_filter(self.filter)
		self.search_entry.connect('search-changed', self.search_changed)

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.setup_list_item)
		factory.connect('bind', self.bind_list_item)

		self.selection = Gtk.SingleSelection(model=self.filter_model)
		self.skills_list.set_model(self.selection)
		self.skills_list.set_factory(factory)

	def show_search(self, button, *args):
		if button.get_active():
			self.search_bar.set_search_mode(True)
		else:
			self.search_bar.set_search_mode(False)

	def setup_list_item(self, factory, list_item, *args):
		"""Sets up a list item."""
		list_item.set_child(SkillView())

	def bind_list_item(self, factory, list_item, *args):
		"""Binds a list item."""
		skill_view = list_item.get_child()
		skill = list_item.get_item()
		skill_view.bind_to_skill(skill)

	def set_skills(self, message):
		"""Sets the initial list of skills."""
		# This function is called as a result of receiving 'mycroft.skills.list',
		# which contains a dict with the skill IDs as the name, and the information
		# about the skill in the value.
		#
		# We send this information to LapelSkill, which has the necessary parsing
		# functions to get the full path, information and location of the skill.
		skills = message.data
		for skill_id, data in skills.items():
			self.daemon.add_skill(skill_id, data)

	def update_skills(self, message):
		"""
		Adds/removes a skill from the skills list based on whether it was
		installed or removed.
		"""
		if message.msg_type == 'msm.install.succeeded':
			self.daemon.add_skill(message.data['skill'])
		elif message.msg_type == 'msm.remove.succeeded':
			self.daemon.remove_skill(message.data['skill'])
		elif message.msg_type == 'mycroft.skills.loaded':
			self.daemon.add_skill(message.data['id'])

	def sort_func(self, a, b, *args):
		"""Custom sort function implementation for skills."""
		a_name = GLib.utf8_casefold(a.data['title'], -1)
		if not a_name:
			a_name = a.get_id()
		b_name = GLib.utf8_casefold(b.data['title'], -1)
		if not b_name:
			b_name = b.get_id()
		return GLib.utf8_collate(a_name, b_name)

	def filter_func(self, skill, *args):
		"""Custom filter for skill search."""
		query = self.search_entry.get_text()
		if not query:
			return True
		query = query.casefold()

		if query in skill.data['title'].casefold():
			return True

		if query in skill.data['category'].casefold():
			return True

		# for keyword in skill.data['tags']:
		# 	if query in keyword.casefold():
		# 		return True

		return False

	def search_changed(self, search_entry, *args):
		"""Emitted when the search has changed."""
		if search_entry.get_text():
			self.in_search = True
		else:
			self.in_search = False
			#self.no_results.set_visible(False)

		self.filter.changed(Gtk.FilterChange.DIFFERENT)

		#if self.filter_model.get_n_items() == 0:
		#	self.no_results.set_visible(True)
		#else:
		#	self.no_results.set_visible(False)

		# Select first item in list
		first_item = self.skills_list.get_first_child()
		if first_item:
			self.selection.set_selected(0)

		# Scroll back to top of list
		vadjust = self.skills_list.get_vadjustment()
		vadjust.set_value(vadjust.get_lower())
