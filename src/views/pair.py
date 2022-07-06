# coding: utf-8
"""
Code for the pairing dialog.
"""
from gi.repository import Adw, Gtk
from uuid import uuid4
from requests import HTTPError
import threading, time
from mycroft_bus_client import Message
from mycroft.api import is_paired
from mycroft.identity import IdentityManager

from ..daemon import get_daemon

@Gtk.Template(resource_path='/org/dithernet/lapel/ui/pair.ui')
class LapelPairingDialog(Adw.Window):
	"""Preference window for Assistant."""
	__gtype_name__ = 'LapelPairingDialog'

	pairing_code_label = Gtk.Template.Child()
	paired = False

	def __init__(self, parent=None):
		super().__init__(transient_for=parent)
		self.set_modal(True)
		self.daemon = get_daemon()

		self.state = str(uuid4)
		pairing_data = self.daemon.api.get_code(self.state)
		self.code = pairing_data['code']
		self.token = pairing_data['token']
		self.pairing_code_label.set_label(self.code)

		await_thread = threading.Thread(target=self.await_paired, daemon=True)
		await_thread.start()

		self.daemon.client.on('mycroft.paired', self.on_pair)
		self.daemon.client.on('mycroft.ready', self.on_pair)

	def await_paired(self):
		while not self.paired:
			time.sleep(2)
			try:
				login = self.daemon.api.activate(self.state, self.token)
			except HTTPError:
				pass
			else:
				IdentityManager.save(login)
				self.daemon.client.emit(Message("mycroft.paired", login))
				self.daemon.bus.emit(Message("configuration.updated"))
				self.on_pair()

	def on_pair(self, *args):
		is_paired()
		self.paired = True
		self.close()
