# coding: utf-8
"""
Contains code for working with widget dialogs
"""
from .dialog import ConfirmDialog
from .gui import AnswerImageWrapper
from .common import PlaceholderWrapper

dialog_wrappers = {
	"install.confirm": ConfirmDialog,
	"remove.confirm": ConfirmDialog
}

gui_wrappers = {
	"mycroft-fallback-duck-duck-go.mycroftai": AnswerImageWrapper,
	"mycroft-wiki.mycroftai": AnswerImageWrapper
}

def dialog_wrapper_for(message):
	"""Returns a dialog wrapper for the provided message."""
	if 'meta' in message.data and 'dialog' in message.data['meta']:
		dialog = message.data['meta']['dialog']
		if dialog in dialog_wrappers.keys():
			return dialog_wrappers[dialog](message)
	return None

def gui_wrapper_for(message):
	"""Returns a wrapper for the provided message's gui values."""
	gui_values = message._gui_values

	if '__from' in gui_values:
		_type = gui_values['__from']
	else:
		_type = message.type

	if _type in gui_wrappers:
		return gui_wrappers[_type](message, gui_values)
	return None
