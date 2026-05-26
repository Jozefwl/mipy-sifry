# mipy-sifry — Project Scope & Specifikace

> Detailní technicko‑produktová specifikace projektu. Slouží jako jediný zdroj pravdy o stavu, architektuře, packagingu a roadmapě. Vychází ze zadání `/Users/daniel/Downloads/zadani.pdf` a aktuálního stavu repozitáře k větvi `main`.

---

## 1. Cíl projektu

Vytvořit vlastní Python knihovnu, která umí:

1. **Šifrovat a dešifrovat** text klasickou **substituční šifrou** nad zjednodušenou anglickou abecedou `A–Z + _` (27 znaků; mezera → podtržítko).
2. **Automaticky prolomit** šifru pomocí **Metropolis-Hastings (M-H) algoritmu** s využitím **bigramové matice** sestavené z dlouhého českého referenčního textu (doporučeno Krakatit z Wikisource, ~452 000 znaků).
3. Aplikovat knihovnu na poskytnuté zašifrované texty (vyučující), výsledky **exportovat** podle pevné konvence pojmenování souborů.
4. Vše **demonstrovat v Jupyter notebooku** a notebook **vyexportovat do HTML nebo PDF** jako součást odevzdání.

Hodnocení (dle zadání): funkčnost šifrování/dešifrování, správnost kryptoanalýzy (bigramová matice + M-H), kvalita prezentace v notebooku, dokumentace a komentáře v kódu.

---

## 2. Stav implementace

### Mapování úkolů ze zadání → realita

| # | Úkol ze zadání                                          | Stav        | Odhad |
| - | ------------------------------------------------------- | ----------- | ----- |
| 1 | Šifrovací / dešifrovací funkčnost                       | Hotovo      | ~95 % |
| 2 | Bigramová matice + M-H algoritmus                       | Nehotovo    | ~5 %  |
| 3 | Jupyter notebook s demonstrací                          | Nehotovo    | 0 %   |
| 4 | Export dešifrovaných textů a klíčů (naming konvence)    | Nehotovo    | 0 %   |
| 5 | Notebook → HTML/PDF + krátký report                     | Nehotovo    | 0 %   |

### Hotovo (úkol 1)

V souboru `sifry/src/substitution_cipher.py` (92 řádků, plně otestováno):

- `ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"` — 27 znaků.
- `validate_key(key)` — kontroluje délku, unikátnost a přesnou shodu znaků.
- `normalize_text(text, keep_non_alphabet=False)` — uppercase, odstranění diakritiky přes NFD, mezery → `_`.
- `get_bigrams(text)` — list všech dvojic znaků.
- `transition_matrix(bigrams, alphabet, relative=False)` — frekvenční matice s Laplace smoothing; volitelně relativní (součet = 1).
- `substitute_encrypt(plaintext, key)`, `substitute_decrypt(ciphertext, key)` — šifrování/dešifrování přes mapování slovníkem.

Testy v `sifry/tests/test_basic_cipher.py` (7 testů, pytest-kompatibilní + standalone runner) — všechny prochází.

Podpůrné soubory: `README.md`, `LICENSE` (MIT, © 2026 Jozef Waldhauser), `function_descriptions.txt` (česky popsaný plán funkcí kryptoanalýzy), `sifry/setup.py`, `sifry/requirements.txt`.

### Nehotovo

- **Bigramová referenční matice** z českého textu (Krakatit). Soubor `sifry/data/reference-texts/text1.txt` je prázdný (0 B).
- **`plausibility(text, TM_ref)`** — log-likelihood srovnání pozorované a referenční matice.
- **`prolom_substitute(text, TM_ref, iter, start_key)`** — M-H algoritmus přesně podle pseudokódu v zadání.
- **Export rutina** — `text_{délka}_sample_{id}_plaintext.txt` + `_key.txt`, 20 000 iterací na text.
- **Jupyter notebook** `notebooks/demo.ipynb` s vizualizací.
- **Export notebooku** do HTML/PDF.
- **Stručný report** s výsledky.

### Drobné architektonické problémy zjištěné při průzkumu

