"""Sifry — knihovna pro substituční šifru a její kryptoanalýzu."""

from .cipher import (
    ALPHABET,
    get_bigrams,
    normalize_text,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
    validate_key,
)

__all__ = [
    "ALPHABET",
    "get_bigrams",
    "normalize_text",
    "substitute_decrypt",
    "substitute_encrypt",
    "transition_matrix",
    "validate_key",
]

__version__ = "0.2.0"
