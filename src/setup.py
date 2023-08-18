import sys
from cx_Freeze import setup, Executable


def generate_shortcut_table(shortcuts):
    table = []
    for location in shortcuts:
        table.append((
            f'{location}Shortcut',
            f'{location}Folder',
            'Common Clipboard',
            'TARGETDIR',
            '[TARGETDIR]common_clipboard.exe',
            None,
            None,
            None,
            None,
            None,
            None,
            'TARGETDIR'
        ))
    return table


if __name__ == '__main__':
    setup(
        name='common_clipboard',
        description='Common Clipboard',
        author='cmdvmd',
        version='1.0b0',
        options={
            'build_exe': {
                'packages': [
                    'setuptools',
                    'requests',
                    'time',
                    'win32clipboard',
                    'sys',
                    'pickle',
                    'socket',
                    'threading',
                    'multiprocessing',
                    'enum',
                    'pystray',
                    'PIL',
                    'io',
                    'flask',
                    'tkinter'
                ],
                'excludes': [
                    '_distutils_hack',
                    'asyncio'
                    'concurrent',
                    'distutils',
                    'lib2to3',
                    'pkg_resources',
                    'pydoc_data',
                    'test',
                    'unittest',
                    'xml',
                    'xmlrpc',
                ],
                'include_files': [
                    'systray_icon.ico'
                ],
                'optimize': 2
            },
            'bdist_msi': {
                'data': {
                    'Shortcut': generate_shortcut_table(['Desktop', 'StartMenu', 'Startup'])
                }
            }
        },
        executables=[
            Executable(
                script='common_clipboard.py',
                icon='../static/icon.ico',
                copyright='Copyright (c) cmdvmd 2023',
                base='Win32GUI' if sys.platform == 'win32' else None,
                shortcut_name='Common Clipboard',
                shortcut_dir=''
            )
        ]
    )
