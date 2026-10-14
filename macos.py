"""macOS helpers: a clipboard-safe paste and a frontmost-app lookup (pyobjc, installed with rumps)."""
import threading
import time

from AppKit import NSPasteboard, NSPasteboardItem, NSPasteboardTypeString, NSWorkspace

TRANSIENT_TYPE = "org.nspasteboard.TransientType"  # clipboard managers skip entries marked with this
PASTE_DELAY_S = 0.15  # let the pasteboard settle before pressing Cmd+V
RESTORE_DELAY_S = 0.5  # slow apps (Electron, remote desktop) read the clipboard a moment after Cmd+V

_lock = threading.Lock()  # one paste at a time, so a second paste never snapshots our transcript


def frontmost_app_pid():
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    return app.processIdentifier() if app else None


def _snapshot(pasteboard):
    """Every item with every type's raw data, so images, files and rich text survive."""
    return [{t: item.dataForType_(t) for t in item.types()} for item in (pasteboard.pasteboardItems() or [])]


def _restore(pasteboard, snapshot):
    pasteboard.clearContents()
    items = []
    for entry in snapshot:
        item = NSPasteboardItem.alloc().init()
        for type_, data in entry.items():
            if data is not None:
                item.setData_forType_(data, type_)
        items.append(item)
    if items:
        pasteboard.writeObjects_(items)


def paste_text(text, press_paste, target_pid):
    """Paste text into the focused app, then restore the previous clipboard.

    Returns False and leaves the text on the clipboard (no auto paste) if focus moved to another
    app since recording ended, so dictated text never lands in the wrong window.
    The old clipboard is not restored if you copied something else in the meantime.
    """
    with _lock:
        pasteboard = NSPasteboard.generalPasteboard()
        snapshot = _snapshot(pasteboard)
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, NSPasteboardTypeString)
        pasteboard.setString_forType_("", TRANSIENT_TYPE)
        ours = pasteboard.changeCount()
        if frontmost_app_pid() != target_pid:
            return False
        try:
            time.sleep(PASTE_DELAY_S)
            press_paste()
            time.sleep(RESTORE_DELAY_S)
        finally:
            if pasteboard.changeCount() == ours:
                _restore(pasteboard, snapshot)
        return True
