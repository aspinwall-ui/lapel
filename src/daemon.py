# coding: utf-8
"""
Contains code for the message bus daemon.
"""
from ovos_backend_client.api import DeviceApi
from ovos_backend_client import check_remote_pairing
from ovos_utils.signal import create_signal
from ovos_bus_client import Message
from ovos_bus_client import MessageBusClient as OriginalMessageBusClient
from gi.repository import Gio, GObject
import socket
import time
import threading
from uuid import uuid4
import websocket

from .types.message import LapelMessage
from .types.skill import LapelSkill
from .config import config

daemon = None

class MessageBusClient(OriginalMessageBusClient):
    # Subclass of MessageBusClient that replaces the on_error function
    def on_error(self, *args):
        if len(args) == 1:
            error = args[0]
        else:
            error = args[1]
        self.emitter.emit('error', error)
        try:
            self.client.close()
        except Exception as e:
            print(repr(e))

class GUIHandler:
    """
    Convenience class that handles GUI information.
    """
    ws = None
    port = None

    def __init__(self, daemon):
        # Some skills require a GUI to be registered, others just send
        # gui.value.set messages to the main bus directly.
        # ...unless the client bus is a GUI itself, in which case I'm
        # unaware of it.
        self.daemon = daemon
        self.client = self.daemon.client
        self.gui_id = "lapel_" + str(uuid4())

        self.client.on('gui.status.request', self.on_gui_request)
        self.client.on('mycroft.gui.port', self.gui_port)
        threading.Thread(target=self.gui_connect_func, daemon=True).start()

    def gui_connect_func(self):
        self.client.emit(Message('mycroft.gui.connected', {"gui_id": self.gui_id}))

    def on_gui_request(self, message):
        self.client.emit(message.reply("gui.status.request.response", {"connected": True}))

    def gui_port(self, message):
        if message.data['gui_id'] != self.gui_id:
            return

        self.port = message.data['port']
        self.ws = websocket.WebSocketApp("ws://0.0.0.0:" + str(self.port) + "/gui",
                    on_message=self.on_gui_message,
                    on_error=self.on_gui_error,
                    on_close=self.on_gui_close)
        print("GUI connection: ws://0.0.0.0:" + str(self.port))

    def on_gui_message(self, message):
        if message.data['type'] == 'gui.value.set':
            self.daemon.set_gui_values(message)

    def on_gui_error(self, socket, error):
        pass

    def on_gui_close(self, socket):
        self.ws.close()

    def __del__(self):
        self.ws.close()

