"""Shared engine: hold the hotkey, speak, release, and the transcript is pasted at the cursor.

Runs fully on your Mac (Whisper via faster-whisper); no audio leaves the machine.
"""
import subprocess
import threading
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard

from cleanup import clean

HOTKEY = keyboard.Key.alt_r  # hold right Option
MODEL_NAME = "small"  # multilingual; "base" is faster, "medium" more accurate
SAMPLE_RATE = 16_000
MIN_SECONDS = 0.3  # ignore accidental taps
PASTE_DELAY_S = 0.15  # let the clipboard settle before pasting

# Label -> Whisper language code. None lets Whisper detect the language itself.
LANGUAGES = {
    "Auto-detect": None,
    "English": "en",
    "Italian": "it",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
}


class Dictation:
    def __init__(self, model_name=MODEL_NAME):
        self.model = WhisperModel(model_name, compute_type="int8")
        self.language = None
        self.cleanup = True
        self.state = "idle"  # idle, listening or working
        self._keys = keyboard.Controller()
        self._chunks = []
        self._stream = None
        self._held = False

    def listen(self):
        """Start the global hotkey listener in a background thread and return it."""
        listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        listener.start()
        return listener

    def _on_press(self, key):
        if key == HOTKEY and not self._held:  # key repeat fires press again; ignore it
            self._held = True
            self._start_recording()

    def _on_release(self, key):
        if key == HOTKEY and self._held:
            self._held = False
            audio = self._stop_recording()
            threading.Thread(target=self._finish, args=(audio,), daemon=True).start()

    def _start_recording(self):
        self._chunks = []
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32",
            callback=lambda indata, frames, t, status: self._chunks.append(indata.copy()),
        )
        self._stream.start()
        self.state = "listening"

    def _stop_recording(self):
        self._stream.stop()
        self._stream.close()
        self._stream = None
        self.state = "working"
        return np.concatenate(self._chunks).flatten() if self._chunks else np.zeros(0, dtype="float32")

    def _finish(self, audio):
        try:
            text = self.transcribe(audio)
            if text:
                self._paste(text)
                print(text)
        finally:
            self.state = "idle"

    def transcribe(self, audio):
        if len(audio) < MIN_SECONDS * SAMPLE_RATE:
            return ""
        segments, _ = self.model.transcribe(audio, language=self.language, beam_size=1, vad_filter=True)
        text = " ".join(s.text.strip() for s in segments).strip()
        return clean(text) if self.cleanup else text

    def _paste(self, text):
        """Put text on the clipboard, press Cmd+V, then restore what was there."""
        previous = subprocess.run(["pbpaste"], capture_output=True).stdout
        subprocess.run(["pbcopy"], input=text.encode())
        time.sleep(PASTE_DELAY_S)
        with self._keys.pressed(keyboard.Key.cmd):
            self._keys.tap("v")
        time.sleep(PASTE_DELAY_S)
        subprocess.run(["pbcopy"], input=previous)
