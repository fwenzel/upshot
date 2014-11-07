import os

import objc
from Foundation import *

from lib.logger import log


# Darwin 12.0 is OS X 10.8, and so forth
try:
    # uname is (sysname, nodename, release, version, machine)
    OS_VERSION = os.uname()[3].split('.')[0]
except:
    OS_VERSION = 0


class CommonNotifier(NSObject):
    """Shared code between notifiers."""

    callbacks = {}  # References to callback handlers.

    def register_callback(self, callback):
        """
        Callback is a callable we want to hold on to for later click handling.
        It'll be stored as a weak reference (i.e., garbage collectable) in
        self.callbacks.

        Returns serializable callback ID.
        """
        callback_id = str(callback.__hash__())

        # XXX: We're not cleaning these up because more than one notification
        # will have the same handler. If we do this a lot, this will leak memory.
        self.callbacks[callback_id] = callback

        log.debug('Registered callback ID %s' % callback_id)
        return callback_id


    def click_handler(self, context):
        """
        Handle a click by handing context data back to a previously registered
        callback.

        context is 'callback_id:string', e.g., '12345:/a/path/to/open'.
        """
        if not context:
            return

        callback_id, data = context.split(':', 1)

        callback = self.callbacks.get(callback_id)
        if callback:
            log.debug('Click callback %s with context %s' % (
                callback.__name__, data))
            callback(data)


class Growler(CommonNotifier):
    """Growl wrapper."""

    def init(self):
        self = super(Growler, self).init()
        self.name = 'UpShot'
        objc.loadBundle(
            'GrowlApplicationBridge', globals(), bundle_path=os.path.join(
                NSBundle.mainBundle().privateFrameworksPath(),
                'Growl.framework'))

        self._growl = GrowlApplicationBridge
        self._growl.setGrowlDelegate_(self)

        return self

    def growlNotificationWasClicked_(self, context):
        if context:
            self.click_handler(context)

    def notify(self, title='', description='', context=None):
        GrowlApplicationBridge.notifyWithTitle_description_notificationName_iconData_priority_isSticky_clickContext_(
            #title, description, self.name,
            NSString.stringWithString_(title),
            NSString.stringWithString_(description),
            NSString.stringWithString_(self.name),
            None, 0, False, context or '')


class OSXNotifier(CommonNotifier):
    """Notification Center wrapper."""
    _center = None

    def init(self):
        self = super(OSXNotifier, self).init()

        self._center = NSUserNotificationCenter.defaultUserNotificationCenter()
        self._center.setDelegate_(self)

        return self

    def userNotificationCenter_didActivateNotification_(self, center, notification):
        """Handle click."""
        context = notification.userInfo()
        if context:
            self.click_handler(context['data'])

    def notify(self, title='', description='', context=None):
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        #notification.setSubtitle_(title)
        notification.setInformativeText_(description)

        if context:
            notification.setUserInfo_({'data': context})

        self._center.deliverNotification_(notification)


_notifier = None  # Singleton.
def notify(title='', description='', context=None, callback=None):
    """Fire a notification to the right notification service."""
    global _notifier

    # Initialize notification center.
    if not _notifier:
        if OS_VERSION >= 12:
            _notifier = OSXNotifier.alloc().init()
        else:
            _notifier = Growler.alloc().init()

    # Register callback handler and store its ID in the serializable context
    # data.
    if callback:
        callback_id = _notifier.register_callback(callback)
        ctx = ':'.join(map(str, (callback_id, context)))
    else:
        ctx = None

    _notifier.notify(title, description, ctx)