class MessageBusDaemon(GObject.Object):
    """
    Convenience class that sets up the MessageBus handler and its
    callbacks.
    """
    error_handler_func = None
    _gui_cache = None

    _available = True
    _events = []

    def __init__(self):
        """Sets up the MessageBus handler."""
        super().__init__()
        self._connection_data = (config['websocket-address'], config['websocket-port'])
        self.api = DeviceApi()

        self.messages = Gio.ListStore(item_type=LapelMessage)
        self.skills = Gio.ListStore(item_type=LapelSkill)
        # Start client
        threading.Thread(target=self.setup_client, daemon=True).start()
        # Start availability checker thread
        threading.Thread(target=self._availability_check, daemon=True).start()
        self.connect('notify::available', self.restart_client)

    def restart_client(self, *args):
        """Restarts client after the connection is lost"""
        if self._available:
            threading.Thread(target=self.setup_client, daemon=True).start()

    def setup_client(self, *args):
        self.client = MessageBusClient(host=self._connection_data[0], port=self._connection_data[1])
        self.client.run_in_thread()

        self.check_available()
        if not self._available:
            return False

        self.gui = GUIHandler(self)

        self.client.on('speak', self.to_message)
        self.client.on('recognizer_loop:utterance', self.to_message)
        self.client.on('gui.value.set', self.set_gui_values)
        self.client.on('ready', self.on_ready)
        self.client.on('error', self.check_available)

        for message, handler in self._events:
            self.client.on(message, handler)

    def on(self, message, handler):
        """Wrapper around client.on()."""
        self._events.append((message, handler))
        self.client.on(message, handler)

    def check_available(self, *args):
        """
        Checks if Mycroft is available and sets the 'available' property
        accordingly.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(self._connection_data)
            if result == 0:
                if self._available != True:
                    self._available = True
                    self.notify('available')
            else:
                if self._available != False:
                    self._available = False
                    self.notify('available')
            sock.close()
        except (socket.gaierror, socket.error):
            if self._available != False:
                self._available = False
                self.notify('available')
            sock.close()

    def _availability_check(self):
        while True:
            self.check_available()

            time.sleep(5)

    @GObject.Property(type=bool, default=True, flags=GObject.ParamFlags.READABLE)
    def available(self):
        """Whether Mycroft is available or not."""
        return self._available

    def is_paired(self, *args):
        """Returns True if the device is paired, False otherwise."""
        if self.api.identity.uuid and check_remote_pairing(True):
            return True
        return False

    def start_record(self):
        """Starts recording the message for voice recognition."""
        self.client.emit(Message('mycroft.mic.listen'))

    def stop_record(self):
        """Stops recording the current voice recognition message."""
        self.client.emit(Message('mycroft.stop'))
        create_signal('buttonPress')

    # Message handling

    def to_message(self, message):
        """
        Turns the provided Message to a LapelMessage and adds it to the daemon's
        message list.
        """
        # HACK: drop messages from the pairing skill. We do pairing ourselves,
        # this only gets in the way
        try:
            if message.data['meta']['skill'] == 'PairingSkill' and \
                    message.data['meta']['dialog'] != 'already.paired':
                self.client.emit(Message('mycroft.stop'))
                return
        except KeyError:
            pass

        self.messages.append(LapelMessage(message))
        if self._gui_cache:
            self.set_gui_values(self._gui_cache)

    def _send_message(self, message, reply_to=None):
        """Sends a text message to the daemon."""
        if not reply_to:
            self.client.emit(Message('recognizer_loop:utterance',
                {"utterances": [message], "lang": 'en-us'})
            )
        else:
            try:
                context = {"source": reply_to.context["destination"],
                    "destination": reply_to.context["source"]}
            except KeyError:
                context = {}
            self.client.emit(Message('recognizer_loop:utterance',
                {"utterances": [message], "lang": 'en-us'}, context
            ))

    def send_message(self, message, reply_to=None):
        """Starts a thread to send a text message to the daemon."""
        send_thread = threading.Thread(target=self._send_message,
            args=[message, reply_to]
        )
        send_thread.start()

    def set_gui_values(self, message):
        """Sets GUI values for the message."""
        if not 'summary' in message.data:
            return

        last_message = self.messages.get_item(
            self.messages.get_n_items() -1
        )

        # Check if the GUI value is for us or for the next message
        if last_message and last_message.type != 'recognizer_loop:utterance' and \
                last_message.data['utterance'] == message.data['summary']:
            last_message.set_gui_values(message.data)
            self._gui_cache = None
        else:
            # Wait until next message (set_gui_values is called again with
            # self._gui_cache as the parameter in self.to_message)
            self._gui_cache = message

    def set_error_handler(self, handler):
        """Sets the function to be called when an error occurs."""
        self.error_handler_func = handler

    # Skills
    def refresh_skills(self, *args):
        """Sends a signal to refresh the skills list."""
        if self.skills.get_n_items() > 0:
            self.skills.remove_all()
        t = threading.Thread(target=self.client.emit, args=[Message('skillmanager.list')])
        t.start()

    def add_skill(self, skill_id, data=None):
        """Adds a skill to the skill store."""
        self.skills.append(LapelSkill(skill_id, data))

    def remove_skill(self, skill_id):
        """Removes a skill from the skill store."""
        skills = list(self.skills)
        for skill in skills:
            if skill.id == skill_id:
                self.skills.remove(skill)
                return

    def on_ready(self, *args):
        self.refresh_skills()

def get_daemon():
    """Returns the currently running MessageBus handler."""
    global daemon
    return daemon

def start_daemon():
    """Starts a MessageBusDaemon."""
    global daemon
    if daemon:
        print("Message bus daemon already exists")
        return
    else:
        daemon = MessageBusDaemon()
