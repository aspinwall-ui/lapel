pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'lapel')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'lapel.in',
  output: 'lapel',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

lapel_sources = [
  '__init__.py',
  'assistant.py',
  'daemon.py',
  'message.py',
  'window.py',
]

install_data(lapel_sources, install_dir: moduledir)

subdir('wrappers')
