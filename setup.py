from setuptools import setup

APP = ['upshot.py']
DATA_FILES = ['resources', 'PreferenceWindow.xib']
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'LSUIElement': 1,
        'NSPrincipalClass': 'UpShot',
        'CFBundleShortVersionString': '0.1',
        'NSHumanReadableCopyright': 'Fred Wenzel',
        'CFBundleIdentifier': 'com.fredericiana.upshot',
    },
}

setup(
    name='UpShot',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# Missing libraries (in VIRTUAL_ENV)
# can be symlinked in from:
# /usr/local/Cellar/python/.../libpython2.7.dylib
