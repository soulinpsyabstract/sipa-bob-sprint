"""Standalone example for the terminal demo recording — NOT part of the test
suite, not a claim about Bob's actual output. Demonstrates sipa-signal's
deterministic filler-stripping on an illustrative sentence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "sipa-signal"))

from sipa_signal import extract

EXAMPLE_TEXT = (
    "Well, I think this code is basically fine, to be honest, and it should "
    "probably work in most cases without any real issues."
)

if __name__ == "__main__":
    print(f"input:  {EXAMPLE_TEXT!r}\n")
    card = extract(EXAMPLE_TEXT)
    for k, v in card.to_dict().items():
        print(f"{k}: {v}")
