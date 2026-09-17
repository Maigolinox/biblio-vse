"""Helpers for the English translation of Biblio-VSE v2."""


class T:
    """Full English text of an artifact."""

    def __init__(self, text):
        self.text = text

    def apply(self, spanish):
        return self.text


class R:
    """Targeted (es -> en) replacements for artifacts that are mostly English already."""

    def __init__(self, pairs):
        self.pairs = pairs

    def apply(self, spanish):
        text = spanish
        for es, en in self.pairs:
            if es not in text:
                raise ValueError(f"replacement source not found: {es!r}")
            text = text.replace(es, en)
        return text
