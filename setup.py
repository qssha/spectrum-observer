from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['scipy', 'PyAstronomy',  'CustomExporter', 'CmfgenParse', 'FileDialog', 'Tkinter'],
                    excludes = ['collections.sys', 'collections._weakref', 'traitlets'])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None


executables = [
    Executable('SpecObserver.py', base=base, icon='web.png')
]

setup(name='',
      version = '1.0',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
