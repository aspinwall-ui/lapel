# coding: utf-8
"""
Code for the assistant popup.
"""
from gi.repository import Adw, Gtk
from ..daemon import get_daemon

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/popup.ui')
class AssistantPopup(Adw.Window):
    """Popup window that appears when Mycroft hears its wakeword."""
    __gtype_name__ = 'AssistantPopup'

    flap = Gtk.Template.Child()

    _state = -1 # closed

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.flap.connect('notify::reveal-flap', self.handle_reveal_flap)
        self.flap.connect('notify::reveal-progress', self.handle_reveal_progress)
        self.daemon = get_daemon()
        #self.daemon.on('mycroft.mic.listen', self._show)
        self.daemon.on('recognizer_loop:wakeword', self._show)
        self.daemon.on('recognizer_loop:record_end', self._hide)
        self.daemon.on('speak', self.open_on_message)

    def _show(self, *args):
        active_window = self.app.get_active_window()
        if active_window and active_window.get_visible():
            return

        if self._state == -1:
            self._state = 1 # showing
            self.set_visible(True)
            self.present()
            self.fullscreen()
            self.set_opacity(0.5)
            self.flap.set_reveal_flap(True)

    def _hide(self, *args):
        if self.flap.get_reveal_flap():
            self._state = 0
            self.flap.set_reveal_flap(False)

    def handle_reveal_flap(self, *args):
        if self._state == -1: # closed
            self._state = 1 # opening
        elif self._state == 2: # opened
            self._state = 0 # hiding

    def handle_reveal_progress(self, flap, *args):
        progress = flap.get_reveal_progress()
        if progress == 0 and self._state == 0:
            self.set_visible(False)
            self.daemon.stop_record()
            self._state = -1 # closed
        elif progress == 1 and self._state == 1:
            self._state = 2

    def open_on_message(self, message):
        try:
            if message.data['meta']['skill'] == 'UnknownSkill':
                return
        except KeyError:
            pass
        self.app.show_window()

    def close(self, *args):
        # stub
        pass
