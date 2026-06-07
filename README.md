# mipy-sifry

Python knihovna pro substituční šifru, dešifrování a automatickou kryptoanalýzu
pomocí Metropolis-Hastings algoritmu nad bigramovou maticí češtiny.

## Instalace

### Make venv, activate
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies
```bash
pip install -e .             # vývojový (editable) install
pip install -e .[dev]        # + pytest, pytest-cov
pip install -e .[notebook]   # + jupyter, matplotlib, nbconvert
```

### Run jupyter server

```bash
jupyter notebook
```


## Spuštění testů

```bash
pytest -v
```

## Veřejné API

```python
from sifry import (
    ALPHABET,
    validate_key, normalize_text,
    get_bigrams, transition_matrix,
    substitute_encrypt, substitute_decrypt,
    plausibility, prolom_substitute, CryptanalysisResult,
    load_reference_text, build_reference_matrix, export_decryption,
)
```

## Šifrování / dešifrování

```python
from sifry import substitute_encrypt, substitute_decrypt

key = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"
cipher = substitute_encrypt("HELLO_WORLD", key)
plain  = substitute_decrypt(cipher, key)
```

Klíč musí být permutace abecedy `ABCDEFGHIJKLMNOPQRSTUVWXYZ_` (27 znaků,
mezera nahrazena podtržítkem). Znaky mimo abecedu projdou beze změny.

## Normalizace textu

```python
from sifry import normalize_text

normalize_text("Příliš žluťoučký kůň")  # → "PRILIS_ZLUTOUCKY_KUN"
```

## Kryptoanalýza (M-H algoritmus)

```python
from sifry import (
    load_reference_text, build_reference_matrix,
    substitute_encrypt, prolom_substitute,
)

# 1) Načtení referenčního českého textu a sestavení bigramové matice
reference_text   = load_reference_text("data/reference/krakatit.txt")
reference_matrix = build_reference_matrix(reference_text)

# 2) Vlastní ciphertext
cipher = substitute_encrypt("AHOJ_SVETE", "DEFGHIJKLMNOPQRSTUVWXYZ_ABC")

# 3) Prolomení (20 000 iterací M-H, fixed seed pro reprodukovatelnost)
result = prolom_substitute(
    text=cipher,
    reference_matrix=reference_matrix,
    iterations=20_000,
    seed=42,
)

print(result.plaintext)         # dešifrovaný text
print(result.key)               # nejlepší nalezený klíč
print(result.log_plausibility)  # skóre nejlepšího klíče
```

`prolom_substitute` přijímá tyto volitelné parametry:
- `start_key`: explicitní počáteční klíč (defaultně náhodná permutace)
- `swap_accept_probability`: pravděpodobnost přijetí horšího kandidáta (default `0.01`)
- `log_interval`: výpis progresu každých N iterací (default `50`, `0` umlčí)
- `seed`: seed pro RNG kvůli reprodukovatelnosti

## Export výsledků

```python
from sifry import export_decryption

plaintext_path, key_path = export_decryption(
    text_id=1,
    plaintext=result.plaintext,
    key=result.key,
    out_dir="outputs",
)
# vznikne: outputs/text_{len}_sample_1_plaintext.txt
#          outputs/text_{len}_sample_1_key.txt
```

## Struktura projektu

```
mipy-sifry/
├── pyproject.toml        — build config (PEP 621)
├── sifry/                — Python package
│   ├── __init__.py       — veřejné API
│   ├── cipher.py         — šifra + normalizace + bigramy
│   ├── cryptanalysis.py  — plausibility + M-H prolom_substitute
│   └── utils.py          — I/O + export
├── tests/                — pytest testy
├── data/
│   ├── reference/        — referenční texty (Krakatit)
│   └── encrypted/        — texty k prolomení
├── notebooks/            — Jupyter demonstrace (TODO)
└── docs/                 — projektová dokumentace
```

## Workflow

- Pro každou změnu vytvořit feature branch.
- PR proti `main`, code review před mergem.
- Komplexnější issue rozdělit na sub-issues pro lepší tracking.
