"""Unit testy pro modul sifry.cryptanalysis."""

import numpy as np
import pytest

from sifry import (
    ALPHABET,
    CryptanalysisResult,
    build_reference_matrix,
    normalize_text,
    plausibility,
    prolom_substitute,
    substitute_decrypt,
    substitute_encrypt,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reference_text():
    """Krátký umělý český text s opakovanými bigramy pro stabilní testy.

    Pro produkční použití by se použil Krakatit; pro unit testy je
    rychlejší mít vše inline.
    """
    base_text = (
        "Velmi dlouhý český text který opakovaně používá běžné bigramy "
        "jako NA NE TE ST KO PR a podobné. "
    )
    return normalize_text(base_text * 200)


@pytest.fixture(scope="module")
def reference_matrix(reference_text):
    return build_reference_matrix(reference_text)


@pytest.fixture
def known_key():
    return "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"


# ---------------------------------------------------------------------------
# plausibility()
# ---------------------------------------------------------------------------

def test_plausibility_returns_float(reference_matrix):
    score = plausibility("HELLO_WORLD", reference_matrix)
    assert isinstance(score, float)


def test_plausibility_higher_for_reference_like_text(
    reference_matrix, reference_text,
):
    """Skutečný text z reference dostane vyšší skóre než reverzovaný."""
    real_sample = reference_text[:500]
    scrambled_sample = "".join(reversed(real_sample))
    real_score = plausibility(real_sample, reference_matrix)
    scrambled_score = plausibility(scrambled_sample, reference_matrix)
    assert real_score > scrambled_score


def test_plausibility_rejects_nonpositive_reference_matrix():
    bad_matrix = np.zeros((len(ALPHABET), len(ALPHABET)))
    with pytest.raises(ValueError, match="striktně kladné"):
        plausibility("HELLO", bad_matrix)


def test_plausibility_empty_text_returns_zero(reference_matrix):
    """Prázdný text → žádné bigramy → observed matrix je 0 → suma 0."""
    assert plausibility("", reference_matrix) == 0.0


def test_plausibility_observed_matrix_is_unsmoothed(reference_matrix):
    """Plausibility nesmí zavádět konstantní bias z Laplace smoothing.

    Plausibility prázdného textu = 0 dokazuje, že observed_matrix
    neobsahuje +1 bias na všech buňkách (jinak by bylo
    L = sum(log(ref)) * 1, což rozhodně není 0).
    """
    empty_score = plausibility("", reference_matrix)
    assert empty_score == 0.0


# ---------------------------------------------------------------------------
# prolom_substitute() — funkční testy
# ---------------------------------------------------------------------------

def test_prolom_substitute_returns_result_dataclass(reference_matrix, known_key):
    cipher = substitute_encrypt("HELLO_WORLD", known_key)
    result = prolom_substitute(
        text=cipher,
        reference_matrix=reference_matrix,
        iterations=10,
        log_interval=0,
        seed=42,
    )
    assert isinstance(result, CryptanalysisResult)
    assert len(result.key) == len(ALPHABET)
    assert isinstance(result.log_plausibility, float)
    assert sorted(result.key) == sorted(ALPHABET)


def test_prolom_substitute_deterministic_with_seed(reference_matrix, known_key):
    cipher = substitute_encrypt("HELLO_WORLD_FOO_BAR", known_key)
    result_a = prolom_substitute(
        cipher, reference_matrix,
        iterations=100, seed=42, log_interval=0,
    )
    result_b = prolom_substitute(
        cipher, reference_matrix,
        iterations=100, seed=42, log_interval=0,
    )
    assert result_a.key == result_b.key
    assert result_a.plaintext == result_b.plaintext
    assert result_a.log_plausibility == result_b.log_plausibility


def test_prolom_substitute_respects_start_key(reference_matrix, known_key):
    """Pokud žádný kandidát nezlepší start_key, výsledek = dešifrování start_key.

    Nastavíme swap_accept_probability=0 (žádné náhodné přijetí horšího),
    takže best_key ≥ start_key co do plausibility.
    """
    cipher = substitute_encrypt("HELLO_WORLD", known_key)
    expected_baseline_plaintext = substitute_decrypt(cipher, known_key)
    expected_baseline_score = plausibility(
        expected_baseline_plaintext, reference_matrix,
    )
    result = prolom_substitute(
        cipher, reference_matrix,
        iterations=5,
        start_key=known_key,
        swap_accept_probability=0.0,
        seed=0,
        log_interval=0,
    )
    assert result.log_plausibility >= expected_baseline_score


def test_prolom_substitute_keeps_best_key_across_iterations(
    reference_matrix, known_key,
):
    """Konečné skóre nesmí být horší než počáteční skóre.

    Pseudokód v zadání chybně vrací current_key (může degradovat). My musíme
    vrátit best_key, takže konečné skóre je monotonně neklesající.
    """
    cipher = substitute_encrypt("HELLO_WORLD_FOO_BAR_BAZ", known_key)
    initial_random_key_score = prolom_substitute(
        cipher, reference_matrix,
        iterations=1, seed=123, log_interval=0,
    ).log_plausibility
    longer_run_score = prolom_substitute(
        cipher, reference_matrix,
        iterations=500, seed=123, log_interval=0,
    ).log_plausibility
    assert longer_run_score >= initial_random_key_score


# ---------------------------------------------------------------------------
# prolom_substitute() — validace vstupů
# ---------------------------------------------------------------------------

def test_prolom_substitute_rejects_zero_iterations(reference_matrix):
    with pytest.raises(ValueError, match="iterations"):
        prolom_substitute("AB", reference_matrix, iterations=0)


def test_prolom_substitute_rejects_negative_iterations(reference_matrix):
    with pytest.raises(ValueError, match="iterations"):
        prolom_substitute("AB", reference_matrix, iterations=-10)


def test_prolom_substitute_rejects_invalid_accept_probability(reference_matrix):
    with pytest.raises(ValueError, match="swap_accept_probability"):
        prolom_substitute(
            "AB", reference_matrix, iterations=1,
            swap_accept_probability=1.5,
        )


def test_prolom_substitute_rejects_negative_accept_probability(reference_matrix):
    with pytest.raises(ValueError, match="swap_accept_probability"):
        prolom_substitute(
            "AB", reference_matrix, iterations=1,
            swap_accept_probability=-0.1,
        )


def test_prolom_substitute_rejects_invalid_start_key(reference_matrix):
    with pytest.raises(ValueError):
        prolom_substitute(
            "AB", reference_matrix, iterations=1,
            start_key="ABC",  # špatná délka
        )
