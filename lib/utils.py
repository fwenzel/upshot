from functools import wraps

from AppKit import NSArray, NSAutoreleasePool, NSPasteboard


def autopooled(f):
    """
    Decorator to keep threads from leaking in ObjC.
    http://pyobjc.sourceforge.net/documentation/pyobjc-core/intro.html#working-with-threads
    """
    @wraps(f)
    def pooled_func(*args, **kwargs):
        pool = NSAutoreleasePool.alloc().init()
        f(*args, **kwargs)
        del pool
    return pooled_func


@autopooled
def pbcopy(s):
    """Copy text to the OS X clipboard."""
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    a = NSArray.arrayWithObject_(s)
    pb.writeObjects_(a)
