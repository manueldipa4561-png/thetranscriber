"""Terminal version: hold right Option, speak, release. See menubar.py for the menu-bar app."""
import sys

from dictation import LANGUAGES, MODEL_NAME, Dictation

if __name__ == "__main__":
    engine = Dictation(MODEL_NAME)
    if len(sys.argv) > 1:  # e.g. `python transcriber.py Italian`
        label = sys.argv[1].capitalize()
        if label not in LANGUAGES:
            sys.exit(f"Unknown language {sys.argv[1]!r}. Choose from: {', '.join(LANGUAGES)}")
        engine.language = LANGUAGES[label]
    print(f"Ready. Hold right Option, speak, release. Model: {MODEL_NAME}. Ctrl-C to quit.")
    engine.listen().join()
