"""Sifry — knihovna pro substituční šifru a její kryptoanalýzu.

Veřejné API:
    ALPHABET, validate_key, normalize_text
    get_bigrams, transition_matrix
    substitute_encrypt, substitute_decrypt
    plausibility, prolom_substitute, CryptanalysisResult
    load_reference_text, build_reference_matrix, export_decryption
"""

from .cipher import (
    ALPHABET,
    get_bigrams,
    normalize_text,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
    validate_key,
)
from .cryptanalysis import (
    CryptanalysisResult,
    plausibility,
    prolom_substitute,
)
from .utils import (
    build_reference_matrix,
    export_decryption,
    load_reference_text,
)

__all__ = [
    "ALPHABET",
    "CryptanalysisResult",
    "build_reference_matrix",
    "export_decryption",
    "get_bigrams",
    "load_reference_text",
    "normalize_text",
    "plausibility",
    "prolom_substitute",
    "substitute_decrypt",
    "substitute_encrypt",
    "transition_matrix",
    "validate_key",
]

__version__ = "0.2.0"
