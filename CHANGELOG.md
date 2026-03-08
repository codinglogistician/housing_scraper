# Changelog — Adresowo Scraper

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/)

---

## [Unreleased]

### Dodano
- Eksport danych do JSON, Markdown, XLSX i PDF — przycisk w pasku nad tabelą; eksportuje zaznaczone rekordy (jeśli są) lub wszystkie przefiltrowane; nagłówek raportu zawiera miasto i aktywne filtry
- Checkboxy przy każdym wierszu tabeli — zaznaczenie ≥1 rekordu ogranicza eksport do wybranych pozycji; checkbox w nagłówku zaznacza/odznacza całą bieżącą stronę
- Przelicznik ceny mieszkania — przycisk "Przelicz" obok każdego ogłoszenia otwiera popup z przeliczeniem ceny na kebaby (÷35 zł), hot-dogi Żabka (÷8,50 zł) i piwa Żabka (÷4,65 zł)

### Planowane
- Automatyczne wykrywanie zmiany struktury HTML (ostrzeżenie przy < 10 ogłoszeń/stronę)
- Walidacja slugu przed scrapingiem (sprawdzenie redirect HTTP)
- Obsługa HTTP 429 z exponential backoff
- Więcej miast: Gdańsk, Wrocław, Kraków, Warszawa
- Wykres rozkładu cen w dashboardzie
- Eksport filtrowanych danych z dashboardu do CSV
- Testy integracyjne API (httpx + pytest-asyncio)

---

## [1.3.0] — 2026-03-08

### Dodano
- Selektor miasta w topbarze dashboardu (Łódź / Poznań / Świnoujście)
- Sortowanie kolumn w tabeli statystyk dzielnic (klik nagłówka, strzałki ↑↓)
- Skill Claude Code `adresowo-scraper` z pełnym kontekstem projektowym
- Pliki dokumentacji: `README.md`, `TASKS.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `TESTING.md`, `CHANGELOG.md`

### Naprawiono
- Błędny slug Świnoujścia (`swinoujscie` → `swinoujscie-h`) — poprzedni slug zwracał dane ogólnopolskie zamiast lokalnych
- `Uncaught SyntaxError: Identifier 'avg' has already been declared` w dashboardzie — podwójna deklaracja w `buildStats()`

---

## [1.2.0] — 2026-03-08

### Dodano
- Obsługa trzech miast: Łódź, Poznań, Świnoujście
- Endpoint `GET /api/cities` — lista dostępnych miast z flagą `available`
- Parametr `?city=` w `GET /api/data`
- Backend API w `api.py` (FastAPI + Uvicorn, port 8001)
- Dashboard SPA (`dashboard.html`): tabela ogłoszeń, filtry, statystyki, test runner
- Przełącznik dark/light mode
- Sortowanie kolumn w tabeli ogłoszeń
- Paginacja tabeli (25/50/100/200 wierszy)
- Skill Claude Code z dokumentacją projektową

### Zmieniono
- `GET /api/data` przyjmuje parametr `?city=` zamiast stałej ścieżki do CSV

---

## [1.1.0] — 2026-03-08

### Dodano
- Deduplikacja rekordów po `id` w `scraper.py` — funkcja `deduplikuj()`
- Raport liczby usuniętych duplikatów w output scrapera
- Raport testów `test_description.md` (42 testy, format `## nazwa / ### opis / Wynik`)

### Naprawiono
- Adresowo.pl duplikuje promowane ogłoszenia na każdej stronie paginacji — Poznań tracił 202/448 rekordów, Świnoujście 234/322

---

## [1.0.0] — 2026-03-08

### Dodano
- Parser HTML `parser.py` — selektory dla struktury Tailwind adresowo.pl (`div[data-offer-card]`)
- Scraper CLI `scraper.py` z parametrami `--city`, `--pages`, `--output`
- 42 testy jednostkowe w `test_parser.py`
  - Fixtures z `scope="module"` — parsowanie HTML raz dla całego modułu
  - `@pytest.mark.parametrize` dla funkcji pomocniczych
  - 7 klas testów: liczba rekordów, pola ogłoszeń, edge cases, funkcje pomocnicze
- `sample_page.html` — fixture z 4 ogłoszeniami (3 kompletne + 1 edge case)
- Zapis CSV z kodowaniem `utf-8-sig` (BOM dla Excela)
- Paginacja: strona 1 → `/mieszkania/{miasto}/`, kolejne → `/_l{nr}`

### Zmieniono
- Przepisanie parsera względem poprzedniej wersji (`scaper.py`): zwrot `dict` zamiast `list`, filtrowanie `None` na wejściu, wyliczana `price_per_m2_zl`
- Selektory CSS zaktualizowane z BEM (`section.search-results__item`) na Tailwind (`div[data-offer-card]`) po zmianie frontendu adresowo.pl
