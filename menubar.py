"""Menu-bar version: a microphone icon that shows status, with language and cleanup settings."""
import threading

import rumps

from dictation import LANGUAGES, MODEL_NAME, Dictation

ICONS = {"loading": "⏳", "idle": "🎙", "listening": "🔴", "working": "⏳"}
POLL_S = 0.2


class MenuBarApp(rumps.App):
    def __init__(self):
        super().__init__(ICONS["loading"], quit_button="Quit")
        self.engine = None
        self.language_items = {label: rumps.MenuItem(label, callback=self.pick_language) for label in LANGUAGES}
        language_menu = rumps.MenuItem("Language")
        for item in self.language_items.values():
            language_menu.add(item)
        self.cleanup_item = rumps.MenuItem("Clean up filler words", callback=self.toggle_cleanup)
        self.cleanup_item.state = 1
        self.menu = [
            rumps.MenuItem("Hold right Option to dictate"),
            None,
            language_menu,
            self.cleanup_item,
        ]
        self.language_items["Auto-detect"].state = 1
        threading.Thread(target=self._load_engine, daemon=True).start()  # model load/download takes a while
        self.poll = rumps.Timer(self._refresh_icon, POLL_S)
        self.poll.start()

    def _load_engine(self):
        engine = Dictation(MODEL_NAME)
        engine.listen()
        self.engine = engine

    def _refresh_icon(self, _):
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
