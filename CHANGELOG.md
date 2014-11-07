UpShot Changelog
================

master
------
* New icon, retina and dark mode compatible. Fix #48. Fix #41.
* Updated and fixed background image for DMG file. Fix #61.
* Added menu item to search for updates. Fix #54.
* Log with Growl on 10.7, with notification center on 10.8 and up. Fix #59.
* Use windowDidLoad rather than override showWindow. Fix #62.
* Never die while processing a screenshot, log exceptions as needed. Fix #38.

v2.0 (8/22/2014)
----------------
* Allow auto-scaling of retina screenshots down to 72dpi. Fix #44.
* Add automated update service (Sparkle!). Fix #14.
* Do not say "paused" when quitting. Fix #51.

v1.1 (4/26/2013)
----------------
* Dropbox v2 support:
  * Detect user ID out of Dropbox v2 urls. Fix #46.
  * Generate dropboxusercontent.com URLs by default.

v1.0.1 (12/15/2012)
-------------------
* Change project website link to upshot.it. Fix #34.
* Only handle files for 15 seconds after their creation, to not suck in files we did not create. Fix #26.
* Don't complain if a Screenshots folder does not exist. Fix #35.

v1.0 (12/13/2012)
-------------------
* Help users create public folders if they do not already have one. Fix #29.
* Add grayscale menu bar icon as a preference. Fix #31.
* Made share URLs customizable. Fix issue #16.
* Use temporary directory for creating DMG file. Fix #27.
* Some code cosmetics.

v0.9.1 (12/5/2012)
------------------
* Uploading worked for full-screen and per-window shots but not selections. Fix #28.

v0.9 (11/25/2012)
-----------------
* First public release
* Screenshot uploading to Dropbox
* randomized filenames
* growl notifications
