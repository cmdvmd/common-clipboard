import sys
from cx_Freeze import setup, Executable


if __name__ == '__main__':
    setup(
        name='common_clipboard',
        description='Common Clipboard',
        author='cmdvmd',
        version='1.1b2',
        options={
            'build_exe': {
                'packages': [
                    'setuptools',
                    'requests',
                    'time',
                    'win32clipboard',
                    'sys',
                    'os',
                    'pickle',
                    'socket',
                    'threading',
                    'multiprocessing',
                    'enum',
                    'pystray',
                    'PIL',
                    'io',
                    'ntplib',
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
            }
        },
        executables=[
            Executable(
                script='common_clipboard.py',
                icon='../static/icon.ico',
                copyright='Copyright (c) cmdvmd 2023',
                base='Win32GUI' if sys.platform == 'win32' else None
            )
        ]
    )
