import glob
import os
import platform
import sys
from tempfile import mkdtemp

from setuptools import setup

from fabric.api import local
from fabric.context_managers import lcd

RELEASE = '2.0'

HERE = os.path.dirname(__file__)
RUN_PATH = './dist/UpShot.app/Contents/MacOS/UpShot'
DMGNAME = 'UpShot-%s.dmg' % RELEASE
OPENSSL = '/usr/bin/openssl'

_path = lambda *a: os.path.join(HERE, *a)
_err = lambda s: sys.stderr.write('%s\n' % s)


def clean():
    """Clean up build artifacts."""
    local('rm -rf dist/ build/')
    local('find . -name \*.py[co] -delete')


def build():
    """Build executable via py2app."""
    if platform.system() != 'Darwin':
        _err('Sorry, only works on Mac OS X!')
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
        'plist': {  # Usually info.plist, we'll do it inline.
            'LSUIElement': 1,
            'NSPrincipalClass': 'UpShot',
            'NSHumanReadableCopyright': 'Fred Wenzel',
            'CFBundleIdentifier': 'com.fredericiana.upshot',
            'CFBundleVersion': RELEASE,
            'CFBundleShortVersionString': RELEASE,
            # Sparkle settings:
            'SUFeedURL': 'http://upshot.it/updates.xml',
            'SUPublicDSAKeyFile': 'dsa_pub.pem',
        },
        #'frameworks': glob.glob('resources/*.framework'),
        'excludes': ['email']
    }

    # XXX Workaround for https://bitbucket.org/ronaldoussoren/py2app/issue/126/
    # zipio throws IOError and needs time for cleanup. Lolwut?
    import py2app
    if py2app.__version__ == '0.8.1':
        import time
        import py2app.util
        def copy_decorator(f):
            def decorated(*args, **kwargs):
                try:
                    f(*args, **kwargs)
                except:
                    time.sleep(2)
                    raise
            return decorated
        py2app.util._copy_file = copy_decorator(py2app.util._copy_file)

    setup(
        name='UpShot',
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
        install_requires=['pyobjc'],
    )

    # Some cleanup.
    local('find dist/ -name .DS_Store -delete')


def make_dmg():
    """Bundle the app into a DMG file."""
    if not os.path.exists(RUN_PATH):
        _err('Run `fab build` before you can build a DMG file.')
        sys.exit(1)

    tmpdir = mkdtemp()
    with lcd(tmpdir):
        # Unzip and mount template sparseimage.
        local('unzip -o "%s"' % _path('dmg-template',
                                      'template.sparseimage.zip'))
        local('hdiutil mount template.sparseimage')

        # Copy build into sparseimage.
        local('cp -a "%s" /Volumes/UpShot/' % _path('dist', 'UpShot.app'))

        # Unmount this.
        local('hdiutil eject /Volumes/UpShot')

        # Make a DMG out of it.
        local('hdiutil convert template.sparseimage -format UDBZ '
              '-o "%s" > /dev/null' % _path('dist', DMGNAME))
        # "Internet-enable" it.
        local('hdiutil internet-enable "%s"' % _path('dist', DMGNAME))

    # Clean up.
    local('rm -rf "%s"' % tmpdir)


def sign(private_key=os.path.expanduser('~/dsa_priv.pem')):
    """Calculate .dmg file signature for automatic update service."""
    dmg_file = _path('dist', DMGNAME)

    if not os.path.exists(dmg_file):
        _err('Run `fab make_dmg` before you can sign the DMG file.')
        sys.exit(1)

    if not os.path.exists(private_key):
        _err('Private key file %s not found. Choose your own with `fab '
             'sign:<private_key>`' % private_key)
        sys.exit(1)

    local('{openssl} dgst -sha1 -binary < "{dmg}" | '
          '{openssl} dgst -dss1 -sign "{key}" | '
          '{openssl} enc -base64'.format(openssl=OPENSSL, dmg=dmg_file,
                                         key=private_key))


def run():
    """Run an already built instance of UpShot."""
    if not os.path.exists(RUN_PATH):
        _err('Run `fab build` before you can run UpShot.')
        sys.exit(1)
    local(RUN_PATH)
