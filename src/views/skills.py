# coding: utf-8
"""
Code for the skills page.
"""
from gi.repository import Gtk

from ..daemon import get_daemon
from ..types.skill import SkillView

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/skills.ui')
class SkillsContent(Gtk.Box):
	"""Box that shows the microphone volume when speaking to Mycroft."""
	__gtype_name__ = 'SkillsContent'

	skills_list = Gtk.Template.Child()

	def __init__(self):
		"""Initializes a SkillsContent object."""
		self.daemon = get_daemon()

		self.daemon.client.on('mycroft.skills.list', self.set_skills)
		# FIXME: It seems that these two are never broadcast. Investigate
		self.daemon.client.on('msm.install.succeeded', self.update_skills)
		self.daemon.client.on('msm.remove.succeeded', self.update_skills)

		self.daemon.client.on('mycroft.skills.loaded', self.update_skills)

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.setup_list_item)
		factory.connect('bind', self.bind_list_item)

		self.skills_list.set_model(Gtk.SingleSelection(model=self.daemon.skills))
		self.skills_list.set_factory(factory)

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
