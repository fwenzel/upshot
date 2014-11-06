"""Code related to auto-updating UpShot via a Sparkle app manifest."""
import os

import objc
from Foundation import *


class SparkleUpdater(NSObject):
    """
    Sparkle Updater wrapper.

    Overrides certain Sparkle updater behavior.
    Docs: https://github.com/andymatuschak/Sparkle/wiki/customization
    """

    def init(self):
        #super(SparkleUpdater, self).init()

        # Load Sparkle framework.
        bundle_path = os.path.join(
            NSBundle.mainBundle().privateFrameworksPath(),
            'Sparkle.framework')
        objc.loadBundle('Sparkle', globals(), bundle_path=bundle_path)

        self._sparkle = SUUpdater.sharedUpdater()
        self._sparkle.setDelegate_(self)
        return self

    def auto_update(self):
        """Check for updates in the background."""
        self._sparkle.checkForUpdatesInBackground()
