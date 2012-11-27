import glob
import os
import platform
import sys

from setuptools import setup

from fabric.api import local


RUN_PATH = './dist/UpShot.app/Contents/MacOS/UpShot'
RELEASE = '0.1'


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
    DATA_FILES = [('', glob.glob('resources/*')), ('', glob.glob('*.xib'))]
    OPTIONS = {
        'argv_emulation': False,
        'iconfile': 'resources/UpShot.icns',
        'plist': {
            'LSUIElement': 1,
            'NSPrincipalClass': 'UpShot',
            'CFBundleShortVersionString': RELEASE,
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


def make_dmg():
    if not os.path.exists(RUN_PATH):
        sys.stderr.write('Run `fab build` before you can build a DMG file.')
        sys.exit(1)
    # XXX Should probably do all this in a temp dir.

    # Unzip and mount template spareseimage.
    local('unzip -o dmg-template/template.sparseimage.zip')
    local('hdiutil mount template.sparseimage')

    # Copy build into sparseimage.
    local('cp -a dist/UpShot.app /Volumes/UpShot/')

    # Unmount this.
    local('hdiutil eject /Volumes/UpShot')

    # Make a DMG out of it.
    dmgname = 'UpShot-%s.dmg' % RELEASE
    local('hdiutil convert template.sparseimage -format UDBZ -o ./dist/%s > '
          '/dev/null' % dmgname)

    # Clean up.
    local('rm -f template.sparseimage')


def run():
    """Run an already built instance of UpShot."""
    if not os.path.exists(RUN_PATH):
        sys.stderr.write('Run `fab build` before you can run UpShot.')
        sys.exit(1)
    local(RUN_PATH)
