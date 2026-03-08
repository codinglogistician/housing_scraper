# Contributing — Adresowo Scraper

---

## Środowisko deweloperskie

```bash
git clone <repo>
cd housing_scraper
pip install -r requirements.txt
```

Wymagania: Python 3.11+.

---

## Konwencje kodu

### Python

- Type hints wymagane na wszystkich funkcjach publicznych.
- Docstringi na funkcjach publicznych — krótkie, opisują co i dlaczego, nie jak.
- PEP 8. Nazwy zmiennych i komentarze po polsku (wyjątek: publiczne API, README).
- `from __future__ import annotations` w każdym module.
- Zwracaj `None` dla brakujących danych — nigdy pusty string ani `0`.

```python
# Dobrze
def parsuj_ogloszenie(item: Tag) -> dict | None:
    """Parsuje pojedynczy div[data-offer-card]. Zwraca None gdy brak locality lub url."""
    ...

# Źle
def parse(item):
    ...
```

### Nazewnictwo

| Element | Konwencja | Przykład |
|---|---|---|
| Funkcje Python | `snake_case` PL | `parsuj_ogloszenie`, `deduplikuj` |
| Klasy testów | `PascalCase` PL | `TestBrakujaceDane` |
| Metody testów | `test_` + opis PL | `test_brakujaca_cena_zwraca_none` |
| Pliki danych | `adresowo_{slug}.csv` | `adresowo_poznan.csv` |
| Zmienne JS | `camelCase` PL | `currentCity`, `districtData` |

### JavaScript (dashboard.html)

- Czysty JS — bez frameworków, bez bundlera.
- Stan globalny jako zmienne modułu (`let allData = []`).
- Funkcje nazwane po polsku, w `camelCase`.
- CSS Variables dla wszystkich kolorów i rozmiarów — bez hardkodowanych wartości.

---

## Dodawanie nowego miasta

1. **Zweryfikuj slug:**
   ```python
   import requests
   r = requests.get('https://adresowo.pl/mieszkania/{slug}/', allow_redirects=True)
   print(r.url)  # musi zawierać slug, nie być stroną główną
   ```

2. **Dodaj do `CITIES` w `api.py`:**
   ```python
   CITIES = {
       "lodz":          "Łódź",
       "poznan":        "Poznań",
       "swinoujscie-h": "Świnoujście",
       "nowy-slug":     "Nowe Miasto",   # ← dodaj tu
   }
   ```

3. **Zescrapuj dane:**
   ```bash
   python scraper.py --city nowy-slug --pages 8 --output adresowo_nowy-slug.csv
   ```

4. **Zrestartuj API** i zweryfikuj w dashboardzie.

---

## Aktualizacja parsera po zmianie HTML adresowo.pl

Adresowo.pl może zmienić strukturę HTML bez ostrzeżenia. Gdy liczba scrapowanych ogłoszeń spada do zera:

1. Pobierz aktualny HTML strony listingowej.
2. Znajdź nowy selektor kontenera ogłoszenia (był: `div[data-offer-card]`).
3. Zaktualizuj selektory w `parser.py`.
4. Zaktualizuj `sample_page.html` przykładowym fragmentem nowej struktury.
5. Uruchom testy — powinny wskazać które pola się zepsuły.
6. Popraw testy jeśli zmieniły się selektory lub struktura danych.

---

## Testy

Przed każdym commitem uruchom pełny zestaw testów:

```bash
pytest test_parser.py -v
```

Wymagane: **wszystkie 42 testy muszą przejść**. Nie commituj kodu z failującymi testami.

Dodając nową funkcję parsera:
- Dodaj przypadek do `sample_page.html`.
- Napisz test w odpowiedniej klasie lub utwórz nową.
- Przy funkcjach pomocniczych użyj `@pytest.mark.parametrize`.

---

## Struktura commitów

```
typ: krótki opis (max 72 znaki)

Opcjonalne rozwinięcie wyjaśniające decyzję.
```

Typy: `feat` · `fix` · `refactor` · `test` · `docs` · `chore`

Przykłady:
```
feat: dodaj miasto Gdańsk z weryfikacją slugu
fix: deduplikacja po id przed zapisem CSV
test: dodaj edge case dla ogłoszenia bez ceny
docs: aktualizuj TASKS po wdrożeniu sortowania
```
