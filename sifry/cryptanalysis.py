"""Kryptoanalýza substituční šifry pomocí Metropolis-Hastings algoritmu.

Modul implementuje statistickou kryptoanalýzu popsanou v zadání:
log-likelihood věrohodnostní funkci a M-H sampler, který prohledává
prostor permutací abecedy a hledá klíč, jehož dešifrovaný text má
bigramovou strukturu nejbližší českému jazyku.

Veřejné funkce:
    plausibility: skóre textu vůči referenční bigramové matici.
    prolom_substitute: M-H prolomení šifry.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .cipher import (
    ALPHABET,
    get_bigrams,
    substitute_decrypt,
    validate_key,
)


@dataclass(frozen=True)
class CryptanalysisResult:
    """Výsledek jednoho běhu M-H prolomení šifry.

    Attributes:
        key: Permutace abecedy s nejvyšší dosaženou věrohodností napříč
            všemi iteracemi.
        plaintext: Dešifrovaný text získaný aplikací `key` na vstupní
            ciphertext.
        log_plausibility: Hodnota věrohodnostní funkce pro `key`. Vyšší
            (méně záporné) číslo = lepší shoda s jazykovým modelem.
    """

    key: str
    plaintext: str
    log_plausibility: float


def plausibility(text: str, reference_matrix: np.ndarray) -> float:
    """Spočítá log-věrohodnost textu vůči referenční bigramové matici.

    Skóre je definováno jako:

        L = Σ_{i,j} log(reference_matrix[i, j]) * observed_matrix[i, j]

    kde `observed_matrix` je absolutní matice četností bigramů textu
    nad projektovou abecedou (bez Laplace smoothing — to by zavedlo
    konstantní bias do skóre).

    Args:
        text: Již normalizovaný text (uppercase, jen A-Z a `_`). Texty
            před normalizací produkují podhodnocené skóre, protože znaky
            mimo abecedu jsou tiše vynechány v bigramové analýze.
        reference_matrix: Relativní referenční bigramová matice (součet 1)
            o rozměru 27×27, indexovaná podle ALPHABET. Musí mít všechny
            prvky striktně kladné (Laplace smoothing), jinak log(0).

    Returns:
        Log-věrohodnost jako Python float. Hodnoty jsou typicky velká
        záporná čísla; čím vyšší, tím lépe text odpovídá referenci.
        Pro prázdný text vrací 0.0 (žádné bigramy → žádný příspěvek).

    Raises:
        ValueError: Pokud `reference_matrix` obsahuje nekladné prvky.
    """
    if np.any(reference_matrix <= 0):
        raise ValueError(
            "reference_matrix musí mít striktně kladné prvky "
            "(aplikujte Laplace smoothing na referenční matici)."
        )

    observed_matrix = _observed_transition_matrix(text)
    log_reference_matrix = np.log(reference_matrix)
    weighted_log_likelihood = log_reference_matrix * observed_matrix
    return float(np.sum(weighted_log_likelihood))


def prolom_substitute(
    text: str,
    reference_matrix: np.ndarray,
    iterations: int,
    start_key: Optional[str] = None,
    swap_accept_probability: float = 0.01,
    log_interval: int = 50,
    seed: Optional[int] = None,
) -> CryptanalysisResult:
    """Najde nejpravděpodobnější dešifrovací klíč Metropolis-Hastings samplingem.

    Algoritmus iterativně navrhuje nové klíče prohozením dvou náhodných
    pozic v současném klíči, dešifruje ciphertext kandidátním klíčem a
    spočítá jeho `plausibility`. Kandidát je přijat:
      - bezpodmínečně, pokud má vyšší věrohodnost než současný klíč,
      - jinak s pravděpodobností `swap_accept_probability` (defaultně 0.01,
        umožňuje algoritmu uniknout z lokálních maxim).

    Napříč iteracemi se vede zvlášť **nejlepší dosud nalezený klíč**, který
    se vrací v `CryptanalysisResult` (i kdyby ho M-H později opustil).

    Args:
        text: Ciphertext (již normalizovaný — pouze ALPHABET znaky).
        reference_matrix: Relativní referenční bigramová matice (viz
            `plausibility`).
        iterations: Počet M-H kroků. Zadání specifikuje 20 000 pro
            finální exporty; pro testy postačí 2 000–5 000.
        start_key: Počáteční klíč. Pokud None, vygeneruje se náhodná
            permutace ALPHABET.
        swap_accept_probability: Pravděpodobnost přijetí horšího kandidáta
            (zadání používá 0.01). Vyšší hodnota = agresivnější průzkum.
            Validní rozsah <0, 1>.
        log_interval: Frekvence výpisu progressu (každých N iterací).
            Nastavte 0 pro umlčení.
        seed: Volitelný seed pro reprodukovatelnost. Pokud None, použije
            se nedeterministický zdroj náhody.

    Returns:
        CryptanalysisResult s nejlepším klíčem, odpovídajícím dešifrovaným
        textem a jeho log-věrohodností.

    Raises:
        ValueError: Pokud `iterations < 1`, `swap_accept_probability` je
            mimo <0, 1>, nebo `start_key` (je-li zadán) není platná
            permutace ALPHABET.
    """
    if iterations < 1:
        raise ValueError("iterations musí být kladné celé číslo.")
    if not 0 <= swap_accept_probability <= 1:
        raise ValueError("swap_accept_probability musí být v intervalu <0, 1>.")

    rng = random.Random(seed)

    initial_key = start_key if start_key is not None else _generate_random_key(rng)
    validate_key(initial_key)

    current_key = initial_key
    current_plaintext = substitute_decrypt(text, current_key)
    current_score = plausibility(current_plaintext, reference_matrix)

    best_key = current_key
    best_plaintext = current_plaintext
    best_score = current_score

    for iteration_index in range(1, iterations + 1):
        candidate_key = _swap_two_random_positions(current_key, rng)
        candidate_plaintext = substitute_decrypt(text, candidate_key)
        candidate_score = plausibility(candidate_plaintext, reference_matrix)

        improves_score = candidate_score > current_score
        accepted_by_chance = rng.random() < swap_accept_probability
        should_accept = improves_score or accepted_by_chance

        if should_accept:
            current_key = candidate_key
            current_plaintext = candidate_plaintext
            current_score = candidate_score

            if current_score > best_score:
                best_key = current_key
                best_plaintext = current_plaintext
                best_score = current_score

        is_log_iteration = log_interval > 0 and iteration_index % log_interval == 0
        if is_log_iteration:
            print(
                f"Iteration {iteration_index}: "
                f"log plausibility = {current_score:.2f} "
                f"(best = {best_score:.2f})"
            )

    return CryptanalysisResult(
        key=best_key,
        plaintext=best_plaintext,
        log_plausibility=best_score,
    )


# -----------------------------------------------------------------------------
# Privátní helpery
# -----------------------------------------------------------------------------

def _observed_transition_matrix(text: str) -> np.ndarray:
    """Sestaví absolutní (nesmoothovanou) bigramovou matici z textu.

    Toto je úmyslně oddělené od veřejného `transition_matrix` z modulu
    `cipher`: ten aplikuje Laplace smoothing nepodmíněně (přičítá +1
    ke všem buňkám), což je správně pro **referenční** matice používané
    v `log(...)`, ale **nesprávně** pro **pozorovanou** matici, která
    vstupuje do plausibility jen jako násobitel. Smoothing v pozorované
    matici by zavedl konstantní bias do celého skóre.

    Args:
        text: Normalizovaný text (uppercase ALPHABET + `_`).

    Returns:
        numpy.ndarray (27×27, dtype=float) absolutních počtů bigramů.
        Buňky pro bigramy, které se v textu nevyskytly, jsou přesně 0.
    """
    character_to_index = {ch: idx for idx, ch in enumerate(ALPHABET)}
    alphabet_size = len(ALPHABET)
    matrix = np.zeros((alphabet_size, alphabet_size), dtype=float)

    for bigram in get_bigrams(text):
        if len(bigram) != 2:
            continue
        first_char, second_char = bigram
        if first_char in character_to_index and second_char in character_to_index:
            row = character_to_index[first_char]
            col = character_to_index[second_char]
            matrix[row, col] += 1

    return matrix


def _generate_random_key(rng: random.Random) -> str:
    """Vytvoří uniformní náhodnou permutaci ALPHABET.

    Args:
        rng: Zdroj náhodných čísel (přijímán zvenčí kvůli reprodukovatelnosti).

    Returns:
        Řetězec délky 27 — náhodná permutace ALPHABET.
    """
    alphabet_chars = list(ALPHABET)
    rng.shuffle(alphabet_chars)
    return "".join(alphabet_chars)


def _swap_two_random_positions(key: str, rng: random.Random) -> str:
    """Vrátí kopii klíče se zaměněnými dvěma náhodnými pozicemi.

    Args:
        key: Vstupní klíč (permutace ALPHABET).
        rng: Zdroj náhodných čísel.

    Returns:
        Nový řetězec stejné délky jako `key` se zaměněnými dvěma znaky.
    """
    key_chars = list(key)
    first_position, second_position = rng.sample(range(len(key_chars)), 2)
    key_chars[first_position], key_chars[second_position] = (
        key_chars[second_position],
        key_chars[first_position],
    )
    return "".join(key_chars)
