pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'lapel')

lapel_wrapper_sources = [
  '__init__.py',
  'wrappers.py'
]

install_data(lapel_wrapper_sources, install_dir: join_paths(moduledir, 'wrappers'))
