# TASKS — Adresowo Scraper

Rejestr zadań projektowych. Status: `[ ]` otwarte · `[x]` ukończone · `[~]` w toku · `[!]` zablokowane.

---

## Ukończone

- [x] Implementacja parsera HTML (`parser.py`) — selektory dla struktury Tailwind adresowo.pl
- [x] Implementacja scrapera CLI (`scraper.py`) — paginacja, throttle, zapis CSV
- [x] Deduplikacja rekordów po `id` przed zapisem do CSV
- [x] Backend FastAPI (`api.py`) — endpointy `/api/cities`, `/api/data`, `/api/run-tests`
- [x] Dashboard SPA (`dashboard.html`) — tabela, filtry, statystyki, test runner
- [x] Przełącznik dark/light mode
- [x] Selektor miasta w topbarze dashboardu
- [x] Sortowanie kolumn w tabeli ogłoszeń
- [x] Sortowanie kolumn w tabeli statystyk dzielnic
- [x] 42 testy jednostkowe z fixtures i parametryzacją
- [x] Raport testów (`test_description.md`)
- [x] Scraping Łódź, Poznań, Świnoujście
- [x] Naprawa slugu Świnoujścia (`swinoujscie` → `swinoujscie-h`)
- [x] Skill Claude Code (`adresowo-scraper`) z pełnym kontekstem projektowym
- [x] Eksport danych do JSON, Markdown, XLSX i PDF z checkboxami do selekcji rekordów
- [x] Kalkulator wolności finansowej (modal, slider oszczędności, animowany pasek, komentarz)
- [x] Ranking absurdu (TOP 3 najdroższe / najtańsze z losowanymi komentarzami)
- [x] Histogram cen (canvas, 10 kubełków, tooltip, odświeżany przy filtrach)
- [x] Heatmapa dzielnic (gradient zielony→czerwony na kolumnie zł/m² w tabeli dzielnic)
- [x] Znajdź podobne (modal z 5 podobnymi ogłoszeniami, kryterium dzielnica LUB ±15%)
- [x] Porównywarka (modal side-by-side dla 2–4 zaznaczonych, podświetlenie best/worst)
- [x] Mój budżet (tryb uproszczony z jednym suwakiem, zwija sidebar)
- [x] Widok kartek (toggle tabela/karty, CSS grid 3/2/1 kolumn)
- [x] Animowany licznik wyników (requestAnimationFrame, 400ms)

---

## Otwarte

### Wysoki priorytet

- [ ] **Automatyczne wykrywanie zmiany struktury HTML** — parser powinien logować ostrzeżenie gdy liczba sparsowanych ogłoszeń jest podejrzanie niska (< 10 na stronę)
- [ ] **Walidacja slugu przed scrapingiem** — sprawdzenie redirect przed uruchomieniem pętli stron
- [ ] **Obsługa błędu HTTP 429** (rate limiting) — exponential backoff w scraper.py

### Średni priorytet

- [ ] **Więcej miast** — Gdańsk, Wrocław, Kraków, Warszawa (weryfikacja slugów wymagana)
- [x] ~~Wykres cen w dashboardzie~~ → zrealizowano jako histogram cen (canvas, 10 kubełków)
- [x] ~~Eksport filtrowanych danych z dashboardu do CSV~~ → zrealizowano jako JSON/MD/XLSX/PDF
- [ ] **Porównanie miast** w zakładce Statystyki — zestawienie avg cena/m² per miasto
- [ ] **Automatyczny re-scraping** — GitHub Actions workflow uruchamiający scraper co tydzień
- [ ] **Cache po stronie API** — unikanie wielokrotnego czytania CSV przy każdym żądaniu

### Niski priorytet

- [ ] **Tryb `--all-cities`** w scraper.py — scrapowanie wszystkich skonfigurowanych miast jednym poleceniem
- [ ] **Strona szczegółów ogłoszenia** — scraping strony `adresowo.pl/o/{slug}` po kliknięciu w dashboardzie
- [x] ~~Eksport do Excel (.xlsx)~~ → zrealizowano w pakiecie eksportu (SheetJS)
- [ ] **Testy integracyjne API** — pytest dla endpointów FastAPI (httpx + pytest-asyncio)
- [ ] **Docker Compose** — konteneryzacja API + volume na dane CSV

---

## Znane problemy

- **Świnoujście — mała liczba rekordów**: 88 unikalnych ogłoszeń po deduplikacji. Adresowo.pl ma ograniczoną ofertę dla tego miasta — nie jest to błąd scrapera.
- **Brak `price_per_m2_zl` w HTML**: karta ogłoszenia na stronie listingowej nie eksponuje ceny za m² — jest wyliczana lokalnie, co przy zaokrągleniu może różnić się o 1 zł od wartości na stronie szczegółów.
- **Kodowanie terminala Windows**: print w bash pokazuje krzaki (cp1250) — dane w CSV są poprawne.