| # | Problém | Lokace | Závažnost |
| - | ------- | ------ | --------- |
| A | `sys.path.insert(0, …)` hack místo skutečného balíčku | `sifry/src/__init__.py` + `tests/test_basic_cipher.py` | Střední — blokuje čistý `import sifry` |
| B | `setup.py` je AI-generovaný, autor sám varuje („This file might be wrong“) | `sifry/setup.py:8` | Střední |
| C | `install_requires` má `requests>=2.25.0`, který nikde není použit | `sifry/setup.py:57` | Nízká — zbytečná dependency |
| D | `author_email='your.email@example.com'` — placeholder | `sifry/setup.py:36-38` | Nízká |
| E | Prázdné placeholder složky `cipher/`, `utils/`, `notebooks/` (jen README) | `sifry/` | Nízká — uklidit při restrukturalizaci |
| F | Chybí CI/CD (`.github/workflows/`) | repo root | Nízká |
| G | `transition_matrix` přičítá `+1` ke všem buňkám vždy; pseudokód v zadání říká přičíst 1 jen tam, kde byla 0 | `substitution_cipher.py:58` | Nízká — funkčně ekvivalentní pro M-H, ale liší se od specifikace |

---

## 3. Současná architektura

```
mipy-sifry/
├── README.md                       ✓ česky/anglicky, popis API
├── LICENSE                         ✓ MIT
├── function_descriptions.txt       ✓ česky, plán funkcí kryptoanalýzy
├── .gitignore                      ✓
└── sifry/
    ├── setup.py                    ⚠ AI-generated, nutno revidovat
    ├── requirements.txt            ✓ jen numpy
    ├── src/
    │   ├── __init__.py             ⚠ sys.path hack
    │   └── substitution_cipher.py  ✓ implementováno, plně testováno
    ├── tests/
    │   ├── README.md               ─ placeholder
    │   └── test_basic_cipher.py    ✓ 7 testů, prochází
    ├── cipher/README.md            ─ prázdné, jen placeholder
    ├── cryptanalysis/README.md     ─ prázdné, jen placeholder
    ├── utils/README.md             ─ prázdné, jen placeholder
    ├── notebooks/README.md         ─ prázdné, jen placeholder
    └── data/
        ├── README.md               ✓ popis struktury
        ├── encrypted-texts/text1.txt  ─ 0 B
        └── reference-texts/text1.txt  ─ 0 B
```

**Importovací schéma dnes (problematické):**
```
tests/test_basic_cipher.py
   └─ sys.path.insert(0, "..")
        └─ from src.substitution_cipher import ...
```
To znamená, že knihovna není instalovatelná jako balíček (`import sifry` nefunguje), funguje jen pokud spouštíš testy ze správného CWD.

---

## 4. Cílová architektura (po dokončení úkolu 2)

```
mipy-sifry/
├── pyproject.toml                  ★ nahradit setup.py (PEP 621)
├── README.md
├── LICENSE
├── docs/
│   ├── PROJECT_SCOPE.md            ← tento soubor
│   ├── REPORT.md                   ★ závěrečný stručný report
│   └── exports/
│       ├── demo.html               ★ exportovaný notebook
│       └── demo.pdf                ★ exportovaný notebook
├── sifry/                          ★ pravý top-level Python package
│   ├── __init__.py                 ★ re-exporty veřejného API
│   ├── cipher.py                   ★ z src/substitution_cipher.py
│   ├── cryptanalysis.py            ★ plausibility, prolom_substitute
│   ├── utils.py                    ★ I/O, export, načítání ref. textu
│   └── data/
│       ├── reference/
│       │   └── krakatit.txt        ★ stažený a normalizovaný
│       └── encrypted/
│           └── text_*_ciphertext.txt
├── notebooks/
│   └── demo.ipynb                  ★ hlavní demo
├── tests/
│   ├── test_cipher.py              (přesun + úprava importu)
│   ├── test_cryptanalysis.py       ★
│   └── test_utils.py               ★
└── outputs/                        ★ výstupy exportu
    ├── text_1000_sample_1_plaintext.txt
    ├── text_1000_sample_1_key.txt
    └── …
```

★ = nový nebo přepracovaný oproti dnešnímu stavu

---

## 5. Packaging Python knihovny

### Volba build systému

**Doporučeno:** migrovat `setup.py` → `pyproject.toml` (PEP 621). Důvody:
- Moderní standard, lépe podporovaný.
- Deklarativní (žádný spustitelný kód při buildu).
- Zbavíme se AI-generovaného `setup.py` s varováním autora.

