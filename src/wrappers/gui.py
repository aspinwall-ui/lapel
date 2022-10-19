# coding: utf-8
"""
Wrappers that use GUI values.
"""
from gi.repository import Gtk, GdkPixbuf
from .common import ImageWrapper

import time
import tempfile
import os.path
import requests

class AnswerImageWrapper(ImageWrapper):
    """Generic wrapper containing an image."""
    __gtype_name__ = 'AnswerImageWrapper'

    def __init__(self, message, gui_values):
        """Initializes an AnswerImageWrapper."""
        super().__init__()

        if 'imgLink' not in gui_values or not gui_values['imgLink']:
            return

        image_url = gui_values['imgLink']
        title = None
        if 'title' in gui_values and gui_values['title']:
            title = gui_values['title']

        # Attempt to download the image
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(image_url)[1]) as image_cache:
            image_path = image_cache.name
            data = requests.get(image_url, stream=True)
            if data.status_code == 200:
                for chunk in data:
                    image_cache.write(chunk)
                image_cache.flush()
            self.add_from_path(image_path)
            image_cache.close()
