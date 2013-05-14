import objc
from Foundation import *
from LaunchServices import *

import DropboxDetect
from lib.utils import detect_dropbox_folder, get_pref, set_pref, share_url
from lib.windows import UpShotWindowController


DEFAULTS = {
    'launchAtStartup': True,
    'iconset': 'default',  # Which status bar icon? 'default' or 'grayscale'
    'randomize': True,  # Randomize screenshot names?
    'copyonly': False,  # Copy (don't move) screen shots.
    'retinascale': False,  # Scale upscaled retina images to low DPI automatically.
    'customurl': '',  # Empty string means: default Dropbox URL.
}
DOMAIN_HELP_URL = ('http://fredericiana.com/2012/12/09/'
                   'custom-domain-with-dropbox/')
EXAMPLE_FILENAME = 'hZr9.png'


class PreferencesWindowController(UpShotWindowController):
    nibfile = u'PreferenceWindow'

    # General
    launchAtStartup = objc.IBOutlet()
    iconset = objc.IBOutlet()

    # Screenshots
    randomize = objc.IBOutlet()
    copyonly = objc.IBOutlet()
    retinascale = objc.IBOutlet()

    # Dropbox metadata
    dropboxdir = objc.IBOutlet()
    dropboxid = objc.IBOutlet()

    # Custom share URLs
    url_select = objc.IBOutlet()
    url_text = objc.IBOutlet()
    url_example = objc.IBOutlet()

    def showWindow_(self, sender):
        super(PreferencesWindowController, self).showWindow_(sender)
        self.updateDisplay()

    def updateDisplay(self):
        """Update window display from settings."""
        self.launchAtStartup.setState_(get_pref('launchAtStartup'))
        self.iconset.selectCellWithTag_(
            1 if get_pref('iconset') == 'grayscale' else 0)

        self.randomize.setState_(get_pref('randomize'))
        self.copyonly.setState_(get_pref('copyonly'))
        self.copyonly.setState_(get_pref('retinascale'))

        dropboxdir = detect_dropbox_folder()
        self.dropboxdir.setStringValue_(
            dropboxdir or u'None. Install Dropbox?')
        self.dropboxid.setStringValue_(get_pref('dropboxid'))

        customurl = get_pref('customurl')
        if not customurl:  # Default.
            self.url_select.selectCellWithTag_(0)
            self.url_text.setEnabled_(False)
            self.url_text.setStringValue_('')
            self.url_example.setStringValue_(share_url(EXAMPLE_FILENAME,
                                                       url=''))
        else:  # Custom.
            self.url_select.selectCellWithTag_(1)
            self.url_text.setEnabled_(True)
            self.url_text.setStringValue_(customurl)
            self.url_example.setStringValue_(share_url(EXAMPLE_FILENAME,
                                                       url=customurl))

    @objc.IBAction
    def saveSettings_(self, sender):
        """Save changed settings."""
        set_pref('launchAtStartup', bool(self.launchAtStartup.state()))
        launch_at_startup(bool(self.launchAtStartup.state()))

        # Iconset
        iconset_sel = self.iconset.selectedCell().tag()
        if iconset_sel == 1:  # Grayscale
            set_pref('iconset', 'grayscale')
        else:
            set_pref('iconset', 'default')
        upshot = NSApplication.sharedApplication().delegate()
        upshot.update_menu()

        set_pref('randomize', bool(self.randomize.state()))
        set_pref('copyonly', bool(self.copyonly.state()))
        set_pref('retinascale', bool(self.retinascale.state()))

        try:
            set_pref('dropboxid', int(self.dropboxid.stringValue()))
        except ValueError:
            pass

        # Custom URL settings.
        if self.url_select.selectedCell().tag() == 0:  # Default
            self.url_text.setStringValue_('')
            self.url_text.setEnabled_(False)
            self.url_example.setStringValue_(share_url(EXAMPLE_FILENAME,
                                                       url=''))
            set_pref('customurl', '')
        else:  # Custom
            self.url_text.setEnabled_(True)
            self.url_example.setStringValue_(
                share_url(EXAMPLE_FILENAME, url=self.url_text.stringValue()))
            set_pref('customurl', self.url_text.stringValue())

    @objc.IBAction
    def dropboxDetect_(self, sender):
        """Open dropbox detection window."""
        DropboxDetect.DropboxDetectWindowController.showWindow()
        self.close()

    @objc.IBAction
    def domainHelp_(self, sender):
        """Open URL to learn about custom domain setup with Dropbox."""
        sw = NSWorkspace.sharedWorkspace()
        sw.openURL_(NSURL.URLWithString_(DOMAIN_HELP_URL))


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
