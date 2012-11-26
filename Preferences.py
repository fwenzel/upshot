import objc
from Foundation import *

import DropboxDetect
from lib.utils import detect_dropbox_folder, get_pref, set_pref
from lib.windows import UpShotWindowController


DEFAULTS = {
    'randomize': True,  # Randomize screenshot names?
    'copyonly': False,  # Copy (don't move) screen shots.
}


class PreferencesWindowController(UpShotWindowController):
    nibfile = u'PreferenceWindow'

    randomize = objc.IBOutlet()
    copyonly = objc.IBOutlet()
    dropboxdir = objc.IBOutlet()
    dropboxid = objc.IBOutlet()

    def showWindow_(self, sender):
        super(PreferencesWindowController, self).showWindow_(sender)
        self.updateDisplay()

    def updateDisplay(self):
        """Update window display from settings."""
        self.randomize.setState_(get_pref('randomize'))
        self.copyonly.setState_(get_pref('copyonly'))

        dropboxdir = detect_dropbox_folder()
        self.dropboxdir.setStringValue_(
            dropboxdir or u'None. Install Dropbox?')
        self.dropboxid.setStringValue_(get_pref('dropboxid'))

    @objc.IBAction
    def saveSettings_(self, sender):
        """Save changed settings."""
        set_pref('randomize', bool(self.randomize.state()))
        set_pref('copyonly', bool(self.copyonly.state()))
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
