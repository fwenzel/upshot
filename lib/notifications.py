import os

import objc
from Foundation import *


class Growler(NSObject):
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
        self._callback = lambda ctx: None
        return self

    def growlNotificationWasClicked_(self, context):
        self._callback(context)

    def setCallback(self, callback):
        self._callback = callback

    def notify(self, title='', description='', context=None):
        GrowlApplicationBridge.notifyWithTitle_description_notificationName_iconData_priority_isSticky_clickContext_(
            #title, description, self.name,
            NSString.stringWithString_(title),
            NSString.stringWithString_(description),
            NSString.stringWithString_(self.name),
            None, 0, False, context or NSDate.date())
