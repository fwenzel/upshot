UpShot
======

![](https://raw.github.com/fwenzel/upshot/master/upshot.png)

UpShot is an automatic screen shot uploader for OS X, written in Python.

> *Note:* This is experimental software and probably does not do what you want yet without massaging the source code.
> This is going to change over time and become more convenient to use.
> As always, pull requests and Issues on github are welcome!

Features
--------
It's pretty basic right now:
* Listens to a new screenshot being created with OS X's default screenshot function.
* Gives that screenshot a random filename and moves it to your public Dropbox folder.
* Copies that public Dropbox URL to your clipboard.

How to run it
-------------
1. Create a [virtualenv][virtualenv].
2. ``pip install -r requirements.txt``
3. ``python setup.py py2app``

This will build an app package in the directory ``dist``. You can execute it from there. If you want to see console output, start it via ``./dist/UpShot.app/Contents/MacOS/UpShot`` instead.

[virtualenv]: http://www.virtualenv.org/

> *Note:* Your virtualenv might not contain libpython2.x.dylib and thus cause an error. You can simply ``cd $VIRTUAL_ENV`` and ``ln -s /path/to/libpython2.7.dylib`` as a workaround.

Configuration
-------------
The latest version has a configuration screen, but not everything is configurable yet. For a full list, check out ``upshot.py`` for constants. You can override all those in a (new) file ``settings_local.py``.

The most important setting you want to change is ``SHARE_URL``. Set it to
``http://dl.dropbox.com/u/XXXXXXXX/Screenshots/``, where ``XXXXXXXX`` is your
public dropbox ID number.

Acknowledgments
---------------
* Thanks to David Vignoni for his [upload icon][icon].

[icon]: http://www.iconfinder.com/icondetails/1858/32/

License
-------
UpShot is released under a BSD license. Read the file ``LICENSE`` for more information.

---

Copyright (c) 2012 [Fred Wenzel](http://fredericiana.com).
