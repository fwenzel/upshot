import objc
from AppKit import *
from Foundation import *


class UpShotWindowController(NSWindowController):
    """Common code for preferences window and others."""
    nibfile = None  # Must be overridden in subclasses.
    _singleton = None

    @classmethod
    def showWindow(cls, app=None):
        """Create window as a singleton and return."""
        if not cls._singleton:
            cls._singleton = cls.alloc().init()

        NSApp.activateIgnoringOtherApps_(True)

        cls._singleton.window().center()
        cls._singleton.showWindow_(cls._singleton)
        return cls._singleton

    def init(self):
        return self.initWithWindowNibName_(self.nibfile)


class Alert(object):
    """
    Show an alert window.
    Courtesy of https://gist.github.com/1083908.
    """
    buttons = []
    informative_text = ''
    message_text = ''

    def __init__(self, message_text, info_text, buttons):
        super(Alert, self).__init__()
        self.buttons = buttons
        self.informative_text = info_text
        self.message_text = message_text

    def displayAlert(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_(self.message_text)
        alert.setInformativeText_(self.informative_text)
        alert.setAlertStyle_(NSInformationalAlertStyle)
        for button in self.buttons:
            alert.addButtonWithTitle_(button)
        NSApp.activateIgnoringOtherApps_(True)
        self.buttonPressed = alert.runModal()


def alert(message='Default Message', info_text='', buttons=['OK']):
    ap = Alert(message, info_text, buttons)
    ap.displayAlert()
    return ap.buttonPressed
