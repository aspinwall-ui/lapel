# coding: utf-8
"""
Contains code for handling skills.
"""
from mycroft.configuration import Configuration
from gi.repository import Gtk, GObject
import os.path
import re
import threading
import xdg

mycroft_config = None
mycroft_config_set = False

# Getting the config takes a while, and locks up the application.
# Run this in a thread to avoid this.

def set_config_func():
	"""Gets the Mycroft config and stores it in a global variable."""
	global mycroft_config
	global mycroft_config_set
	mycroft_config = Configuration.get()
	mycroft_config_set = True

if not mycroft_config_set:
	set_config_thread = threading.Thread(target=set_config_func)
	set_config_thread.start()

def skill_id_to_path(skill_id):
	"""
	Takes a skill ID and tries to find its path.
	Derived from mycroft.util.resolve_resource_file.
	"""
	global mycroft_config
	global mycroft_config_set

	# Look in XDG_DATA_DIRS
	for conf_dir in xdg.BaseDirectory.load_data_paths('mycroft'):
		filename = os.path.join(conf_dir, 'skills', skill_id)
		if os.path.isdir(filename):
			return filename

	# Look in old user location
	filename = os.path.join(os.path.expanduser('~'), '.mycroft', 'skills', skill_id)
	if os.path.isdir(filename):
		return filename

	# Get global dir
	if mycroft_config_set:
		data_dir = os.path.join(os.path.expanduser(mycroft_config['data_dir']), 'skills')
	else:
		# Just assume /opt/mycroft for now
		data_dir = os.path.join('opt', 'mycroft', 'skills')
	filename = os.path.expanduser(os.path.join(data_dir, skill_id))
	if os.path.isdir(filename):
		return filename

	return None  # Skill cannot be resolved

class LapelSkill(GObject.Object):
	"""
	GObject wrapper for Mycroft skills, created from dicts provided by
	the 'skillmanager.list' message.
	"""
	__gtype_name__ = 'LapelSkill'

	def __init__(self, skill_id, data=None):
		"""Initializes a LapelSkill object."""
		super().__init__()
		self.skill_id = skill_id
		self.skill_path = skill_id_to_path(self.skill_id)
		if data:
			self.active = data['active']
		else:
			self.active = True

		# Get data from README
		if self.skill_path:
			readme = os.path.join(self.skill_path, 'README.md')
			if not os.path.isfile(readme):
				print("Couldn't find information for " + self.skill_id)
				self.data = None
			else:
				with open(readme) as readme_raw:
					readme_content = readme_raw.read()
					self.data = {}

					# Get icon and title
					img_title_exp = re.compile("<img[^>]*src='([^']*)'.*\/>\s(.*)") # noqa: W605
					img_title_match = img_title_exp.findall(readme_content)

					if img_title_match:
						try:
							self.data['icon'] = img_title_match[0][0]
							self.data['title'] = img_title_match[0][1]
						except (ValueError, KeyError):
							print("Could not find title and icon for skill with ID " + self.skill_id)
							self.data['icon'] = None
							self.data['title'] = None
					else:
							print("Could not find title and icon for skill with ID " + self.skill_id)
							self.data['icon'] = None
							self.data['title'] = None

					# Get examples
					examples_exp = re.compile('## Examples.*\n.*"(.*)"\n\*\s"(.*)"') # noqa: W605
					examples_match = examples_exp.findall(readme_content)
					if examples_match:
						self.data['examples'] = examples_match[0]
					else:
						self.data['examples'] = []

					# Get categories
					category_exp = re.compile("## Category.*\n\*\*(.*)\*\*") # noqa: W605
					category_match = category_exp.findall(readme_content)
					if category_match:
						self.data['category'] = category_match[0]
					else:
						self.data['category'] = None

					# TODO: Get tags
		else:
			self.data = None

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def id(self):
		"""The skill's unique ID."""
		return self.skill_id

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def path(self):
		"""The path to the skill's source code."""
		return self.skill_path

	@GObject.Property(type=bool, default=True)
	def is_active(self):
		"""Whether the skill is active or not."""
		return self.active

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/skillview.ui')
class SkillView(Gtk.Box):
	"""
	GTK widget for displaying the data of a message contained in a
	LapelMessage object.
	"""
	__gtype_name__ = 'SkillView'

	title_label = Gtk.Template.Child()
	examples_label = Gtk.Template.Child()

	def __init__(self):
		super().__init__()

	def bind_to_skill(self, skill):
		"""Binds the SkillView to a LapelSkill."""
		self.skill = skill
		if skill.data:
			self.title_label.set_label(skill.data['title'])

			if skill.data['examples']:
				examples = ''
				for example in skill.data['examples']:
					if examples != '':
						examples += '\n'
					examples += '• ' + example
				self.examples_label.set_label(examples)
			else:
				self.examples_label.set_use_markup(True)
				# TRANSLATORS: Shown in the skills menu when no a skill has no provided examples.
				self.examples_label.set_label('<i>' + _('No examples found.') + '</i>') # noqa: F821
		else:
			self.title_label.set_label(skill.id)
			self.examples_label.set_use_markup(True)
			# TRANSLATORS: Shown in the skills menu when a skill's information could not be found.
			self.examples_label.set_label('<i>' + _("Skill data not found.") + '</i>') # noqa: F821
