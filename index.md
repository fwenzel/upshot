---
layout: default
versions:
- [1.0, 12/13/2012]
- [0.9.1, 12/5/2012]
- [0.9, 11/25/2012]
---

**UpShot** combines the power of OS X's built-in screenshot functionality with Dropbox. This makes UpShot the easiest way to automatically upload and share screenshots on OS X.

**It's as easy as 1 - 2 - 3!**

1. You **take a screenshot**
2. The screenshot URL shows up in your clipboard, **ready to be pasted** wherever you want.
3. Actually, there is no step 3!

<div id="dlbutton">
<a href="'http://dl.upshot.it/UpShot-{{ page.versions|first|first }}.dmg" class="button">Download UpShot</a>
<p>.dmg file, version {{ page.versions|first|first }}, {{ page.versions|first|last}}</p>
</div>

### Installing UpShot
* Download the DMG file above, double click to open
* drag the UpShot app into your ``/Applications`` directory (overwrite the existing version when updating).
* go to the Applications directory and start UpShot from there. UpShot will show up in your status bar in the top right corner of the screen.

### Screenshots
<div id="screenshots">
<a href="images/upshot-menu.png" rel="lightbox[s]" title="The main titlebar menu"><img src="images/upshot-menu.png"></a>
<a href="images/preferences.png" rel="lightbox[s]" title="UpShot's preferences screen"><img src="images/preferences.png"></a>
</div>

### Version History
For a summary of what changed between versions, check out the [changelog][changelog].

If you know what you're doing, you may download previous versions here:

{% for v in page.versions %}
* [v{{ v|first }} ({{ v|last }})](http://dl.upshot.it/UpShot-{{ v|first }}.dmg){% endfor %}

[changelog]: https://github.com/fwenzel/upshot/blob/master/CHANGELOG.md
[1.0]: {{ latest }}
[0.9.1]: http://dl.upshot.it/UpShot-0.9.1.dmg
[0.9]: http://dl.upshot.it/UpShot-0.9.dmg

### Contributing

UpShot is an open source project on [Github][upshot-gh], written in Python. Issues and Pull Requests are highly appreciated!

The [README][readme] file also has additional technical info on how UpShot works.

[upshot-gh]: https://github.com/fwenzel/upshot/
[readme]: https://github.com/fwenzel/upshot#readme

### License
Copyright (c) {{ 'now' | date: '%Y' }} [Fred Wenzel](http://fredericiana.com).

UpShot is released under a BSD license. Read the file [``LICENSE``][license] for more information.

[license]: https://github.com/fwenzel/upshot/blob/master/LICENSE
