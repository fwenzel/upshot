import base64
import os
import random
import string
from functools import wraps
from subprocess import check_output
from urlparse import urljoin

from Foundation import *
from AppKit import *


CHARS = string.ascii_letters + string.digits
DEFAULT_SHARE_URL = 'http://dl.dropboxusercontent.com/u/{dropboxid}/Screenshots/'


def autopooled(f):
    """
    Decorator to keep threads from leaking in ObjC.
    http://pyobjc.sourceforge.net/documentation/pyobjc-core/intro.html#working-with-threads
    """
    @wraps(f)
    def pooled_func(*args, **kwargs):
        pool = NSAutoreleasePool.alloc().init()
        result = f(*args, **kwargs)
        del pool
        return result
    return pooled_func


def detect_dropbox_folder():
    """
    Find user's dropbox folder location.
    They keep it base64-encoded in a file 'host.db' in $HOME/.dropbox.
    """
    try:
        with open(os.path.join(os.environ['HOME'], '.dropbox', 'host.db'),
                  'r') as f:
            encoded_dir = f.readlines()[1]
            return base64.b64decode(encoded_dir)
    except:
        return None


@autopooled
def is_screenshot(filename):
    """Is file an OS X screen capture?"""
    fileman = NSFileManager.defaultManager()
    # Read file attributes.
    try:
        attrs = fileman.attributesOfItemAtPath_error_(filename, None)[0]
        # Abandon all hope for PEP8, ye who enter here.
        is_screen = attrs['NSFileExtendedAttributes']['com.apple.metadata:kMDItemIsScreenCapture']
        plist, fmt, err = NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
            is_screen, NSPropertyListMutableContainers, None, None)
        # If all this worked, we have a boolean now.
        return isinstance(plist, bool) and plist
    except (TypeError, KeyError):
        return False


@autopooled
def pbcopy(s):
    """Copy text to the OS X clipboard."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    a = NSArray.arrayWithObject_(s)
    pb.writeObjects_(a)


def randname(length=4):
    """Generate random (file) name."""
    return ''.join(random.choice(CHARS) for i in xrange(length))


def resampleRetinaImage(filename, target):
    """
    Resample high DPI image ``filename`` to 72 dpi image ``target``.

    Uses ``sips``, which ships with OS X.

    Returns bool whether image was resampled successfully.
    """
    sips = '/usr/bin/sips'  # Safe to hard-code, I hope.
    # Extract image properties from sips.
    sipsinfo = lambda prop: check_output(
        [sips, '-g', prop, filename]).split(': ')[1].strip()

    # Detect current DPI.
    dpi = float(sipsinfo('dpiWidth'))
    if int(dpi) == 72:  # Nothing to do here.
        NSLog('File %s was already 72 dpi, nothing to resample.' % filename)
        return False

    # Determine current / target width and resample.
    cur_width = float(sipsinfo('pixelWidth'))
    target_width = int(72 / dpi * cur_width)

    check_output([sips, '--resampleWidth', str(target_width), filename,
                 '--out', target])
    NSLog('Resampled %s from %s dpi to 72.' % (filename, dpi))
    return True


def share_url(filename, url=None):
    """Get the URL a file will be shared under."""
    if url is None:  # Get pref. Otherwise use passed-in URL fragment.
        url = get_pref('customurl')

    if url:  # Custom URL
        return urljoin(url, filename)
    else:  # Default URL.
        return urljoin(
            DEFAULT_SHARE_URL.format(dropboxid=get_pref('dropboxid')),
            filename)


@autopooled
def get_pref(key, default=None, setdefault=False, domain=None):
    """
    Read a user pref, possibly from another domain.
    setdefault will set pref to default value if not found.
    """
    user_defaults = NSUserDefaults.standardUserDefaults()
    if domain is not None:
        user_defaults = user_defaults.persistentDomainForName_(domain)
    try:
        return user_defaults[key]
    except (TypeError, KeyError):
        if setdefault and domain is None:
            set_pref(key, default)
        # If domain or key were not found, fall back.
        return default


@autopooled
def set_pref(key, val):
    """Set a user pref in the current domain."""
    user_defaults = NSUserDefaults.standardUserDefaults()
    user_defaults.setObject_forKey_(val, key)
