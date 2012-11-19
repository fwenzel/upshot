#!/usr/bin/env python
import glob
import logging
import os
import shutil
import sys
import time
import urllib
import urlparse

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from lib import utils


SCREENSHOT_DIR = utils.get_pref(
    domain='com.apple.screencapture', key='location',
    default=os.path.join(os.environ['HOME'], 'Desktop'))
# XXX: Actually detect dropbox dir
SHARE_DIR = os.path.join(utils.detect_dropbox_folder(), 'Public',
                         'Screenshots')

# XXX: Detect this, somehow
DROPBOX_ID = 18779383  # Part of my public shares, probably safe to put here.
SHARE_URL = 'http://dl.dropbox.com/u/%s/Screenshots/' % DROPBOX_ID

RANDOM_FILENAMES = True  # Randomize file name?

# Set up logging
LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger('upshot')

# Local settings
try:
    from settings_local import *
except ImportError:
    pass


class ScreenshotHandler(FileSystemEventHandler):
    """Handle file creation events in our screenshot dir."""
    def on_moved(self, event):
        """
        Catch move event: OS X creates a temp file, then moves it to its
        final name.
        """
        f = event.dest_path

        # The moved file could be anything. Only act if it's a screenshot.
        if not utils.is_screenshot(f):
            return

        # Create target dir if needed.
        if not os.path.isdir(SHARE_DIR):
            log.debug('Creating share dir %s' % SHARE_DIR)
            os.makedirs(SHARE_DIR)

        # Move image file to target dir.
        log.debug('Moving %s to %s' % (f, SHARE_DIR))
        if RANDOM_FILENAMES:
            ext = os.path.splitext(f)[1]
            while True:
                shared_name = utils.randname() + ext
                target_file = os.path.join(SHARE_DIR, shared_name)
                if not os.path.exists(target_file):
                    log.debug('New file name is: %s' % shared_name)
                    shutil.move(f, target_file)
                    break
        else:
            shared_name = os.path.basename(f)
            shutil.move(f, SHARE_DIR)

        # Create shared URL
        url = urlparse.urljoin(SHARE_URL, urllib.quote(shared_name))
        logging.debug('Share URL is %s' % url)

        logging.debug('Copying to clipboard.')
        utils.pbcopy(url)


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