Příklad minimálního `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sifry"
version = "0.2.0"
description = "Substituční šifra + kryptoanalýza M-H algoritmem (české bigramy)"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"
authors = [{ name = "Daniel Zikmund", email = "zikmund.d@gmail.com" }]
dependencies = [
    "numpy>=1.19.0",
]

[project.optional-dependencies]
dev = ["pytest>=6.0", "pytest-cov>=2.10", "black", "flake8"]
notebook = ["jupyter", "matplotlib>=3.3", "pandas", "nbconvert"]

[tool.setuptools.packages.find]
include = ["sifry*"]
```

### Distribuce

```bash
pip install build
python -m build              # vytvoří dist/sifry-0.2.0-py3-none-any.whl + .tar.gz
```

### Lokální vývoj (editable install)

```bash
pip install -e .             # spouštět z repo rootu
pip install -e .[dev,notebook]
```

Po `pip install -e .` funguje v jakémkoli Pythonu / notebooku:
```python
import sifry
sifry.substitute_encrypt(...)
```

### Verzování

Semver, `0.1.0` → `0.2.0` po dokončení úkolu 2 (kryptoanalýza), `1.0.0` po odevzdání.

### Co opravit při migraci

- Odstranit `requests>=2.25.0` z `install_requires` (není použit).
- Vyplnit reálný `author_email`.
- Přepsat `find_packages` po restrukturalizaci (`src/` → `sifry/`).

---

## 6. Co je potřeba dodělat — produktově

### US-1 — Referenční bigramová matice z češtiny
**Jako** uživatel knihovny  
**chci** mít předpočítanou bigramovou matici z reprezentativního českého textu,  
**abych** mohl bez stahování okamžitě spouštět kryptoanalýzu.

**Akceptační kritéria:**
- V `sifry/data/reference/krakatit.txt` je normalizovaný text (≥ 400 000 znaků z abecedy).
- Funkce `build_reference_matrix()` vrátí relativní bigramovou matici 27×27 (součet = 1).
- Vizualizovatelné v notebooku jako heatmapa.

### US-2 — Prolomení libovolného ciphertextu
**Jako** uživatel  
**chci** zavolat jednu funkci nad zašifrovaným textem,  
**abych** dostal nejlepší odhad klíče a dešifrovaný text.

**Akceptační kritéria:**
- Funkce `prolom_substitute(text, TM_ref, iter, start_key)` vrací `(key, decrypted, log_plausibility)`.
- Pro text ≥ 1000 znaků a 20 000 iterací konverguje k textu, kde > 90 % znaků odpovídá originálu (heuristicky ověřeno).
- Při `start_key=None` se vygeneruje náhodný start.

### US-3 — Demonstrační notebook
**Jako** student/vyučující  
**chci** otevřít jeden notebook a vidět celý workflow,  
**abych** porozuměl tomu, co knihovna umí.

**Akceptační kritéria:**
- Notebook `notebooks/demo.ipynb` obsahuje sekce: úvod → šifrování → bigramová matice → vizualizace → kryptoanalýza vlastního textu → kryptoanalýza textů od vyučujícího → analýza úspěšnosti → závěr.
- Vizualizace: heatmap matice, plot konvergence log-plausibility v čase.

### US-4 — Export podle naming konvence
**Jako** vyučující  
**chci** dostat výsledky pojmenované přesně podle vzoru,  
**abych** je mohl automaticky zkontrolovat.

**Akceptační kritéria:**
- Pro každý dešifrovaný text vznikají dva soubory `text_{délka}_sample_{id}_plaintext.txt` a `text_{délka}_sample_{id}_key.txt` v `outputs/`.
- Obsah souborů je čistý text bez metadat.
- 20 000 iterací M-H pro každý text.

### US-5 — Notebook v HTML/PDF
**Jako** odevzdávající student  
**chci** notebook převést do HTML nebo PDF,  
**abych** mohl odevzdat staticky čitelnou verzi.

**Akceptační kritéria:**
- `docs/exports/demo.html` (a/nebo `demo.pdf`) se generují jedním příkazem.
- Czech text se zobrazuje korektně (diakritika).

---

## 7. Co je potřeba dodělat — technicky

### Nové funkce a moduly

#### `sifry/cryptanalysis.py`

```python
def plausibility(text: str, TM_ref: np.ndarray) -> float:
    """Log-likelihood textu vzhledem k referenční bigramové matici.

    Sestaví TM_obs z textu (absolutní bigramy, alphabet zarovnaný s TM_ref).
    Vrátí sum_{i,j} log(TM_ref[i,j]) * TM_obs[i,j].
    """
```

