"""Unit testy pro modul sifry.utils."""

import numpy as np
import pytest

from sifry import (
    ALPHABET,
    build_reference_matrix,
    export_decryption,
    load_reference_text,
    normalize_text,
)


# ---------------------------------------------------------------------------
# load_reference_text
# ---------------------------------------------------------------------------

def test_load_reference_text_normalizes_diacritics(tmp_path):
    source_file = tmp_path / "reference.txt"
    source_file.write_text("Příliš žluťoučký kůň", encoding="utf-8")
    loaded_text = load_reference_text(source_file)
    assert loaded_text == "PRILIS_ZLUTOUCKY_KUN"


def test_load_reference_text_raises_on_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        load_reference_text(missing_path)


def test_load_reference_text_accepts_string_path(tmp_path):
    source_file = tmp_path / "reference.txt"
    source_file.write_text("AHOJ", encoding="utf-8")
    loaded_text = load_reference_text(str(source_file))
    assert loaded_text == "AHOJ"


def test_load_reference_text_supports_alternative_encoding(tmp_path):
    """Krakatit z Wikisource bývá v cp1250 — encoding param to musí umět."""
    source_file = tmp_path / "reference_cp1250.txt"
    czech_text = "Příliš žluťoučký kůň"
    source_file.write_bytes(czech_text.encode("cp1250"))
    loaded_text = load_reference_text(source_file, encoding="cp1250")
    assert loaded_text == "PRILIS_ZLUTOUCKY_KUN"


# ---------------------------------------------------------------------------
# build_reference_matrix
# ---------------------------------------------------------------------------

def test_build_reference_matrix_shape_and_sum():
    text = normalize_text("ABCDEFGHIJKLMNOPQRSTUVWXYZ " * 100)
    matrix = build_reference_matrix(text)
    assert matrix.shape == (len(ALPHABET), len(ALPHABET))
    assert np.isclose(matrix.sum(), 1.0)


def test_build_reference_matrix_all_positive_due_to_smoothing():
    """Smoothing zajistí, že žádná buňka není nula → log(x) bezpečné."""
    minimal_text = normalize_text("AB")
    matrix = build_reference_matrix(minimal_text)
    assert np.all(matrix > 0)


# ---------------------------------------------------------------------------
# export_decryption
# ---------------------------------------------------------------------------

def test_export_decryption_writes_files_with_correct_names(tmp_path):
    plaintext = "HELLO_WORLD"  # délka 11
    key = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"
    sample_id = 42

    plaintext_path, key_path = export_decryption(
        text_id=sample_id,
        plaintext=plaintext,
        key=key,
        out_dir=tmp_path,
    )
    assert plaintext_path.name == "text_11_sample_42_plaintext.txt"
    assert key_path.name == "text_11_sample_42_key.txt"


def test_export_decryption_writes_content_verbatim(tmp_path):
    plaintext = "AB_CD"
    key = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"
    plaintext_path, key_path = export_decryption(
        text_id=1,
        plaintext=plaintext,
        key=key,
        out_dir=tmp_path,
    )
    assert plaintext_path.read_text(encoding="utf-8") == plaintext
    assert key_path.read_text(encoding="utf-8") == key


def test_export_decryption_creates_missing_nested_directory(tmp_path):
    nested_dir = tmp_path / "level1" / "level2"
    assert not nested_dir.exists()
    export_decryption(
        text_id=1,
        plaintext="X",
        key="A" * len(ALPHABET),
        out_dir=nested_dir,
    )
    assert nested_dir.exists()


def test_export_decryption_returns_path_tuple(tmp_path):
    result = export_decryption(
        text_id=0,
        plaintext="X",
        key="A" * len(ALPHABET),
        out_dir=tmp_path,
    )
    assert isinstance(result, tuple)
    assert len(result) == 2
    plaintext_path, key_path = result
    assert plaintext_path.exists()
    assert key_path.exists()
