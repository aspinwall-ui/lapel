# coding: utf-8
"""
Common wrapper base classes.
"""
from gi.repository import Gtk

class PlaceholderWrapper(Gtk.Box):
	"""test"""
	__gtype_name__ = 'PlaceholderWrapper'

	def __init__(self, *args):
		"""aaa"""
		super().__init__()

class ImageWrapper(Gtk.Box):
	"""Generic wrapper containing an image."""
	__gtype_name__ = 'ImageWrapper'

	def __init__(self, pixbuf, alt=None):
		"""Initializes an image wrapper."""
		super().__init__()

		self.pixbuf = pixbuf
		self.alt = alt

		if not pixbuf:
			print("no image")
			return

		picture = Gtk.Picture.new_for_pixbuf(pixbuf)
		if alt:
			picture.set_alternative_text(alt)

		self.append(picture)