Implementační poznámky:
- `TM_ref` je relativní (součet = 1) → použít `np.log` přímo.
- `TM_obs` je absolutní (nebo relativní — výsledek je úměrný), ale **musí** používat stejné indexování abecedy jako `TM_ref`.
- Vrací `float` v záporném rozsahu (log pravděpodobnosti).

```python
def prolom_substitute(
    text: str,
    TM_ref: np.ndarray,
    iter: int,
    start_key: str | None = None,
    accept_prob: float = 0.01,
    log_every: int = 50,
) -> tuple[str, str, float]:
    """M-H algoritmus pro prolomení substituční šifry.

    Vrací (best_key, best_decrypted, best_log_plausibility).
    """
```

Implementační poznámky podle pseudokódu v zadání:
- Pokud `start_key is None`, vygenerovat náhodnou permutaci `ALPHABET`.
- V každé iteraci: prohodit 2 náhodné pozice v klíči, spočítat novou plausibility.
- **Pozor:** plausibility je log, tedy poměr `p_new / p_current` se musí počítat jako `exp(p_new - p_current)`, jinak overflow / nesmyslné hodnoty. Alternativně lze rozhodnutí dělat čistě v log-prostoru: pokud `p_new > p_current` přijmout, jinak přijmout s pravděpodobností `accept_prob` (pseudokód v zadání toto skutečně dělá — fixní 0.01).
- Uchovat **best_key, best_p** napříč iteracemi (zadání: „uchovává klíč, který dosáhl nejvyšší věrohodnosti“). Pseudokód v PDF na to však zapomíná — vrací current_key. Implementujeme správně.
- Logovat každých `log_every` iterací: `print("Iteration", i, "log plausibility:", p_current)`.

#### `sifry/utils.py`

```python
def load_reference_text(path: str) -> str:
    """Načte a normalizuje text z disku."""

def export_decryption(
    text_id: int,
    plaintext: str,
    key: str,
    out_dir: str = "outputs",
) -> tuple[str, str]:
    """Zapíše plaintext a klíč podle naming konvence ze zadání.

    Vrací cesty k oběma souborům.
    Pattern: text_{len(plaintext)}_sample_{text_id}_plaintext.txt
             text_{len(plaintext)}_sample_{text_id}_key.txt
    """

def build_reference_matrix(text: str, alphabet: str = ALPHABET) -> np.ndarray:
    """Convenience wrapper: normalize → bigrams → transition_matrix(relative=True)."""
```

### Refactor existujícího kódu

- **Přesun** `sifry/src/substitution_cipher.py` → `sifry/cipher.py`, smazat `src/` adresář.
- **`sifry/__init__.py`** udělat skutečným package init s re-exporty:
  ```python
  from .cipher import (
      ALPHABET, validate_key, normalize_text,
      get_bigrams, transition_matrix,
      substitute_encrypt, substitute_decrypt,
  )
  from .cryptanalysis import plausibility, prolom_substitute
  from .utils import (
      load_reference_text, export_decryption, build_reference_matrix,
  )
  ```
- **Testy** přesunout `sifry/tests/` → `tests/` (na úrovni repo rootu), odstranit `sys.path` hack a používat `from sifry import ...`.
- **`pyproject.toml`** nahradí `setup.py` + `requirements.txt`.

### Reálná data

- Stáhnout Krakatit z `https://cs.wikisource.org/wiki/Krakatit` (proklikat všechny kapitoly nebo vzít přímo source). Lze i `curl` + cleanup HTML tagů (např. přes `beautifulsoup4` jednorázově), pak spustit `normalize_text` a uložit do `sifry/data/reference/krakatit.txt`.
- Soubory od vyučujícího uložit do `sifry/data/encrypted/`.

### Nové testy

| Modul                  | Test                                                          |
| ---------------------- | ------------------------------------------------------------- |
| `cryptanalysis`        | `plausibility` známého textu > plausibility náhodného textu   |
| `cryptanalysis`        | `prolom_substitute` na vlastnoručně šifrovaném textu vrátí klíč shodný s ~80%+ pozic   |
| `utils`                | `export_decryption` vytvoří správně pojmenované soubory       |
| `utils`                | `load_reference_text` načte a normalizuje                     |

---

## 8. Použití knihovny v Jupyter notebooku

### Předpoklady

```bash
pip install -e .[notebook]   # editable install + jupyter, matplotlib, …
jupyter lab                  # nebo: jupyter notebook
```

### Doporučená struktura `notebooks/demo.ipynb`

