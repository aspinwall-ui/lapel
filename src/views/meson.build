pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'lapel')

lapel_view_sources = [
  '__init__.py',
  'assistant.py',
  'pair.py',
  'popup.py',
  'preferences.py',
  'skills.py',
]

install_data(lapel_view_sources, install_dir: join_paths(moduledir, 'views'))
