"""Hold the hotkey, speak, release: the transcript is pasted at your cursor.

Runs fully on your Mac (Whisper via faster-whisper); no audio leaves the machine.
"""
import subprocess
import threading
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard

HOTKEY = keyboard.Key.alt_r  # hold right Option
MODEL_NAME = "base.en"  # "small.en" is more accurate but slower
SAMPLE_RATE = 16_000
MIN_SECONDS = 0.3  # ignore accidental taps
PASTE_DELAY_S = 0.15  # let the clipboard settle before pasting

model = WhisperModel(MODEL_NAME, compute_type="int8")
keys = keyboard.Controller()
chunks = []
stream = None


def on_audio(indata, frames, time_info, status):
    chunks.append(indata.copy())


def start_recording():
    global stream
    chunks.clear()
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=on_audio)
    stream.start()


def stop_recording():
    global stream
    stream.stop()
    stream.close()
    stream = None
    return np.concatenate(chunks).flatten() if chunks else np.zeros(0, dtype="float32")


def transcribe(audio):
    if len(audio) < MIN_SECONDS * SAMPLE_RATE:
        return ""
    segments, _ = model.transcribe(audio, language="en", beam_size=1, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


def paste(text):
    """Put text on the clipboard, press Cmd+V, then restore what was there."""
    previous = subprocess.run(["pbpaste"], capture_output=True).stdout
    subprocess.run(["pbcopy"], input=text.encode())
    time.sleep(PASTE_DELAY_S)
    with keys.pressed(keyboard.Key.cmd):
        keys.tap("v")
    time.sleep(PASTE_DELAY_S)
    subprocess.run(["pbcopy"], input=previous)


def finish(audio):
    text = transcribe(audio)
    if text:
        paste(text)
        print(text)


held = False


def on_press(key):
    global held
    if key == HOTKEY and not held:  # key repeat fires press again; ignore it
        held = True
        start_recording()


def on_release(key):
    global held
    if key == HOTKEY and held:
        held = False
        threading.Thread(target=finish, args=(stop_recording(),), daemon=True).start()


if __name__ == "__main__":
    print(f"Ready. Hold right Option, speak, release. Model: {MODEL_NAME}. Ctrl-C to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
