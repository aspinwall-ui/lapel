# coding: utf-8
"""
Code for the preferences window.
"""
from gi.repository import Adw, Gtk

from ..config import config

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/preferences.ui')
class LapelPreferences(Adw.PreferencesWindow):
    """Preference window for Assistant."""
    __gtype_name__ = 'LapelPreferences'

    ws_address_entry = Gtk.Template.Child()
    ws_port_entry = Gtk.Template.Child()

    def __init__(self):
        """Initializes the preferences."""
        super().__init__()

        self.ws_address_entry.set_text(config['websocket-address'])
        self.ws_port_entry.set_text(str(config['websocket-port']))

    @Gtk.Template.Callback()
    def set_address(self, entry, *args):
        config['websocket-address'] = entry.get_text()

    @Gtk.Template.Callback()
    def set_port(self, entry, *args):
        config['websocket-port'] = int(entry.get_text())
