#!/usr/bin/env python
import glob
import logging
import os
import shutil
import sys
import time
import urllib
import urlparse

from AppKit import (
    NSApplication, NSImage, NSMenu, NSMenuItem, NSObject, NSStatusBar, NSURL,
    NSVariableStatusItemLength, NSWorkspace)
from PyObjCTools import AppHelper

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import DropboxDetect
import Preferences
import utils


SCREENSHOT_DIR = utils.get_pref(
    domain='com.apple.screencapture', key='location',
    default=os.path.join(os.environ['HOME'], 'Desktop'))
SHARE_DIR = os.path.join(utils.detect_dropbox_folder(), 'Public',
                         'Screenshots')

HOMEPAGE_URL = 'http://github.com/fwenzel/upshot'

SHARE_URL = 'http://dl.dropbox.com/u/{dropboxid}/Screenshots/'

# Set up logging
LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger('upshot')

# NSApp object
app = None

# Local settings
try:
    from settings_local import *
except ImportError:
    pass


class Upshot(NSObject):
    """OS X status bar icon."""
    image_paths = {
        'icon16': 'resources/icon16.png',
        'icon16-off': 'resources/icon16-off.png',
    }
    images = {}
    statusbar = None
    observer = None  # Screenshot directory observer.
    menuitems = {}  # Shortcut to our menuitems.

    def applicationDidFinishLaunching_(self, notification):
        self.build_menu()
        # Go do something useful.
        if utils.get_pref('dropboxid'):
            self.startListening_()
        else:
            self.stopListening_()
            DropboxDetect.DropboxDetectWindowController.showWindow(app)

    def build_menu(self):
        """Build the OS X status bar menu."""
        # Create the statusbar item
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)

        # Load images and set initial icon.
        for tag, img in self.image_paths.items():
            self.images[tag] = NSImage.alloc().initByReferencingFile_(img)
        self.statusitem.setImage_(self.images['icon16'])

        self.statusitem.setHighlightMode_(1)
        self.statusitem.setToolTip_('Upshot Screenshot Sharing')

        # Build menu.
        self.menu = NSMenu.alloc().init()

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Browse Screenshots', 'openShareDir:', '')
        self.menu.addItem_(m)
        self.menuitems['opensharedir'] = m

        self.menu.addItem_(NSMenuItem.separatorItem())

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Start Screenshot Sharing', 'startListening:', '')
        m.setHidden_(True)  # Sharing is on by default.
        self.menu.addItem_(m)
        self.menuitems['start'] = m

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Pause Screenshot Sharing', 'stopListening:', '')
        self.menu.addItem_(m)
        self.menuitems['stop'] = m

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Need to detect Dropbox ID. Open Preferences!", '', '')
        m.setHidden_(True)  # We hopefully don't need this.
        self.menu.addItem_(m)
        self.menuitems['needpref'] = m

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Preferences...', 'openPreferences:', '')
        self.menu.addItem_(m)
        self.menuitems['preferences'] = m

        self.menu.addItem_(NSMenuItem.separatorItem())

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'About UpShot', 'about:', '')
        self.menu.addItem_(m)
        self.menuitems['about'] = m

        self.menu.addItem_(NSMenuItem.separatorItem())

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Quit UpShot', 'terminate:', '')
        self.menu.addItem_(m)
        self.menuitems['quit'] = m

        self.statusitem.setMenu_(self.menu)

    def update_menu(self):
        """Update status bar menu based on app status."""
        running = (self.observer is not None)
        self.statusitem.setImage_(self.images['icon16' if running else
                                              'icon16-off'])

        if utils.get_pref('dropboxid'):  # Runnable.
            self.menuitems['stop'].setHidden_(not running)
            self.menuitems['start'].setHidden_(running)
            self.menuitems['needpref'].setHidden_(True)
        else:  # Need settings.
            self.menuitems['start'].setHidden_(True)
            self.menuitems['stop'].setHidden_(True)
            self.menuitems['needpref'].setHidden_(False)

    def openShareDir_(self, sender=None):
        """Open the share directory in Finder."""
        sw = NSWorkspace.sharedWorkspace()
        sw.openFile_(SHARE_DIR)

    def about_(self, sender=None):
        """Open the UpShot homepage in a browser."""
        sw = NSWorkspace.sharedWorkspace()
        sw.openURL_(NSURL.URLWithString_(HOMEPAGE_URL))

    def openPreferences_(self, sender=None):
        Preferences.PreferencesWindowController.showWindow(app)

    def startListening_(self, sender=None):
        """Start listening for changes to the screenshot dir."""
        event_handler = ScreenshotHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, path=SCREENSHOT_DIR)
        self.observer.start()
        self.update_menu()
        log.debug('Listening for screen shots to be added to: %s' % (
                  SCREENSHOT_DIR))

    def stopListening_(self, sender=None):
        """Stop listening to changes ot the screenshot dir."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            log.debug('Stop listening for screenshots.')
        self.update_menu()

    def restart_(self, sender=None):
        self.stopListening_()
        self.startListening_()

    def terminate_(self, sender=None):
        """Default quit event."""
        log.debug('Terminating.')
        self.stopListening()
        super(Upshot, self).terminate_(sender)


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
        if utils.get_pref('randomize'):  # Randomize file names?
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
        url = urlparse.urljoin(
            SHARE_URL.format(dropboxid=utils.get_pref('dropboxid')),
            urllib.quote(shared_name))
        logging.debug('Share URL is %s' % url)

        logging.debug('Copying to clipboard.')
        utils.pbcopy(url)


if __name__ == '__main__':
    # Prepare preferences service.
    Preferences.set_defaults()

    app = NSApplication.sharedApplication()
    delegate = Upshot.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
