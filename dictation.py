"""Shared engine: hold the hotkey, speak, release, and the transcript is pasted at the cursor.

Runs fully on your Mac (Whisper via faster-whisper); no audio leaves the machine.
"""
import sys
import threading

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard

from cleanup import clean
from macos import frontmost_app_pid, paste_text

HOTKEY = keyboard.Key.alt_r  # hold right Option
MODEL_NAME = "small"  # multilingual; "base" is faster, "medium" more accurate
SAMPLE_RATE = 16_000
MIN_SECONDS = 0.3  # ignore accidental taps
MAX_RECORD_S = 120  # force-stop a recording whose key-release event never arrived

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
        self.error = None  # last failure, shown by the menu-bar app
        self._keys = keyboard.Controller()
        self._lock = threading.Lock()
        self._chunks = []
        self._stream = None
        self._timer = None
        self._held = False

    def listen(self):
        """Start the global hotkey listener in a background thread and return it."""
        listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        listener.start()
        return listener

    def _on_press(self, key):
        # Ignore key repeat, and ignore new presses while the last transcript is still being pasted.
        if key != HOTKEY or self._held or self.state != "idle":
            return
        try:
            self._start_recording()
        except Exception as e:  # a raising callback would stop pynput's listener for good
            self._fail("could not start recording", e)

    def _on_release(self, key):
        if key == HOTKEY:
            self._release()

    def _start_recording(self):
        with self._lock:
            self._chunks = []
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                callback=lambda indata, frames, t, status: self._chunks.append(indata.copy()),
            )
            stream.start()
            self._stream = stream
            self._held = True
            self.state = "listening"
            self.error = None
            self._timer = threading.Timer(MAX_RECORD_S, self._release)
            self._timer.daemon = True
            self._timer.start()

    def _release(self):
        try:
            with self._lock:
                if not self._held:
                    return
                audio = self._stop_recording()
                target_pid = frontmost_app_pid()
        except Exception as e:
            self._fail("could not stop recording", e)
            return
        threading.Thread(target=self._finish, args=(audio, target_pid), daemon=True).start()

    def _stop_recording(self):
        """Always closes the microphone, even if stop() raises. Call with the lock held."""
        self._held = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        stream, self._stream = self._stream, None
        chunks, self._chunks = self._chunks, []  # drop the buffer so audio does not linger in memory
        self.state = "working"
        try:
            stream.stop()
        finally:
            stream.close()
        return np.concatenate(chunks).flatten() if chunks else np.zeros(0, dtype="float32")

    def _finish(self, audio, target_pid):
        try:
            text = self.transcribe(audio)
            if text:
                paste_text(text, lambda: self._press_paste(), target_pid)
        except Exception as e:
            self._fail("transcription failed", e)
        finally:
            self.state = "idle"

    def _press_paste(self):
        with self._keys.pressed(keyboard.Key.cmd):
            self._keys.tap("v")

    def transcribe(self, audio):
        if len(audio) < MIN_SECONDS * SAMPLE_RATE:
            return ""
        segments, _ = self.model.transcribe(audio, language=self.language, beam_size=1, vad_filter=True)
        text = " ".join(s.text.strip() for s in segments).strip()
        return clean(text) if self.cleanup else text

    def _fail(self, what, exc):
        """Record the problem (never the transcript) and get back to a usable state."""
        self.error = f"{what}: {exc}"
        print(self.error, file=sys.stderr)
        with self._lock:
            self._held = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
            stream, self._stream = self._stream, None
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
        self.state = "idle"
