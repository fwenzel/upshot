import glob
import os
import platform
import sys

from setuptools import setup

from fabric.api import local


def clean():
    """Clean up build artifacts."""
    local('rm -rf dist/ build/')
    local('find . -name \*.py[co] -delete')


def build():
    """Build executable via py2app."""
    if platform.system() != 'Darwin':
        print 'Sorry, only works on Mac OS X!'
        sys.exit(1)

    # Clean up old build dir.
    clean()

    # Now build this.
    sys.argv[1] = 'py2app'

    APP = ['upshot.py']
    DATA_FILES = ['resources', ('', glob.glob('*.xib'))]
    OPTIONS = {
        'argv_emulation': False,
        # 'iconfile': 'resources/upshot.icns',
        'plist': {
            'LSUIElement': 1,
            'NSPrincipalClass': 'UpShot',
            'CFBundleShortVersionString': '0.1',
            'NSHumanReadableCopyright': 'Fred Wenzel',
            'CFBundleIdentifier': 'com.fredericiana.upshot',
        },
        'excludes': ['email']
    }

    setup(
        name='UpShot',
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )

    # Some cleanup.
    local('find dist/ -name .DS_Store -delete')


def run():
    """Run an already built instance of UpShot."""
    runpath = './dist/UpShot.app/Contents/MacOS/UpShot'
    if not os.path.exists(runpath):
        sys.stderr.write('Run `fab build` before you can run UpShot.')
        sys.exit(1)
    local(runpath)