| # | Buňka     | Obsah                                                                 |
| - | --------- | --------------------------------------------------------------------- |
| 1 | Markdown  | Titulní strana, autor, datum, abstrakt                                |
| 2 | Markdown  | Úvod — popis problému, abecedy, M-H algoritmu                         |
| 3 | Code      | Import knihovny                                                       |
| 4 | Code      | Demo šifrování + dešifrování na příkladu z PDF                        |
| 5 | Markdown  | Sestavení bigramové matice                                            |
| 6 | Code      | Načtení Krakatitu + `build_reference_matrix()`                        |
| 7 | Code      | Vizualizace matice (matplotlib heatmap se štítky abecedy)             |
| 8 | Markdown  | Kryptoanalýza vlastního testovacího textu                             |
| 9 | Code      | Zašifrovat krátký text, spustit `prolom_substitute(iter=5000)`, porovnat |
| 10 | Markdown | Kryptoanalýza textů od vyučujícího                                    |
| 11 | Code     | Loop přes všechny texty: 20 000 iterací + export + plot konvergence    |
| 12 | Markdown | Analýza úspěšnosti                                                    |
| 13 | Code     | Procento správně dešifrovaných znaků na ground-truth (kde dostupné)   |
| 14 | Markdown | Závěr a poznámky                                                      |

### Konkrétní kód do buněk

```python
# Cell 3 — import
from sifry import (
    ALPHABET,
    substitute_encrypt, substitute_decrypt,
    normalize_text, get_bigrams, transition_matrix,
    plausibility, prolom_substitute,
    build_reference_matrix, export_decryption,
)
import numpy as np
import matplotlib.pyplot as plt
```

```python
# Cell 4 — demo šifrování
plain = "BYL_POZDNI_VECER_PRVNI_MAJ_VECERNI_MAJ_BYL_LASKY_CAS"
key   = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"
cipher = substitute_encrypt(plain, key)
decoded = substitute_decrypt(cipher, key)
print("ciphertext:", cipher)
print("decoded   :", decoded)
assert decoded == plain
```

```python
# Cell 6 — bigramová matice z Krakatitu
with open("../sifry/data/reference/krakatit.txt", encoding="utf-8") as f:
    ref_text = normalize_text(f.read())
TM_ref = transition_matrix(get_bigrams(ref_text), ALPHABET, relative=True)
print(f"Délka ref. textu: {len(ref_text):,} znaků")
print(f"Součet TM_ref: {TM_ref.sum():.6f}  (má být ~1.0)")
```

```python
# Cell 7 — heatmap
fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(np.log(TM_ref), cmap="viridis")
ax.set_xticks(range(27), list(ALPHABET))
ax.set_yticks(range(27), list(ALPHABET))
ax.set_xlabel("druhý znak")
ax.set_ylabel("první znak")
ax.set_title("log(P(bigram)) — Krakatit")
plt.colorbar(im); plt.tight_layout(); plt.show()
```

```python
# Cell 9 — kryptoanalýza
np.random.seed(42)
best_key, decrypted, score = prolom_substitute(
    text=cipher, TM_ref=TM_ref, iter=20000, start_key=None,
)
print("Best key  :", best_key)
print("Decrypted :", decrypted[:200], "…")
print("Score     :", score)
```

```python
# Cell 11 — batch + export
import glob, os
for path in sorted(glob.glob("../sifry/data/encrypted/text_*_ciphertext.txt")):
    fname = os.path.basename(path)
    # parse text_1000_sample_1_ciphertext.txt → délka=1000, id=1
    _, length, _, sample_id, _ = fname.replace(".txt", "").split("_")
    with open(path) as f:
        cipher_text = f.read().strip()
    key, plaintext, _ = prolom_substitute(
        text=cipher_text, TM_ref=TM_ref, iter=20000,
    )
    export_decryption(
        text_id=int(sample_id),
        plaintext=plaintext,
        key=key,
        out_dir="../outputs",
    )
```

---

## 9. Export notebooku do HTML/PDF

### Předpoklady (jednorázově)

```bash
pip install nbconvert jupyter
```

### HTML — nejjednodušší cesta

```bash
jupyter nbconvert --to html notebooks/demo.ipynb \
    --output-dir docs/exports/
```

Bez externích závislostí, vždy funguje, vhodné pro odevzdání.

### PDF přes WebPDF (Chromium) — doporučená cesta pro PDF

```bash
pip install "nbconvert[webpdf]"
playwright install chromium

jupyter nbconvert --to webpdf notebooks/demo.ipynb \
    --output-dir docs/exports/
```

