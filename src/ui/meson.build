pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'lapel')
gnome = import('gnome')

gnome.compile_resources('lapel',
  'lapel.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)
