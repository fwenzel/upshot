import objc
from Foundation import *

import utils


DEFAULTS = {
    'randomize': True,
}


class PreferencesWindowController(NSWindowController):
    randomize = objc.IBOutlet()
    _singleton = None

    @classmethod
    def showPreferencesWindow(cls):
        """Create window as a singleton and return."""
        if not cls._singleton:
            cls._singleton = PreferencesWindowController.alloc().init()
        cls._singleton.window().center()
        cls._singleton.showWindow_(cls._singleton)
        return cls._singleton

    def init(self):
        return self.initWithWindowNibName_(u'PreferenceWindow')

    def updateDisplay(self):
        """Update window display from settings."""
        self.randomize.setState_(get_pref('randomize'))

    @objc.IBAction
    def saveSettings_(self, sender):
        """Save changed settings."""
        set_pref('randomize', bool(self.randomize.state()))

    def awakeFromNib(self):
        self.updateDisplay()


def set_defaults():
    """
    Perform some sanity checks on our preferences and set defaults for those
    that aren't set.
    """
    for key, val in DEFAULTS.items():
        get_pref(key, default=val, setdefault=True)


@utils.autopooled
def get_pref(key, default=None, setdefault=False, domain=None):
    """
    Read a user pref, possibly from another domain.
    setdefault will set pref to default value if not found.
    """
    user_defaults = NSUserDefaults.standardUserDefaults()
    if domain is not None:
        user_defaults = user_defaults.persistentDomainForName_(domain)
    try:
        return user_defaults[key]
    except (TypeError, KeyError):
        if setdefault and domain is None:
            set_pref(key, default)
        # If domain or key were not found, fall back.
        return default


@utils.autopooled
def set_pref(key, val):
    """Set a user pref in the current domain."""
    user_defaults = NSUserDefaults.standardUserDefaults()
    user_defaults.setObject_forKey_(val, key)
