from cx_Freeze import setup, Executable

setup(
    name='Common Clipboard Server',
    author='cmdvmd',
    version='0.1-alpha',
    options={
        'build_exe': {
            'packages': [
                'setuptools',
                'time',
                'webbrowser',
                'infi.systray',
                'flask',
                'threading',
                'io',
            ],
            'include_files': [
                'static',
                'templates'
            ]
        }
    },
    executables=[
        Executable(
            script='server.py',
            icon='icon.ico',
            shortcut_name='Common Clipboard Server',
            shortcut_dir='StartMenuFolder',
            base='Win32GUI'
        )
    ]
)
