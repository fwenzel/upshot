#!/usr/bin/env python
import glob
import logging
import os
import shutil
import sys
import time
import urllib
import urlparse

import Foundation
from AppKit import NSArray, NSPasteboard


# XXX: Use (possibly) configured screen shot dir, fall back to desktop.
# http://secrets.blacktree.com/?showapp=com.apple.screencapture
SCREENSHOT_DIR = os.path.join(os.environ['HOME'], 'Desktop')
# XXX: Actually detect dropbox dir
SHARE_DIR = os.path.join(os.environ['HOME'], 'Dropbox', 'Public',
                         'Screenshots')

# XXX: Detect this, somehow
DROPBOX_ID = 18779383  # Part of my public shares, probably safe to put here.
SHARE_URL = 'http://dl.dropbox.com/u/%s/Screenshots/' % DROPBOX_ID

# Set up logging
LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger('upshot')

# Local settings
try:
    from settings_local import *
except ImportError:
    pass


def handle_screenshot(imagefile):
    # Create target dir if needed.
    if not os.path.isdir(SHARE_DIR):
        log.debug('Creating share dir %s' % SHARE_DIR)
        os.makedirs(SHARE_DIR)

    # Move image file to target dir.
    log.debug('Moving %s to %s' % (imagefile, SHARE_DIR))
    shutil.move(imagefile, SHARE_DIR)

    # Create shared URL
    url = urlparse.urljoin(
        SHARE_URL, urllib.quote(os.path.basename(imagefile)))
    logging.debug('Share URL is %s' % url)

    logging.debug('Copying to clipboard.')
    pbcopy(url)


def pbcopy(s):
    """Copy text to the OS X clipboard."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    a = NSArray.arrayWithObject_(s)
    pb.writeObjects_(a)


if __name__ == '__main__':
    try:
        # XXX: Ugly. Listen to changes in the screenshot target dir instead.
        while True:
            # XXX: Read OS X screen capture flag in the file instead to make
            # sure it's really a screen shot.
            for f in glob.glob(os.path.join(SCREENSHOT_DIR, 'Screen Shot *.png')):
                handle_screenshot(f)
            time.sleep(10)

    except KeyboardInterrupt:
        sys.exit(0)
