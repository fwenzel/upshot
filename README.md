UpShot
======

![](https://raw.github.com/fwenzel/upshot/master/upshot.png)

UpShot is an automatic screen shot uploader for OS X, written in Python.

> *Note:*  UpShot was only tested with OS X 10.7 -- Help porting it to 10.8 (or even back to 10.6, if that's desirable) will be greatly appreciated.
> As always, pull requests and Issues on [github][github] are welcome!

[github]: https://github.com/fwenzel/upshot/


Features
--------
It's pretty basic right now:

* Listens to a new screenshot being created with OS X's default screenshot function.
* Gives that screenshot a random filename and moves it to your public Dropbox folder.
* Copies that public Dropbox URL to your clipboard.

You can find *planned* features (or suggest your own!) on [github issues][issues]. The biggest feature currently planned (why I wrote this in the first place) is [supporting a custom domain name][domainname].

[issues]: https://github.com/fwenzel/upshot/issues
[domainname]: https://github.com/fwenzel/upshot/issues/16


Compiling it
------------
UpShot uses a [fabric][fabric] script for build and maintenance tasks:

1. Create a [virtualenv][virtualenv].
2. ``pip install -r requirements.txt``
3. ``fab build``

This will build an app package in the directory ``dist``. You can execute it from there. If you want to see console output, start it via ``fab run`` instead.

[fabric]: http://fabfile.org/
[virtualenv]: http://www.virtualenv.org/

> *Note:* Your virtualenv might not contain libpython2.x.dylib and thus cause an error. You can simply ``cd $VIRTUAL_ENV`` and ``ln -s /path/to/libpython2.7.dylib`` as a workaround.


Configuration
-------------
The latest version has a configuration screen, but not everything is configurable yet. For a full list, check out ``upshot.py`` for constants. You can override all those in a (new) file ``settings_local.py``.


Acknowledgments
---------------
* Thanks to David Vignoni for his [upload icon][icon].

[icon]: http://www.iconfinder.com/icondetails/1858/32/


License
-------
UpShot is released under a BSD license. Read the file ``LICENSE`` for more information.

---

Copyright (c) 2012 [Fred Wenzel](http://fredericiana.com).
