pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'lapel')

lapel_types_sources = [
  '__init__.py',
  'message.py',
  'skill.py'
]

install_data(lapel_types_sources, install_dir: join_paths(moduledir, 'types'))
