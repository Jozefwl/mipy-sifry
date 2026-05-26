import unicodedata

import numpy as np

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"


def validate_key(key):
    """Zkontroluje, že klíč je platná permutace abecedy."""
    if len(key) != len(ALPHABET):
        raise ValueError("Klíč musí mít délku přesně {} znaků.".format(len(ALPHABET)))

    if len(set(key)) != len(key):
        raise ValueError("Klíč musí obsahovat každý znak právě jednou.")

    if set(key) != set(ALPHABET):
        raise ValueError("Klíč musí obsahovat přesně tyto znaky: {}".format(ALPHABET))


def normalize_text(text, keep_non_alphabet=False):
    """Převede text na formát vhodný pro abecedu ABCDEFGHIJKLMNOPQRSTUVWXYZ_."""
    text = text.upper()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace(" ", "_")

    normalized = []
    for ch in text:
        if ch in ALPHABET:
            normalized.append(ch)
        elif keep_non_alphabet:
            normalized.append(ch)

    return "".join(normalized)


def get_bigrams(text):
    """Vrátí seznam dvojic po sobě jdoucích znaků z textu."""
    return [text[i : i + 2] for i in range(len(text) - 1)]


def transition_matrix(bigrams, alphabet, relative=False):
    """Vytvoří matici četností bigramů pro danou abecedu.

    Přidá 1 ke všem položkám, aby se zabránilo hodnotě 0.
    Pokud je relative=True, vrátí relativní matici, která sečtením prvků dává 1.
    """
    index = {ch: idx for idx, ch in enumerate(alphabet)}
    matrix = np.zeros((len(alphabet), len(alphabet)), dtype=float)

    for bigram in bigrams:
        if len(bigram) != 2:
            continue
        left, right = bigram
        if left in index and right in index:
            matrix[index[left], index[right]] += 1

    matrix += 1.0

    if relative:
        total = np.sum(matrix)
        if total > 0:
            matrix = matrix / total

    return matrix


def substitute_encrypt(plaintext, key):
    """Zašifruje zprávu pomocí substituční šifry a zadaného klíče."""
    validate_key(key)
    mapping = {plain: cipher for plain, cipher in zip(ALPHABET, key)}
    ciphertext = []
    for ch in plaintext:
        if ch in mapping:
            ciphertext.append(mapping[ch])
        else:
            ciphertext.append(ch)
    return "".join(ciphertext)


def substitute_decrypt(ciphertext, key):
    """Dešifruje zprávu zaslanou substituční šifrou zpět na původní text."""
    validate_key(key)
    mapping = {cipher: plain for plain, cipher in zip(ALPHABET, key)}
    plaintext = []
    for ch in ciphertext:
        if ch in mapping:
            plaintext.append(mapping[ch])
        else:
            plaintext.append(ch)
    return "".join(plaintext)
