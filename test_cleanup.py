from cleanup import clean

CASES = [
    ("Um, so, uh, I think, um, it works.", "So, I think, it works."),
    ("hello world", "Hello world"),
    ("I left my umbrella with the drums", "I left my umbrella with the drums"),
    ("Hmm... let me think", "Let me think"),
    ("um uh", ""),
    ("ehm, allora ci vediamo domani", "Allora ci vediamo domani"),
    ("it works . really", "It works. Really"),
]

for raw, expected in CASES:
    got = clean(raw)
    assert got == expected, f"{raw!r} -> {got!r}, expected {expected!r}"

print(f"OK: {len(CASES)} cleanup cases pass")
