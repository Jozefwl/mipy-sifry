# mipy-sifry

Homework assignment from python

### Commit rules
- Please make your own branch when working on an issue
- Send a pull request and it will be merged to main

### Issues rules
- When working on an issue, and the implementation gets more complex / bug is found / you want to contribute **make a sub-issue under the already existing big issue (better tracking)**

## Substitution Cipher Library

Jednoduchá knihovna pro práci se substituční šifrou.

## Struktura projektu

- `sifry/src/substitution_cipher.py` - modul s funkcemi pro šifrování a dešifrování.
- `sifry/tests/test_basic_cipher.py` - jednoduchý test a ukázka běhu.
- `sifry/data/` - místo pro případná vstupní data.

## Jak spustit test

1. Otevři příkazovou řádku ve složce projektu.
2. Nainstaluj závislosti:

```bash
pip install -r sifry/requirements.txt
```

3. Spusť:

```bash
python sifry/tests/test_basic_cipher.py
```

Pokud máš nainstalovaný `pytest`, můžeš také spustit:

```bash
python -m pytest sifry/tests/test_basic_cipher.py
```

## Hlavní funkce

- `substitute_encrypt(plaintext, key)`
  - Zašifruje text pomocí substitučního klíče.
  - Zachovává znaky, které nejsou v abecedě `ABCDEFGHIJKLMNOPQRSTUVWXYZ_`.

- `substitute_decrypt(ciphertext, key)`
  - Dešifruje text zpět pomocí stejného klíče.
  - Zachovává znaky mimo abecedu beze změny.

- `normalize_text(text, keep_non_alphabet=False)`
  - Převede text na velká písmena, odstraní diakritiku a mezery změní na `_`.
  - Znaky mimo abecedu buď odstraní, nebo je ponechá podle parametru.

- `get_bigrams(text)`
  - Vrátí seznam dvojic po sobě jdoucích znaků z textu.

- `transition_matrix(bigrams, alphabet, relative=False)`
  - Vytvoří matici četností bigramů s Laplaceovou hladkou.
  - Pokud `relative=True`, vrátí relativní matici, jejíž součet prvků je 1.

Klíč musí být permutace celé abecedy, tedy obsahovat každý znak právě jednou.
