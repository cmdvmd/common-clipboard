from cx_Freeze import setup, Executable

setup(
    name='Common Clipboard',
    author='cmdvmd',
    version='0.1-alpha',
    options={
        'build_exe': {
            'packages': [
                'setuptools',
                'requests',
                'time',
                'win32clipboard',
                'socket',
                'threading',
                'enum',
                'infi.systray',
                'io',
                'plyer'
            ],
            'include_files': [
                'static'
            ]
        }
    },
    executables=[
        Executable(
            script='common_clipboard.py',
            icon='icon.ico',
            shortcut_name='Common Clipboard',
            shortcut_dir='StartMenuFolder',
            base='Win32GUI'
        )
    ]
)
