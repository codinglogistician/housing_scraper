# Changelog — Adresowo Scraper

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/)

---

## [Unreleased]

### Dodano
- **Kalkulator wolności finansowej** — modal z inputem pensji i sliderem oszczędności (10–30%), oblicza lata do zakupu dla zaznaczonego ogłoszenia lub mediany widoku; animowany pasek + humorystyczny komentarz
- **Ranking absurdu** — przycisk w statusbarze; modal z TOP 3 najdroższych i najtańszych ogłoszeń z filteredData, każdy rekord z losowanym żartobliwym komentarzem z puli 10 tekstów
- **Histogram cen** — canvas w zakładce Statystyki; 10 kubełków cenowych, słupki amber, interaktywny tooltip z zakresem i liczbą ogłoszeń; odświeżany przy każdej zmianie filtrów
- **Heatmapa dzielnic** — kolumna Śr. zł/m² w tabeli dzielnic kolorowana gradientem zielony→czerwony w zależności od wartości względem min/max
- **Znajdź podobne** — przycisk `~` przy każdym ogłoszeniu; modal z 5 podobnymi rekordami (ta sama dzielnica LUB ±15% cena i ±15% m²)
- **Porównywarka** — gdy zaznaczono 2–4 checkboxy, pojawia się przycisk `⚖ Porównaj`; modal z tabelą wiersze×kolumny, podświetlenie najlepszej (zielony) i najgorszej (czerwony) wartości w każdym polu
- **Mój budżet** — tryb uproszczony: toggle zwija sidebar do jednego suwaka budżetu max (50k–2M zł), live filtruje dane
- **Widok kartek** — przełącznik ⊞/☰ w statusbarze; CSS grid kart (3/2/1 kolumn) z ceną amber, dzielnicą cyan, linkiem i Przelicz
- **Animowany licznik wyników** — zmiana liczby wyników animowana przez 400ms via requestAnimationFrame (bez animacji gdy Δ<5)
- Eksport danych do JSON, Markdown, XLSX i PDF — przycisk w pasku nad tabelą; eksportuje zaznaczone rekordy (jeśli są) lub wszystkie przefiltrowane; nagłówek raportu zawiera miasto i aktywne filtry
- Checkboxy przy każdym wierszu tabeli — zaznaczenie ≥1 rekordu ogranicza eksport do wybranych pozycji; checkbox w nagłówku zaznacza/odznacza całą bieżącą stronę
- Przelicznik ceny mieszkania — przycisk "Przelicz" obok każdego ogłoszenia otwiera popup z przeliczeniem ceny na kebaby (÷35 zł), hot-dogi Żabka (÷8,50 zł) i piwa Żabka (÷4,65 zł)

### Planowane
- Automatyczne wykrywanie zmiany struktury HTML (ostrzeżenie przy < 10 ogłoszeń/stronę)
- Walidacja slugu przed scrapingiem (sprawdzenie redirect HTTP)
- Obsługa HTTP 429 z exponential backoff
- Więcej miast: Gdańsk, Wrocław, Kraków, Warszawa
- Alert cenowy (powiadomienie przy nowych ogłoszeniach spełniających kryteria)
- Sparkline trendu cen per dzielnica (wymaga cyklicznego scrapingu)
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
