# thetranscriber

Hold a key, speak, release: your words are typed where the cursor is. Runs locally on your Mac with Whisper; no audio leaves the machine.

## Setup

Needs Python 3.12+. If you only have an older one, `uv` downloads 3.12 for you:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Menu-bar app (recommended):

```bash
python menubar.py
```

Or the terminal version (optionally pass a language):

```bash
python transcriber.py Italian
```

The first run downloads the Whisper model (`small`, about 460 MB) from Hugging Face. The icon shows ⏳ while it loads.

## macOS permissions (one time)

System Settings → Privacy & Security, then allow your terminal app under:
- **Microphone** (to hear you)
- **Accessibility** (to press Cmd+V)
- **Input Monitoring** (to see the hotkey)

Restart the terminal after granting them.

## Use

Hold **right Option**, speak, release. In the menu bar: 🎙 ready, 🔴 listening, ⏳ working, ⚠️ a problem (the first menu line says what).

- **Language:** Auto-detect, English, Italian, Spanish, French, German or Portuguese (menu, or the first argument of `transcriber.py`). Add more in `LANGUAGES` in `dictation.py`.
- **Clean up filler words:** removes "um", "uh", "erm", "ehm", "hmm", fixes spacing and capitalises sentences. Toggle it in the menu.
- Change `HOTKEY` or `MODEL_NAME` at the top of `dictation.py` (`base` is faster, `medium` more accurate).

## Privacy and security

- Audio stays in memory, is never written to disk, and is dropped after each transcription. Transcripts are never printed or logged.
- Recording stops by itself after 2 minutes, in case a key-release event is lost.
- The paste uses your clipboard. The transcript is marked as transient so well-behaved clipboard managers (Maccy, Alfred, Raycast) skip it, then your previous clipboard is restored, including images and files. If you copy something else during the half second of the paste, your new copy is kept.
- If you switch to another app before transcription finishes, the text is **not** pasted. It stays on the clipboard so you can paste it yourself.
- **Input Monitoring lets the process see all keystrokes.** The code reads only the hotkey and stores nothing, but the permission is broad, so read the code (about 200 lines) before granting it.
- Permissions granted to "your terminal app" cover everything you run in that terminal, not just this app.
- Dependencies are pinned. For hash-checked installs, run `pip-compile --generate-hashes` and install with `--require-hashes`.
- The Whisper model is downloaded from Hugging Face at its latest revision, not a pinned one.

## Test

```bash
python test_cleanup.py
```

## Limits

Not yet tested end to end on a Mac; the pasteboard code in `macos.py` in particular needs a real run. Auto-detect can guess wrong on short clips, so pick a language if you always speak one. Cleanup only knows English and Italian hesitation sounds.
