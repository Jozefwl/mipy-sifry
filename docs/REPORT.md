# Správa: Kryptoanalýza substitučnej šifry

Stručný prehľad implementačného postupu, použitých metód a dosiahnutých výsledkov.

## Cieľ

Cieľom bolo vytvoriť Python knižnicu, ktorá umožní:

- šifrovanie a dešifrovanie textu substitučnou šifrou,
- automatické prolomenie (kryptoanalýzu) tejto šifry pomocou štatistických metód,
- aplikáciu knižnice na zašifrované testovacie dáta a export výsledkov.

## Implementačný postup

**Python knižnica `sifry`**

- Normalizácia textu (veľké písmená, bez diakritiky, medzera ako `_`)
- `substitute_encrypt` a `substitute_decrypt` pre substitučnú šifru
- `get_bigrams` a `transition_matrix` na sestavenie prechodovej matice
- `plausibility` na výpočet likelihood (věrohodnosti) dešifrovaného textu
- `prolom_substitute` na prolomenie šifry algoritmom Metropolis-Hastings (M-H)
- `export_decryption` na uloženie plaintextu a kľúča

**Notebook `notebooks/kryptoanalyza.ipynb`**

1. Šifrovanie a dešifrovanie s known key
2. Vytvorenie teoretickej bigramovej matice z textu Krakatit (Wikisource)
3. Kryptoanalýza s viacerými seedmi a výber najlepšieho výsledku podľa plausibility
4. Vizualizácia (grafy plausibility, porovnanie prechodových matic)
5. Dešifrovanie testovacích súborov a výpis do konzoly
6. Export dešifrovaných textov a kľúčov do priečinka `outputs`

## Použité metódy

**Substitučná šifra**

Klíč je permutácia abecedy (27 znakov: A-Z a `_`). Každý znak prostého textu sa nahradí znakom z kľúča. Výsledok je kryptogram.

**Bigramy a prechodová matica**

Bigramy sú dvojice po sebe idúcich znakov. Z referenčného českého textu (Krakatit, cca 452 tisíc znakov) sme postupne:

1. vytvorili **absolútnu maticu prechodov** (počty bigramov),
2. k bunkám s nulou pripočítali 1 (aby sa pri logaritme nevyskytla log(0)),
3. z absolútnej matice vypočítali **relatívnu prechodovú maticu** `TM_ref` (súčet prvkov = 1).

Táto `TM_ref` slúži ako referenčný jazykový model češtiny.

**Plausibility (likelihood / věrohodnost)**

Funkcia `plausibility(text, TM_ref)` porovná bigramovú štruktúru dešifrovaného textu s referenčnou maticou. Výpočet:

```
likelihood = Σ log(TM_ref[i,j]) × TM_obs[i,j]
```

kde `TM_obs` je absolútna prechodová matica pozorovaného textu. Vyššia hodnota znamená lepšiu zhodu s referenčným modelom.

**Metropolis-Hastings (M-H) algoritmus**

Algoritmus `prolom_substitute(text, TM_ref, iter, start_key)` iteratívne:

1. náhodne vymení dva znaky v kandidátnom kľúči,
2. dešifruje kryptogram a spočíta plausibility,
3. prijme lepší kľúč vždy, horší s pravdepodobnosťou 0.01 (podľa pseudokódu v zadaní),
4. uchová kľúč s najvyššou dosiahnutou plausibility.

Parametre v praxi:

- `iter` = 20 000 iterácií na jeden beh
- `start_key` náhodne alebo cez seed
- pravdepodobnosť prijatia horšieho kandidáta: 0.01

**Multi-seed prístup (doplnok v notebooku)**

Pri demonštrácii na známom texte sme spustili viac behov s rôznymi seedmi a vybrali ten s najvyššou plausibility. Toto nie je v zadaní povinné, ale zlepšuje stabilitu výsledku.

**Export výsledkov**

Podľa zadania pre každý dešifrovaný text ukladáme:

- `text_{dĺžka}_sample_{id}_plaintext.txt`
- `text_{dĺžka}_sample_{id}_key.txt`

Súbory obsahujú len čistý text. Export je v priečinku `outputs`. Príklad formátu je v zadaní pre `text_1000_sample_1`.

## Dosiahnuté výsledky

**Knižnica a testy**

- Knižnica `sifry` implementuje povinné funkcie podľa zadania (`get_bigrams`, `transition_matrix`, `plausibility`, `prolom_substitute`, `substitute_encrypt`, `substitute_decrypt`)
- Unit testy overujú šifru, kryptoanalýzu a export

**Demonštrácia na známom texte (sekcia 3 notebooku)**

- Pri teste na vlastnom zašifrovanom texte najlepší seed dosiahol približne **95,6 %** zhodu s originálom
- Dešifrovaný text bol čitateľný a prechodová matica sa podobala `TM_ref`

**Testovacie súbory (sekcie 5 a 6)**

- Spracovaných **60 kryptogramov** z `data/testovaci_soubory` (20× dĺžka 250, 20× 500, 20× 1000)
- Všetky exportované do `outputs` (120 súborov: plaintext + key)
- Referenčný text: Krakatit, kryptoanalýza podľa českého bigramového modelu

**Kvalita prolomenia**

- Dlhšie kryptogramy (500 a 1000 znakov) dávajú lepšie výsledky, lebo majú viac bigramov na štatistiku
- Kratšie texty (250 znakov) sú náročnejšie a môžu mať viac chýb v jednotlivých znakoch
- Pri jednom seede pre všetky súbory nemusí byť výsledok optimálny pre každý text. Odporúčané je skúšať viac behov M-H a vybrať najlepšiu plausibility

**Príklad**

Dešifrovaný úryvok z `text_1000_sample_10` obsahuje rozpoznateľné pasáže z Krakatitu (Prokop, dialógy). Niektoré znaky sú stále zamenené, ale jazyková štruktúra je zreteľná.

## Záver

Projekt spĺňa požiadavky zadania: funkčná knižnica, notebook s postupom od šifrovania po kryptoanalýzu, export plaintextov a kľúčov. M-H algoritmus s bigramovou `TM_ref` dokáže bez znalosti kľúča obnoviť texty s vysokou presnosťou, najmä pri dostatočne dlhých kryptogramoch.

Možné vylepšenia:

- pre každý kryptogram viac behov M-H s rôznymi `start_key` a výber podľa plausibility
- pri krátkych textoch zvýšiť počet iterácií `iter`
- porovnať dešifrovaný plaintext s originálom, ak je k dispozícii (presnosť v percentách)
