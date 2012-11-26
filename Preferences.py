import objc
from Foundation import *
from LaunchServices import *

import DropboxDetect
from lib.utils import detect_dropbox_folder, get_pref, set_pref
from lib.windows import UpShotWindowController


DEFAULTS = {
    'randomize': True,  # Randomize screenshot names?
    'copyonly': False,  # Copy (don't move) screen shots.
    'launchAtStartup': True,
}


class PreferencesWindowController(UpShotWindowController):
    nibfile = u'PreferenceWindow'

    randomize = objc.IBOutlet()
    copyonly = objc.IBOutlet()
    dropboxdir = objc.IBOutlet()
    dropboxid = objc.IBOutlet()
    launchAtStartup = objc.IBOutlet()

    def showWindow_(self, sender):
        super(PreferencesWindowController, self).showWindow_(sender)
        self.updateDisplay()

    def updateDisplay(self):
        """Update window display from settings."""
        self.randomize.setState_(get_pref('randomize'))
        self.copyonly.setState_(get_pref('copyonly'))
        self.launchAtStartup.setState_(get_pref('launchAtStartup'))

        dropboxdir = detect_dropbox_folder()
        self.dropboxdir.setStringValue_(
            dropboxdir or u'None. Install Dropbox?')
        self.dropboxid.setStringValue_(get_pref('dropboxid'))

    @objc.IBAction
    def saveSettings_(self, sender):
        """Save changed settings."""
        set_pref('randomize', bool(self.randomize.state()))
        set_pref('copyonly', bool(self.copyonly.state()))

        set_pref('launchAtStartup', bool(self.launchAtStartup.state()))
        launch_at_startup(bool(self.launchAtStartup.state()))

        try:
            set_pref('dropboxid', int(self.dropboxid.stringValue()))
        except ValueError:
            pass

    @objc.IBAction
    def dropboxDetect_(self, sender):
        """Open dropbox detection window."""
        DropboxDetect.DropboxDetectWindowController.showWindow(self.app)
        self.close()


def launch_at_startup(switch=True):
    """Add/remove from launch list."""
    loginitems = LSSharedFileListCreate(
        None, kLSSharedFileListSessionLoginItems, None)
    if switch:  # Add to list.
        app_url = NSBundle.mainBundle().bundleURL()
        LSSharedFileListInsertItemURL(loginitems, kLSSharedFileListItemLast,
                                      None, None, app_url, None, None)
    else:  # Remove from list.
        this_app = item_in_login_items()
        if this_app:
            LSSharedFileListItemRemove(loginitems, this_app)


def item_in_login_items():
    """Return item in login items list, if it is in there."""
    app_url = NSBundle.mainBundle().bundleURL()
    loginitems = LSSharedFileListCreate(
        None, kLSSharedFileListSessionLoginItems, None)
    itemlist = LSSharedFileListCopySnapshot(loginitems, None)[0]
    # Find this app in startup item list.
    inlist = next(
        (i for i in itemlist if
         LSSharedFileListItemResolve(i, 0, None, None)[1] == app_url), None)

    return inlist


def set_defaults():
    """
    Perform some sanity checks on our preferences and set defaults for those
    that aren't set.
    """
    for key, val in DEFAULTS.items():
        get_pref(key, default=val, setdefault=True)

    # Add or remove startup item.
    should_start = get_pref('launchAtStartup')
    if bool(item_in_login_items()) != should_start:
        launch_at_startup(should_start)
