# Testing — Adresowo Scraper

---

## Uruchomienie testów

```bash
# Wszystkie testy
pytest test_parser.py -v

# Wybrana klasa
pytest test_parser.py::TestBrakujaceDane -v

# Pojedynczy test
pytest test_parser.py::TestPierwszeOgloszenie::test_price_total_zl -v

# Testy parametryzowane (konkretny przypadek)
pytest "test_parser.py::TestIntZTekstu::test_poprawne_wartosci[399 000-399000]" -v

# Z raportem pokrycia (wymaga pytest-cov)
pytest test_parser.py -v --cov=parser --cov-report=term-missing
```

---

## Struktura testów

Plik: `test_parser.py` | Fixture HTML: `sample_page.html`

```
test_parser.py
│
├── Fixtures (scope="module")
│   ├── sample_html()     # wczytuje sample_page.html raz dla modułu
│   ├── rekordy()         # parsuje HTML → list[dict]
│   ├── r0() – r3()       # skróty do konkretnych rekordów
│
├── TestLiczbaOgloszen         # liczba i kompletność wyników
├── TestPierwszeOgloszenie     # pola rekordu r0 (Łódź Śródmieście, 54m², 399 000 zł)
├── TestDrugieOgloszenie       # pola rekordu r1 (Łódź Śródmieście, 50m², 340 000 zł)
├── TestPowierzchniaZPrzecinkiem  # r2: konwersja '50,5 m²' → float 50.5
├── TestBrakujaceDane          # r3: None dla pustych pól; odrzucanie bez locality/url
├── TestIntZTekstu             # _int_z_tekstu() — parametryzowane (8 przypadków)
└── TestFloatZTekstu           # _float_z_tekstu() — parametryzowane (7 przypadków)
```

Łącznie: **42 testy**, wynik oczekiwany: **42 passed**.

---

## Fixture: sample_page.html

Plik zawiera 4 ogłoszenia celowo dobrane pod kątem pokrycia przypadków:

| Rekord | Dzielnica | Dane | Cel |
|---|---|---|---|
| `r0` (id: 3939824) | Łódź Śródmieście | kompletne, 54 m², 399 000 zł | happy path |
| `r1` (id: 3966006) | Łódź Śródmieście | kompletne, 50 m², 340 000 zł | drugi happy path |
| `r2` (id: 3901234) | Łódź Bałuty | powierzchnia `50,5` (przecinek) | konwersja float |
| `r3` (id: 3999999) | Łódź Polesie | puste `<span>` ceny i powierzchni | edge case |

Przy zmianie struktury HTML adresowo.pl: zaktualizuj `sample_page.html` przykładowym fragmentem nowej struktury, uruchom testy — pokażą które selektory są zepsute.

---

## Grupy testów — opis

### TestLiczbaOgloszen

Weryfikuje że `parsuj_strone()` zwraca dokładnie tyle rekordów ile jest poprawnych `div[data-offer-card]` w HTML, żaden nie jest `None`, a pusta strona daje pustą listę.

### TestPierwszeOgloszenie / TestDrugieOgloszenie

Sprawdzają każde pole rekordu osobno: `id`, `locality`, `rooms`, `area_m2`, `price_total_zl`, `price_per_m2_zl`, `url`. Dla `price_per_m2_zl` weryfikuje formułę `round(cena / m²)`.

### TestPowierzchniaZPrzecinkiem

Kluczowy test dla polskiego formatu liczb. Tekst `'50,5 m²'` musi być sparsowany jako `float` 50.5 — funkcja `_float_z_tekstu()` zastępuje przecinek kropką przed konwersją.

### TestBrakujaceDane

Cztery scenariusze brakujących danych:
- Puste `<span class="font-bold">` → pole zwraca `None` (nie `0`, nie `''`)
- Brak obu składników → `price_per_m2_zl = None`
- Brak `locality` w HTML → `parsuj_ogloszenie()` zwraca `None`
- Brak `<a href>` w `<h2>` → `parsuj_ogloszenie()` zwraca `None`

### TestIntZTekstu / TestFloatZTekstu

Parametryzowane testy funkcji pomocniczych. Weryfikują obsługę separatorów tysięcy (spacja, `\xa0`), polskiego przecinka dziesiętnego, pustego stringa i tekstu nienumerycznego.

---

## Dodawanie nowych testów

### Nowy przypadek parsowania

1. Dodaj ogłoszenie do `sample_page.html` z odpowiednią strukturą HTML.
2. Dodaj fixture `r4(rekordy)` lub użyj `REKORDY[4]` bezpośrednio.
3. Napisz metodę w odpowiedniej klasie lub utwórz nową klasę `TestNazwaScenariusza`.

### Nowa funkcja pomocnicza

Używaj `@pytest.mark.parametrize` dla zestawu wejście → oczekiwane wyjście:

```python
@pytest.mark.parametrize("wejscie,oczekiwane", [
    ("100 000", 100_000),
    ("0",       0),
])
def test_poprawne_wartosci(self, wejscie, oczekiwane):
    assert _int_z_tekstu(wejscie) == oczekiwane
```

### Test API (przyszłość)

Testy integracyjne endpointów FastAPI wymagają `httpx` i `pytest-asyncio`:

```python
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_get_cities():
    resp = client.get("/api/cities")
    assert resp.status_code == 200
    assert any(c["key"] == "lodz" for c in resp.json())
```

---

## Zasady

- Każda funkcja publiczna w `parser.py` musi mieć co najmniej jeden test.
- Funkcje pomocnicze (`_int_z_tekstu`, `_float_z_tekstu`) testowane są parametrycznie — nie dodawaj osobnych metod dla każdej wartości.
- Fixtures z `scope="module"` — HTML parsowany raz, nie przed każdym testem.
- Nie mockuj `requests` w testach parsera — testy operują na statycznym HTML z `sample_page.html`, bez połączeń sieciowych.
