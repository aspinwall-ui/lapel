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

    def __init__(self):
        """Initializes an image wrapper."""
        super().__init__()

    def add_from_path(self, path, alt=None):
        picture = Gtk.Picture.new_for_filename(path)
        picture.set_can_shrink(True)
        picture.set_size_request(-1, 200)
        picture.set_overflow(Gtk.Overflow.HIDDEN)
        picture.add_css_class('rounded')
        if alt:
            picture.set_alternative_text(alt)

        self.append(picture)

    def add_from_pixbuf(self, pixbuf, alt=None):
        self.pixbuf = pixbuf
        self.alt = alt

        if not pixbuf:
            return

        picture = Gtk.Picture.new_for_pixbuf(pixbuf)
        picture.set_can_shrink(True)
        picture.set_size_request(-1, 200)
        picture.set_overflow(Gtk.Overflow.HIDDEN)
        picture.add_css_class('rounded')
        if alt:
            picture.set_alternative_text(alt)

        self.append(picture)
