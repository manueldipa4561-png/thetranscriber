# thetranscriber

Hold a key, speak, release: your words are typed where the cursor is. Runs locally on your Mac with Whisper; no audio leaves the machine.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Menu-bar app (recommended):

```bash
python menubar.py
```

Or the terminal version (optionally pass a language):

```bash
python transcriber.py Italian
```

The first run downloads the Whisper model (`small`, about 460 MB). The icon shows ⏳ while it loads.

## macOS permissions (one time)

System Settings → Privacy & Security, then allow your terminal app under:
- **Microphone** (to hear you)
- **Accessibility** and **Input Monitoring** (to see the hotkey and press Cmd+V)

Restart the terminal after granting them.

## Use

Hold **right Option**, speak, release. In the menu bar: 🎙 ready, 🔴 listening, ⏳ working.

- **Language:** Auto-detect, English, Italian, Spanish, French, German or Portuguese (menu, or the first argument of `transcriber.py`). Add more in `LANGUAGES` in `dictation.py`.
- **Clean up filler words:** removes "um", "uh", "erm", "ehm", "hmm", fixes spacing and capitalises sentences. Toggle it in the menu.
- Change `HOTKEY` or `MODEL_NAME` at the top of `dictation.py` (`base` is faster, `medium` more accurate).

## Test

```bash
python test_cleanup.py
```

## Limits

Not yet tested end to end on a Mac. Auto-detect can guess wrong on short clips, so pick a language if you always speak one. Cleanup only knows English and Italian hesitation sounds.
