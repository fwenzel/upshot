#!/usr/bin/env python
import glob
import os
import shutil
import sys
import time
import urllib
import urlparse

from AppKit import *
from PyObjCTools import AppHelper

from watchdog.events import (FileCreatedEvent, FileMovedEvent,
                             FileSystemEventHandler)
from watchdog.observers import Observer

import DropboxDetect
import Preferences
from lib import notifications, utils
from lib.logger import log
from lib.notifications import notify
from lib.updater import SparkleUpdater
from lib.windows import alert


SCREENSHOT_DIR = utils.get_pref(
    domain='com.apple.screencapture', key='location',
    default=os.path.join(os.environ['HOME'], 'Desktop'))
DROPBOX_DIR = utils.detect_dropbox_folder()
PUBLIC_DIR = os.path.join(DROPBOX_DIR or '', 'Public')
SHARE_DIR = os.path.join(PUBLIC_DIR, 'Screenshots')

HOMEPAGE_URL = 'http://upshot.it'
DROPBOX_PUBLIC_INFO = 'https://www.dropbox.com/help/16'

TIME_THRESHOLD = 15  # How many seconds after creation do we handle a file?

# Local settings
try:
    from settings_local import *
except ImportError:
    pass


class Upshot(NSObject):
    """OS X status bar icon."""
    icon_paths = {
        'icon_on': 'status',  # Refers to resources/<name>.png and <name>@2x.png
        'icon_off': 'status-off',
    }
    images = {}
    statusitem = None
    updater = None  # Sparkle instance.
    observer = None  # Screenshot directory observer.
    menuitems = {}  # Shortcut to our menuitems.

    def applicationDidFinishLaunching_(self, notification):
        # Check for updates.
        self.updater = SparkleUpdater.alloc().init()
        self.updater.auto_update()

        if not DROPBOX_DIR:  # Oh-oh.
            alert('Unable to detect Dropbox folder',
                  'UpShot requires Dropbox, for now. Please install it, then '
                  'try again.', ['OK'])
            self.quit_(self)

        if not os.path.exists(PUBLIC_DIR):  # No public folder?
            pressed = alert(
                'Unable to detect Public Dropbox folder',
                'UpShot requires a Dropbox Public folder. You seem to have '
                'Dropbox, but no Public folder.\n\n'
                'Since October 2012, Dropbox will only create a public '
                'folder for you if you opt in to it.\n\n'
                'Please do so before using UpShot.',
                ['Learn How to Create a Dropbox Public Folder',
                 'Quit UpShot'])
            if pressed == NSAlertFirstButtonReturn:
                # Open Dropboc opt-in
                sw = NSWorkspace.sharedWorkspace()
                sw.openURL_(NSURL.URLWithString_(DROPBOX_PUBLIC_INFO))
            self.quit_(self)

        # Initialize things.
        self.build_menu()

        # Go do something useful.
        if utils.get_pref('dropboxid'):
            self.startListening_()
        else:
            self.stopListening_()
            DropboxDetect.DropboxDetectWindowController.showWindow()

    def build_menu(self):
        """Build the OS X status bar menu."""
        # Create the statusbar item
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)

        # Set statusbar icon and color/grayscale mode.
        for tag, img in self.icon_paths.items():
            # Automatically pick named file as 1x or 2x based on Retina.
            self.images[tag] = NSImage.imageNamed_(img)
            self.images[tag].setTemplate_(True)
        self.statusitem.setImage_(self.images['icon_on'])

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
            'Check for Updates...', 'updateCheck:', '')
        self.menu.addItem_(m)
        self.menuitems['updatecheck'] = m

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Open UpShot Project Website', 'website:', '')
        self.menu.addItem_(m)
        self.menuitems['website'] = m

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'About UpShot', 'about:', '')
        self.menu.addItem_(m)
        self.menuitems['about'] = m

        self.menu.addItem_(NSMenuItem.separatorItem())

        m = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            'Quit UpShot', 'quit:', '')
        self.menu.addItem_(m)
        self.menuitems['quit'] = m

        self.statusitem.setMenu_(self.menu)

    def update_menu(self):
        """Update status bar menu based on app status."""
        if self.statusitem is None:
            return

        running = (self.observer is not None)
        self.statusitem.setImage_(self.images['icon_on' if running else
                                              'icon_off'])

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
        """Open standard About dialog."""
        app = NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
        app.orderFrontStandardAboutPanel_(sender)

    def updateCheck_(self, sender=None):
        self.updater.sparkle.checkForUpdates_(sender)

    def website_(self, sender=None):
        """Open the UpShot homepage in a browser."""
        sw = NSWorkspace.sharedWorkspace()
        sw.openURL_(NSURL.URLWithString_(HOMEPAGE_URL))

    def openPreferences_(self, sender=None):
        Preferences.PreferencesWindowController.showWindow()

    def startListening_(self, sender=None):
        """Start listening for changes to the screenshot dir."""
        event_handler = ScreenshotHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, path=SCREENSHOT_DIR)
        self.observer.start()
        self.update_menu()
        log.debug('Listening for screen shots to be added to: %s' % (
                  SCREENSHOT_DIR))

        notify('UpShot started', 'and listening for screenshots!')

    def stopListening_(self, sender=None):
        """Stop listening to changes ot the screenshot dir."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            log.debug('Stop listening for screenshots.')

            if sender == self.menuitems['quit']:
                notify('UpShot shutting down',
                       'Not listening for screenshots anymore!')
            else:
                notify('UpShot paused',
                       'Not listening for screenshots for now!')
        self.update_menu()

    def restart_(self, sender=None):
        self.stopListening_()
        self.startListening_()

    def quit_(self, sender=None):
        """Default quit event."""
        log.debug('Terminating.')
        self.stopListening_(sender)
        NSApplication.sharedApplication().terminate_(sender)


class ScreenshotHandler(FileSystemEventHandler):
    """Handle file creation events in our screenshot dir."""
    def on_created(self, event):
        """File creation, handles screen clips."""
        f = event.src_path
        if isinstance(event, FileCreatedEvent) and not (
            os.path.basename(f).startswith('.')):
            self.handle_screenshot_candidate(f)

    def on_moved(self, event):
        """
        Catch move event: For full screenshots, OS X creates a temp file,
        then moves it to its final name.
        """
        if isinstance(event, FileMovedEvent):
            self.handle_screenshot_candidate(event.dest_path)

    @utils.fail_gracefully
    def handle_screenshot_candidate(self, f):
        """Given a candidate file, handle it if it's a screenshot."""
        # The file could be anything. Only act if it's a screenshot.
        if not utils.is_screenshot(f):
            return

        # Do not act on files that are too old (so we don't swallow old files
        # that are not new screenshots).
        now = time.time()
        filename_time = utils.timestamp_from_filename(f)  # Parse time out of filename.
        if (now - os.path.getctime(f) > TIME_THRESHOLD or
            not filename_time or
            now - filename_time > TIME_THRESHOLD):
            log.debug('Ignoring %s, too old.' % f)
            return

        # Create target dir if needed.
        if not os.path.isdir(SHARE_DIR):
            log.debug('Creating share dir %s' % SHARE_DIR)
            os.makedirs(SHARE_DIR)

        # Determine target filename in share directory.
        log.debug('Moving %s to %s' % (f, SHARE_DIR))
        if utils.get_pref('randomize'):  # Randomize file names?
            ext = os.path.splitext(f)[1]
            while True:
                shared_name = utils.randname() + ext
                target_file = os.path.join(SHARE_DIR, shared_name)
                if not os.path.exists(target_file):
                    log.debug('New file name is: %s' % shared_name)
                    break
        else:
            shared_name = os.path.basename(f)
            target_file = os.path.join(SHARE_DIR, shared_name)

        # Move/copy file there.
        if (utils.get_pref('retinascale') and
            utils.resampleRetinaImage(f, target_file)):
            if not utils.get_pref('copyonly'):
                os.unlink(f)
        else:
            if utils.get_pref('copyonly'):
                shutil.copy(f, target_file)
            else:
                shutil.move(f, target_file)

        # Create shared URL.
        url = utils.share_url(urllib.quote(shared_name))
        log.debug('Share URL is %s' % url)

        log.debug('Copying to clipboard.')
        utils.pbcopy(url)

        # Notify user.
        notify('Screenshot shared!',
               'Your URL is: %s\n\n'
               'Click here to view file.' % url,
               context=target_file, callback=self.notify_callback)

    def notify_callback(self, filepath):
        """
        When notification is clicked, open Finder with shared file.
        """
        ws = NSWorkspace.sharedWorkspace()
        ws.activateFileViewerSelectingURLs_(
            NSArray.arrayWithObject_(NSURL.fileURLWithPath_(filepath)))


if __name__ == '__main__':
    # Prepare preferences service.
    Preferences.set_defaults()

    app = NSApplication.sharedApplication()
    delegate = Upshot.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
