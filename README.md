# thetranscriber

Hold a key, speak, release: your words are typed where the cursor is. Runs locally on your Mac with Whisper; no audio leaves the machine.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python transcriber.py
```

The first run downloads the Whisper model (`base.en`, about 140 MB).

## macOS permissions (one time)

System Settings → Privacy & Security, then allow your terminal app under:
- **Microphone** (to hear you)
- **Accessibility** and **Input Monitoring** (to see the hotkey and press Cmd+V)

Restart the terminal after granting them.

## Use

Hold **right Option**, speak, release. Change `HOTKEY` or `MODEL_NAME` at the top of `transcriber.py`.

## Limits

English only for now. The first transcription after launch is slower while the model warms up.
