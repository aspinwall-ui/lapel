# coding: utf-8
"""
Contains code for working with widget dialogs
"""
from .wrappers import ConfirmDialog

dialog_wrappers = {
	"install.confirm": ConfirmDialog,
	"remove.confirm": ConfirmDialog
}

def dialog_wrapper_for(dialog):
	"""Returns a dialog wrapper for the provided dialog."""
	print(dialog)
	if dialog in dialog_wrappers.keys():
		return dialog_wrappers[dialog]()
	return None
