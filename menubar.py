"""Menu-bar version: a microphone icon that shows status, with language and cleanup settings."""
import sys
import threading

import rumps

from dictation import LANGUAGES, MODEL_NAME, Dictation

ICONS = {"loading": "⏳", "idle": "🎙", "listening": "🔴", "working": "⏳", "error": "⚠️"}
POLL_S = 0.2


class MenuBarApp(rumps.App):
    def __init__(self):
        super().__init__(ICONS["loading"], quit_button="Quit")
        self.engine = None
        self.load_error = None
        self.language_items = {label: rumps.MenuItem(label, callback=self.pick_language) for label in LANGUAGES}
        language_menu = rumps.MenuItem("Language")
        for item in self.language_items.values():
            language_menu.add(item)
        self.cleanup_item = rumps.MenuItem("Clean up filler words", callback=self.toggle_cleanup)
        self.cleanup_item.state = 1
        self.status_item = rumps.MenuItem("Hold right Option to dictate")
        self.menu = [self.status_item, None, language_menu, self.cleanup_item]
        self.language_items["Auto-detect"].state = 1
        threading.Thread(target=self._load_engine, daemon=True).start()  # model load/download takes a while
        self.poll = rumps.Timer(self._refresh, POLL_S)
        self.poll.start()

    def _load_engine(self):
        try:
            engine = Dictation(MODEL_NAME)
            engine.listen()
            self.engine = engine
        except Exception as e:  # no network for the first download, missing permission, ...
            self.load_error = f"could not start: {e}"
            print(self.load_error, file=sys.stderr)

    def _refresh(self, _):
        problem = self.load_error or (self.engine.error if self.engine else None)
        if problem:
            self.title, self.status_item.title = ICONS["error"], f"Problem: {problem}"
            return
        self.status_item.title = "Hold right Option to dictate"
        self.title = ICONS[self.engine.state] if self.engine else ICONS["loading"]

    def pick_language(self, sender):
        for item in self.language_items.values():
            item.state = 0
        sender.state = 1
        if self.engine:
            self.engine.language = LANGUAGES[sender.title]

    def toggle_cleanup(self, sender):
        sender.state = 0 if sender.state else 1
        if self.engine:
            self.engine.cleanup = bool(sender.state)


if __name__ == "__main__":
    MenuBarApp().run()