Renderuje stejně jako prohlížeč → diakritika a unicode bez problémů. Nepotřebuje LaTeX.

### PDF přes LaTeX (alternativa, vyšší kvalita typografie)

```bash
brew install --cask basictex
# nebo: brew install --cask mactex (větší, kompletní)
eval "$(/usr/libexec/path_helper)"      # přidá tex do PATH
sudo tlmgr update --self
sudo tlmgr install collection-latexextra babel-czech

jupyter nbconvert --to pdf notebooks/demo.ipynb \
    --output-dir docs/exports/
```

**Pozor na češtinu:** výchozí `pdflatex` template nemusí umět diakritiku. Buď použít `--template=…` s XeTeX, nebo přidat do prvního markdown buňky:
```latex
% raw_latex
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
```

### Doporučení pro tento projekt

Pro odevzdání **stačí HTML**. PDF přes WebPDF je druhá nejjednodušší možnost. LaTeX cesta dává nejhezčí výstup, ale má největší overhead.

---

## 10. Roadmap úkolů (priorita shora dolů)

1. **Refaktor balíčku** — `src/` → `sifry/`, oprava `__init__.py`, migrace `setup.py` → `pyproject.toml`.
2. **Reálná data** — stáhnout a normalizovat Krakatit → `sifry/data/reference/krakatit.txt`.
3. **`cryptanalysis.plausibility()`** + unit testy.
4. **`cryptanalysis.prolom_substitute()`** + integrační test (encrypt → break → verify).
5. **`sifry/utils.py`** s `load_reference_text`, `export_decryption`, `build_reference_matrix`.
6. **Notebook** `notebooks/demo.ipynb` podle struktury v §8.
7. **Batch běh** na poskytnutých textech (20 000 iterací každý) + export do `outputs/`.
8. **Export notebooku** do `docs/exports/demo.html` (+ volitelně PDF).
9. **`docs/REPORT.md`** — stručné shrnutí metod a výsledků (1–2 strany).
10. **(Volitelné)** Základní GitHub Action `.github/workflows/test.yml` — `pip install -e .[dev] && pytest`.

---

## 11. Identifikované drobné chyby k opravě při refaktoru

| # | Lokace                                | Co                                                                                                   | Akce |
| - | ------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---- |
| 1 | `sifry/setup.py:55-58`                | `requests>=2.25.0` v `install_requires`, nikde nepoužito                                             | Smazat |
| 2 | `sifry/setup.py:36-38`                | `author_email='your.email@example.com'`                                                              | Vyplnit reálný e-mail (zikmund.d@gmail.com) |
| 3 | `sifry/setup.py:1-9`                  | Soubor je AI-generovaný s explicitním varováním autora                                               | Nahradit `pyproject.toml` |
| 4 | `sifry/src/__init__.py:4`             | `sys.path.insert(0, …)` hack                                                                          | Odstranit po restrukturalizaci |
| 5 | `sifry/tests/test_basic_cipher.py:4`  | Stejný `sys.path` hack                                                                                | Odstranit, použít `from sifry import …` |
| 6 | `sifry/src/substitution_cipher.py:58` | `matrix += 1.0` přičítá ke všem buňkám (vs. pseudokód, který říká „jen tam, kde je 0“)              | Buď přepsat podle PDF, nebo dokumentovat odchylku (Laplace smoothing je matematicky čistší, výsledek M-H se prakticky neliší) |
| 7 | `sifry/cipher/`, `sifry/utils/`, `sifry/notebooks/` | Prázdné placeholder složky                                                                | Po restrukturalizaci buď naplnit, nebo smazat |

---

## 12. Souhrn pro odevzdání

Dle zadání se odevzdává:

- ✅ **Zdrojový kód** knihovny s povinnou dokumentací funkcí.
- ✅ **Jupyter notebook** ve formátu PDF nebo HTML.
- ✅ **Stručný report** se shrnutím metod a výsledků.
- ✅ **Exportované klíče a plaintexty** (`text_*_plaintext.txt`, `text_*_key.txt`).

Aktuálně máme bod 1 z ~25 % (jen úkol 1 ze 5). Zbývá doimplementovat kryptoanalýzu, sestavit notebook, vyexportovat ho a spustit na poskytnutých datech.

---

*Dokument vygenerován ze zadání `zadani.pdf` a stavu repa na větvi `main` (commit `09b6d78`).*
