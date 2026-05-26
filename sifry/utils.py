"""Pomocné I/O funkce pro práci s referenčními a šifrovanými texty."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, Union

import numpy as np

from .cipher import (
    ALPHABET,
    get_bigrams,
    normalize_text,
    transition_matrix,
)

PathLike = Union[str, Path]


def load_reference_text(path: PathLike, encoding: str = "utf-8") -> str:
    """Načte a normalizuje český referenční text ze souboru.

    Soubor je očekáván jako prostý text (typicky Krakatit z Wikisource).
    Po načtení se aplikuje `normalize_text`: uppercase, odstranění diakritiky,
    mezery → `_`, vyhození znaků mimo ALPHABET.

    Args:
        path: Cesta k textovému souboru.
        encoding: Kódování souboru. Defaultně UTF-8. České texty z Windows
            zdrojů jsou často v `cp1250` nebo `iso-8859-2` — v takovém
            případě zadejte explicitně.

    Returns:
        Normalizovaný řetězec připravený pro `build_reference_matrix`.

    Raises:
        FileNotFoundError: Pokud soubor neexistuje.
        UnicodeDecodeError: Pokud soubor není v zadaném kódování.
    """
    source_path = Path(path)
    raw_text = source_path.read_text(encoding=encoding)
    return normalize_text(raw_text)


def build_reference_matrix(text: str) -> np.ndarray:
    """Sestaví relativní bigramovou matici z normalizovaného textu.

    Convenience wrapper okolo `get_bigrams` + `transition_matrix`
    s `relative=True`. Laplace smoothing je v `transition_matrix` vždy
    aktivní, takže výstup je přímo bezpečný pro `np.log(...)` a tedy
    použitelný jako `reference_matrix` pro `plausibility` a
    `prolom_substitute`.

    Args:
        text: Již normalizovaný text (viz `load_reference_text` nebo
            `normalize_text`). Musí být dostatečně dlouhý — zadání
            doporučuje ≥ 400 000 znaků (Krakatit ~452 k).

    Returns:
        numpy.ndarray (27×27, dtype=float), součet všech prvků = 1.
    """
    bigrams = get_bigrams(text)
    return transition_matrix(bigrams, ALPHABET, relative=True)


def export_decryption(
    text_id: int,
    plaintext: str,
    key: str,
    out_dir: PathLike = "outputs",
) -> Tuple[Path, Path]:
    """Uloží dešifrovaný text a klíč podle naming konvence ze zadání.

    Vytvoří dva soubory v `out_dir`:

        text_{len(plaintext)}_sample_{text_id}_plaintext.txt
        text_{len(plaintext)}_sample_{text_id}_key.txt

    Soubory obsahují pouze čistý text bez metadat (požadavek zadání).
    Cílový adresář se vytvoří, pokud neexistuje (včetně nadřazených).

    Args:
        text_id: Identifikátor vzorku (`sample_id` v konvenci zadání).
        plaintext: Dešifrovaný text — jeho délka určuje jméno souboru.
        key: Substituční klíč (permutace ALPHABET).
        out_dir: Cílový adresář. Defaultně `outputs` (relativní k CWD).

    Returns:
        Tuple `(plaintext_path, key_path)` s cestami zapsaných souborů.
    """
    output_directory = Path(out_dir)
    output_directory.mkdir(parents=True, exist_ok=True)

    plaintext_length = len(plaintext)
    filename_prefix = f"text_{plaintext_length}_sample_{text_id}"
    plaintext_path = output_directory / f"{filename_prefix}_plaintext.txt"
    key_path = output_directory / f"{filename_prefix}_key.txt"

    plaintext_path.write_text(plaintext, encoding="utf-8")
    key_path.write_text(key, encoding="utf-8")

    return plaintext_path, key_path
