# Architecture — Adresowo Scraper

---

## Przegląd

System składa się z trzech warstw: scraper CLI, backend REST API i frontend SPA. Dane przepływają jednostronnie: adresowo.pl → parser → CSV → API → dashboard.

```
┌─────────────────────────────────────────────────────────┐
│                      adresowo.pl                        │
│              (HTML, paginacja, Tailwind CSS)            │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP GET (requests)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    scraper.py (CLI)                     │
│  pobierz_strone() → parsuj_strone() → deduplikuj()     │
│                        ↓                                │
│                    zapisz_csv()                         │
└───────────────────────┬─────────────────────────────────┘
                        │ CSV (utf-8-sig)
                        ▼
┌──────────────────────────────────────┐
│  adresowo_{miasto}.csv               │
│  (jeden plik per miasto, na dysku)   │
└───────────────┬──────────────────────┘
                │ csv.DictReader
                ▼
┌─────────────────────────────────────────────────────────┐
│                     api.py (FastAPI)                    │
│  GET /api/cities     → lista miast                      │
│  GET /api/data       → JSON z rekordami                 │
│  POST /api/run-tests → subprocess pytest → JSON         │
│  GET /               → dashboard.html                   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP JSON (fetch)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   dashboard.html (SPA)                  │
│  Ogłoszenia │ Statystyki │ Test Runner                  │
└─────────────────────────────────────────────────────────┘
```

---

## Moduły

### `parser.py`

Odpowiedzialność: parsowanie pojedynczej strony HTML adresowo.pl do listy słowników.

```
parsuj_strone(html: str) -> list[dict]
    └── parsuj_ogloszenie(item: Tag) -> dict | None
            ├── _wartosc_przed_jednostka()   # wyciąga wartość przed 'zł'/'m²'/'pok.'
            ├── _int_z_tekstu()              # '399 000' → 399000, None dla błędów
            └── _float_z_tekstu()            # '50,5' → 50.5, None dla błędów
```

Kluczowe decyzje:
- `parsuj_ogloszenie` zwraca `None` gdy brak `locality` lub `url` — filtruje bezużyteczne rekordy na wejściu, nie na wyjściu.
- `price_per_m2_zl` wyliczana lokalnie (`round(cena / m²)`) — strona listingowa nie eksponuje tej wartości bezpośrednio.
- Selektor kontenera: `div[data-offer-card]` — wynika ze struktury Tailwind aktualnej wersji adresowo.pl (zmienione z `section.search-results__item` w poprzedniej wersji).

### `scraper.py`

Odpowiedzialność: paginacja, HTTP, deduplikacja, zapis CSV.

```
uruchom(miasto, strony, plik_wyjsciowy)
    └── pobierz_strone(sesja, miasto, nr) -> str | None
    └── parsuj_strone(html) -> list[dict]         # z parser.py
    └── deduplikuj(rekordy) -> list[dict]
    └── zapisz_csv(rekordy, sciezka)
```

Kluczowe decyzje:
- Deduplikacja po `id` jest niezbędna — adresowo.pl wyświetla promowane ogłoszenia na każdej stronie paginacji, co przy 8 stronach może dawać 7× powielenie tego samego rekordu.
- Paginacja: strona 1 używa `/mieszkania/{miasto}/`, kolejne `/_l{nr}` — asymetria wynika ze struktury URL portalu.
- Throttle `time.sleep(0.5)` między stronami — brak mechanizmu retry (dodać z `tenacity` w przyszłości).

### `api.py`

Odpowiedzialność: REST API + serwowanie dashboardu.

Endpointy:

| Metoda | Ścieżka | Opis |
|---|---|---|
| `GET` | `/` | Serwuje `dashboard.html` |
| `GET` | `/api/cities` | Lista miast z flagą `available` |
| `GET` | `/api/data?city={klucz}` | Rekordy z CSV jako JSON |
| `POST` | `/api/run-tests` | Uruchamia pytest, zwraca per-test status |

Kluczowe decyzje:
- CSV czytany przy każdym żądaniu — brak cache. Wystarczające dla obecnej skali (~1000 rekordów); przy większych zbiorach dodać cache in-memory.
- `POST /api/run-tests` uruchamia subprocess `pytest -v` i parsuje stdout. Alternatywa (pytest API przez `pytest.main()`) utrudniałaby izolację środowiska.
- CORS `allow_origins=["*"]` — środowisko developerskie, nie produkcja.

### `dashboard.html`

Odpowiedzialność: prezentacja danych, filtrowanie, test runner.

Stan aplikacji:
```javascript
allData        // wszystkie rekordy z API (niezmienne po załadowaniu)
filteredData   // po zastosowaniu filtrów i sortowania
districtData   // cache dla tabeli dzielnic (buildStats → renderDistrictTable)
currentCity    // aktywne miasto
sortCol/sortDir         // stan sortowania tabeli ogłoszeń
districtSortCol/Dir     // stan sortowania tabeli dzielnic
testResults    // { node_id: 'PASSED'|'FAILED' }
```

Przepływ danych w dashboardzie:
```
init()
  └── buildCityButtons()  ← GET /api/cities
  └── loadCity(city)
        └── GET /api/data?city=...
        └── applyFilters() → renderTable()
        └── updateTicker()
        └── buildStats() → renderDistrictTable()
```

---

## Decyzje architektoniczne

### Dlaczego CSV zamiast bazy danych?

Projekt to narzędzie analityczne do jednorazowych sesji eksploracyjnych, nie system z wieloma użytkownikami ani zapisem w czasie rzeczywistym. CSV jest wystarczający: otwieralny w Excelu, wersjonowany w Git, prosty w naprawie ręcznej. Migracja do SQLite byłaby uzasadniona gdyby pojawiły się zapytania wieloparametryczne po stronie serwera lub historia zmian cen.

### Dlaczego jeden plik HTML bez frameworka?

Dashboard ma służyć jako standalone narzędzie uruchamiane lokalnie przez jedną osobę. Zero zależności budowania (webpack, node_modules) = zero problemów z środowiskiem. Vanilla JS jest wystarczający dla ~500 linii logiki.

### Dlaczego FastAPI zamiast prostego `http.server`?

`http.server` nie obsługuje CORS ani dynamicznych endpointów. FastAPI daje automatyczną walidację (Pydantic), dokumentację `/docs` i łatwe rozszerzanie o nowe endpointy bez boilerplate.
