#!/usr/bin/env python
import glob
import logging
import os
import shutil
import sys
import time
import urllib
import urlparse

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from lib.utils import pbcopy


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


class ScreenshotHandler(PatternMatchingEventHandler):
    """Handle file creation events in our screenshot dir."""
    def __init__(self):
        super(ScreenshotHandler, self).__init__(
            patterns='Screen Shot.*\.png')

    def on_moved(self, event):
        """
        Catch move event: OS X creates a temp file, then moves it to its
        final name.
        """
        f = event.dest_path

        # Create target dir if needed.
        if not os.path.isdir(SHARE_DIR):
            log.debug('Creating share dir %s' % SHARE_DIR)
            os.makedirs(SHARE_DIR)

        # Move image file to target dir.
        log.debug('Moving %s to %s' % (f, SHARE_DIR))
        shutil.move(f, SHARE_DIR)

        # Create shared URL
        url = urlparse.urljoin(
            SHARE_URL, urllib.quote(os.path.basename(f)))
        logging.debug('Share URL is %s' % url)

        logging.debug('Copying to clipboard.')
        pbcopy(url)


if __name__ == '__main__':
    # Listen to changes to the screenshot dir.
    event_handler = ScreenshotHandler()
    observer = Observer()
    observer.schedule(event_handler, path=SCREENSHOT_DIR)
    observer.start()
    log.debug('Listening for screen shots to be added to: %s' % (
              SCREENSHOT_DIR))

    try:
        while True:
            # Hang out while the listener listens.
            time.sleep(1)

    except KeyboardInterrupt:
        sys.exit(0)

    finally:
        observer.stop()
        observer.join()
