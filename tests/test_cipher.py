import numpy as np

from sifry import (
    get_bigrams,
    normalize_text,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
)

VALID_KEY = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"


def test_encrypt_decrypt():
    original = "HELLO_WORLD!"
    encrypted = substitute_encrypt(original, VALID_KEY)
    decrypted = substitute_decrypt(encrypted, VALID_KEY)

    assert encrypted == "KHOORCZRUOG!"
    assert decrypted == original


def test_normalize_text():
    text = "Čau světe 123"
    normalized = normalize_text(text)

    assert normalized == "CAU_SVETE_"


def test_normalize_text_keep_non_alphabet():
    text = "Čau světe 123!"
    normalized = normalize_text(text, keep_non_alphabet=True)

    assert normalized == "CAU_SVETE_123!"


def test_get_bigrams_and_transition_matrix():
    text = normalize_text("AB CD")
    bigrams = get_bigrams(text)
    matrix = transition_matrix(bigrams, "ABCDEFGHIJKLMNOPQRSTUVWXYZ_", relative=True)

    assert text == "AB_CD"
    assert bigrams == ["AB", "B_", "_C", "CD"]
    assert np.isclose(np.sum(matrix), 1.0)


def test_invalid_key_length():
    bad_key = "ABC"
    try:
        substitute_encrypt("TEXT", bad_key)
    except ValueError as error:
        assert "délku" in str(error)
    else:
        raise AssertionError("Očekáván byl ValueError pro špatnou délku klíče.")


def test_invalid_key_chars():
    bad_key = "DEFGHIJKLMNOPQRSTUVWXYZ_AbC"  # špatný znak 'a' místo 'A'
    try:
        substitute_encrypt("TEXT", bad_key)
    except ValueError as error:
        assert "obsahovat přesně" in str(error)
    else:
        raise AssertionError("Očekáván byl ValueError pro špatné znaky v klíči.")


def test_duplicate_key_chars():
    bad_key = "AABCDEFGHIJKLMNOPQRSTUVWXY_"  # duplicitní A
    try:
        substitute_encrypt("TEXT", bad_key)
    except ValueError as error:
        assert "právě jednou" in str(error)
    else:
        raise AssertionError("Očekáván byl ValueError pro duplicitní znaky v klíči.")


if __name__ == "__main__":
    print("Test: zašifrování a dešifrování")
    test_encrypt_decrypt()
    print(" - funkce fungují pro platný klíč")

    print("Test: špatná délka klíče")
    test_invalid_key_length()
    print(" - správně hodí chybu")

    print("Test: chybějící znak v klíči")
    test_invalid_key_chars()
    print(" - správně hodí chybu")

    print("Test: duplicitní znak v klíči")
    test_duplicate_key_chars()
    print(" - správně hodí chybu")

    print("Test: normalizace textu")
    test_normalize_text()
    test_normalize_text_keep_non_alphabet()
    print(" - normalizace funguje")

    print("Test: bigramy a matice")
    test_get_bigrams_and_transition_matrix()
    print(" - bigramy a matice fungují")

    print("Všechny testy proběhly úspěšně.")
