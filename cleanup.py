"""Tidy a raw transcript: drop spoken fillers, fix spacing, capitalise sentences."""
import re

# English and Italian hesitation sounds. Whole words only, so "umbrella" and "drums" survive.
FILLER = re.compile(r"\b(?:umm*|uhh*|erm*|ehm+|hmm+|mmm*)\b,?", re.IGNORECASE)


def clean(text):
    text = FILLER.sub("", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)  # no space before punctuation
    text = re.sub(r"(,\s*)+,", ",", text)  # "so, , yes" -> "so, yes"
    text = re.sub(r"^[,.\s]+", "", text)  # leftover lead-in punctuation
    text = re.sub(r"(^|[.!?]\s+)([a-zà-ü])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text.strip()
