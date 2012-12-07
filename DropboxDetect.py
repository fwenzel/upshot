import os
import re

import objc
from AppKit import *
from Foundation import *

from lib.utils import detect_dropbox_folder, set_pref
from lib.windows import UpShotWindowController


DROPBOX_URL_RE = re.compile(r'^https?://dl.dropbox.com/u/(\d+)/.*')


class DropboxDetectWindowController(UpShotWindowController):
    nibfile = u'DropboxDetectWindow'
    timer = None
    detected_id = None  # Detected Dropbox ID.

    imgfield = objc.IBOutlet()
    infofield = objc.IBOutlet()
    okbutton = objc.IBOutlet()

    def awakeFromNib(self):
        img = NSImage.alloc().initByReferencingFile_('copy-public.png')
        self.imgfield.setImage_(img)

    def showWindow_(self, sender):
        super(DropboxDetectWindowController, self).showWindow_(sender)
        self.okbutton.setEnabled_(False)
        self.startTimer()

    def startTimer(self):
        """Start timer to listen to clipboard."""
        self.infofield.setStringValue_(u'Waiting for link...')

        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            NSDate.date(), 1.0, self, 'tick:', None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer,
                                                     NSDefaultRunLoopMode)
        self.timer.fire()

    def stopTimer(self):
        """Stop the listen timer."""
        if self.timer:
            self.timer.invalidate()
        self.timer = None

    def tick_(self, sender):
        """Listen to the clipboard."""
        pb = NSPasteboard.generalPasteboard()
        content = pb.stringForType_(NSStringPboardType)
        if content:
            matched = DROPBOX_URL_RE.match(content)
            if matched:
                # We got a winner!
                self.stopTimer()
                self.detected_id = matched.group(1)
                self.infofield.setStringValue_(u'Found! Press OK to save.')
                self.okbutton.setEnabled_(True)
                self.window().makeFirstResponder_(self.okbutton)
                # Show window up front.
                NSApp.activateIgnoringOtherApps_(True)
                self.window().makeKeyAndOrderFront_(self)

    @objc.IBAction
    def cancel_(self, sender):
        self.detected_id = None
        self.stopTimer()
        self.close()

    @objc.IBAction
    def ok_(self, sender):
        if self.detected_id:
            set_pref('dropboxid', self.detected_id)
            # Start sharing.
            app = NSApplication.sharedApplication()
            app.delegate().restart_()
        self.cancel_(sender)

    @objc.IBAction
    def openDropboxFolder_(self, sender):
        sw = NSWorkspace.sharedWorkspace()
        sw.openFile_(os.path.join(detect_dropbox_folder(), 'Public'))
