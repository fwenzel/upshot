import objc
from Foundation import *

import DropboxDetect
from utils import (UpShotWindowController, detect_dropbox_folder, get_pref,
                   set_pref)


DEFAULTS = {
    'randomize': True,  # Randomize screenshot names?
}


class PreferencesWindowController(UpShotWindowController):
    nibfile = u'PreferenceWindow'

    randomize = objc.IBOutlet()
    dropboxdir = objc.IBOutlet()
    dropboxid = objc.IBOutlet()

    def showWindow_(self, sender):
        super(PreferencesWindowController, self).showWindow_(sender)
        self.updateDisplay()

    def updateDisplay(self):
        """Update window display from settings."""
        dropboxdir = detect_dropbox_folder()
        self.dropboxdir.setStringValue_(
            dropboxdir or u'None. Install Dropbox?')
        self.dropboxid.setStringValue_(get_pref('dropboxid'))

        self.randomize.setState_(get_pref('randomize'))

    @objc.IBAction
    def saveSettings_(self, sender):
        """Save changed settings."""
        set_pref('randomize', bool(self.randomize.state()))
        try:
            set_pref('dropboxid', int(self.dropboxid.stringValue()))
        except ValueError:
            pass

    @objc.IBAction
    def dropboxDetect_(self, sender):
        """Open dropbox detection window."""
        DropboxDetect.DropboxDetectWindowController.showWindow(self.app)
        self.close()


def set_defaults():
    """
    Perform some sanity checks on our preferences and set defaults for those
    that aren't set.
    """
    for key, val in DEFAULTS.items():
        get_pref(key, default=val, setdefault=True)
