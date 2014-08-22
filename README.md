UpShot
======

![](https://raw.github.com/fwenzel/upshot/master/upshot.png)

UpShot is an automatic screen shot uploader for OS X, written in Python.

For sharing, UpShot uses Dropbox's Public folder, giving you maximum control over what you share.

**For more information and to download UpShot, visit the [UpShot website][upshot].** If you want to contribute to UpShot or check out its source code, read on.

[upshot]: http://upshot.it

Features
--------
The basic workflow is this:

* UpShot listens to a new screenshot being created with OS X's default screenshot function.
* It moves that screenshot to your public Dropbox folder.
* It copies that public Dropbox URL to your clipboard.

Other features currently include:

* Custom domain name support (some "assembly" required)
* randomized filenames


Contributing
------------
UpShot is an open source project. [Issues / pull requests][issues], feedback, feature requests, …, are greatly appreciated!

[issues]: https://github.com/fwenzel/upshot/issues


Compiling it
------------
UpShot uses a [fabric][fabric] script for build and maintenance tasks:

1. Create a [virtualenv][virtualenv].
2. ``pip install -r requirements.txt``
3. ``fab build``

This will build an app package in the directory ``dist``. You can execute it from there. If you want to see console output, start it via ``fab run`` instead.

[fabric]: http://fabfile.org/
[virtualenv]: http://www.virtualenv.org/

> *Note:* Your virtualenv might not contain libpython2.x.dylib and thus cause an error. You can simply ``cd $VIRTUAL_ENV`` and ``ln -s /path/to/libpython2.x.dylib`` as a workaround.


Configuration
-------------
The latest version has a configuration screen, but not everything is configurable yet. For a full list, check out ``upshot.py`` for constants. You can override all those in a (new) file ``settings_local.py``.


Acknowledgments
---------------
Thanks to:

* David Vignoni for his [upload icon][icon].
* Jason Costello for [Slate][slate], the website theme that upshot.it uses.

[icon]: http://www.iconfinder.com/icondetails/1858/32/
[slate]: https://github.com/jsncostello/slate


License
-------
UpShot is released under a BSD license. Read the file ``LICENSE`` for more information.

---

Copyright (c) 2012-2014 [Fred Wenzel](http://fredericiana.com).
