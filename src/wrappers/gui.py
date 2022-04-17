# coding: utf-8
"""
Wrappers that use GUI values.
"""
from gi.repository import Gtk, GdkPixbuf
from .common import ImageWrapper

import time
import tempfile
import os.path
import urllib

class AnswerImageWrapper(Gtk.Box):
	"""Generic wrapper containing an image."""
	__gtype_name__ = 'AnswerImageWrapper'

	def __init__(self, message, gui_values):
		"""Initializes an AnswerImageWrapper."""
		super().__init__()
		if 'imgLink' not in gui_values.keys() or not gui_values['imgLink']:
			super().__init__(None)
			return

		image_url = gui_values['imgLink']
		title = gui_values['title']

		# Attempt to download the image
		with tempfile.TemporaryDirectory() as tmpdir:
			filename = str(time.time()) + os.path.splitext(image_url)[1]
			saved_image_path = os.path.join(tmpdir, filename)

			try:
				urllib.request.urlretrieve(image_url, saved_image_path)
			except (ValueError, urllib.error.URLError):
				print("Failed to retrieve image: " + image_url)
				super().__init__(None)
				return

			pixbuf = GdkPixbuf.Pixbuf.new_from_file(saved_image_path)

			picture = Gtk.Image.new_from_pixbuf(pixbuf)
			#if title:
			#	picture.set_alternative_text(title)

			self.append(picture)
