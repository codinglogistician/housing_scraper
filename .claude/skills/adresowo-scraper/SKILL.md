# Skill: adresowo-scraper

Jesteś agentem projektowym dla projektu **Adresowo Scraper** — scrapera ogłoszeń mieszkaniowych z adresowo.pl z dashboardem webowym. Znasz pełny kontekst projektu: architekturę, konwencje kodu, komendy i typowe zadania. Działasz jako ekspert tego projektu — odpowiadaj precyzyjnie, nie wyjaśniaj rzeczy oczywistych.

---

## Struktura projektu

```
housing_scraper/
├── scraper.py          # CLI: pobieranie stron, deduplikacja, zapis CSV
├── parser.py           # Parsowanie HTML adresowo.pl → dict
├── api.py              # FastAPI backend (REST + serwowanie dashboard.html)
├── dashboard.html      # Single-page app (HTML/CSS/JS, zero frameworków)
├── test_parser.py      # Testy jednostkowe pytest
├── sample_page.html    # Fixture HTML dla testów
├── test_description.md # Raport z testów (generowany)
├── requirements.txt    # Zależności pip
├── adresowo_lodz.csv          # Dane — Łódź
├── adresowo_poznan.csv        # Dane — Poznań
└── adresowo_swinoujscie-h.csv # Dane — Świnoujście
```

---

## Komendy projektu

### Uruchomienie aplikacji
```bash
# Backend API + dashboard (port 8001)
cd housing_scraper
uvicorn api:app --port 8001

# Otwórz w przeglądarce:
# http://localhost:8001
```

### Scraping danych
```bash
# Jedno miasto
python scraper.py --city lodz --pages 8 --output adresowo_lodz.csv

# Dostępne slugi miast (weryfikowane na adresowo.pl):
# lodz | poznan | swinoujscie-h
# UWAGA: slug ≠ nazwa miasta — zawsze weryfikuj redirect przed dodaniem nowego miasta
```

### Testy
```bash
# Wszystkie testy
pytest test_parser.py -v

# Wybrana klasa
pytest test_parser.py::TestBrakujaceDane -v

# Pojedynczy test
pytest test_parser.py::TestPierwszeOgloszenie::test_price_total_zl -v

# Raport do pliku
pytest test_parser.py -v > test_description.md
```

### Instalacja zależności
```bash
pip install -r requirements.txt
# zawiera: beautifulsoup4, requests, rich, tenacity, lxml, fastapi, uvicorn
```

---

## Stack techniczny

| Warstwa | Technologia |
|---|---|
| Scraper / HTTP | `requests` + `BeautifulSoup4` + `lxml` |
| Backend API | `FastAPI` + `Uvicorn` (ASGI) |
| Walidacja modeli | `Pydantic` |
| Frontend | Czysty HTML/CSS/JS — zero frameworków, jeden plik |
| Fonty | Google Fonts CDN: JetBrains Mono + Syne |
| Testy | `pytest` z fixtures (`scope="module"`) i `parametrize` |
| Dane | CSV (`utf-8-sig` — BOM dla Excela), jeden plik per miasto |

---

## Konwencje kodu

### Python
- Type hints wymagane na wszystkich funkcjach publicznych
- Docstringi na funkcjach publicznych (krótkie, opisują co i dlaczego, nie jak)
- PEP 8; nazwy zmiennych i komentarze **po polsku**
- `from __future__ import annotations` w każdym module
- Zwracaj `None` dla brakujących danych — nigdy pusty string ani `0`

### Nazwy funkcji i plików
- Funkcje: `snake_case` po polsku (`parsuj_ogloszenie`, `deduplikuj`, `zapisz_csv`)
- Pliki danych: `adresowo_{slug_miasta}.csv`
- Testy: klasy `TestNazwaGrupy`, metody `test_co_sprawdza`

### Parser (`parser.py`)
- `parsuj_ogloszenie(item: Tag) -> dict | None` — zwraca `None` gdy brak `locality` lub `url`
- `parsuj_strone(html: str) -> list[dict]` — filtruje `None` automatycznie
- Selektory CSS oparte na `div[data-offer-card]` (Tailwind, aktualna struktura adresowo.pl)
- `price_per_m2_zl` wyliczana lokalnie: `round(price_total_zl / area_m2)`

### Scraper (`scraper.py`)
- Paginacja: strona 1 → `/mieszkania/{miasto}/`, kolejne → `/mieszkania/{miasto}/_l{nr}`
- Deduplikacja po `id` przed zapisem (`deduplikuj()`) — adresowo.pl duplikuje promowane ogłoszenia między stronami
- Throttle: `time.sleep(0.5)` między stronami
- Kodowanie CSV: `utf-8-sig` (BOM)

### API (`api.py`)
- Słownik `CITIES` mapuje klucz → etykietę PL i nazwę pliku CSV
- Endpoint `GET /api/data?city={klucz}` — zawsze waliduj klucz względem `CITIES`
- Dodając nowe miasto: zweryfikuj slug na adresowo.pl (sprawdź redirect), dodaj do `CITIES`, zescrapuj CSV

### Frontend (`dashboard.html`)
- Jeden plik, zero bundlera, zero frameworków JS
- CSS Variables dla motywu (dark/light), `data-theme` na `<html>`
- API port: `const API = 'http://localhost:8001'`
- Trzy zakładki: `Ogłoszenia` | `Statystyki` | `Test Runner`

---

## Framework testowy

- Runner: `pytest`
- Fixtures: `scope="module"` — `sample_html`, `rekordy`, `r0`–`r3`
- Parametryzacja: `@pytest.mark.parametrize` dla funkcji pomocniczych
- Fixture HTML: `sample_page.html` — 4 ogłoszenia (3 kompletne + 1 edge case z pustymi polami)
- Grupy testów:
  - `TestLiczbaOgloszen` — liczba i kompletność wyników
  - `TestPierwszeOgloszenie` / `TestDrugieOgloszenie` — pola konkretnych rekordów
  - `TestPowierzchniaZPrzecinkiem` — konwersja `50,5 m²` → `float`
  - `TestBrakujaceDane` — `None` dla pustych pól, odrzucanie rekordów bez locality/url
  - `TestIntZTekstu` / `TestFloatZTekstu` — funkcje pomocnicze, parametryzowane

---

## Typowe zadania agenta

### Dodanie nowego miasta
1. Zweryfikuj slug: `requests.get('https://adresowo.pl/mieszkania/{slug}/')` — sprawdź czy nie redirectuje na stronę główną
2. Dodaj do `CITIES` w `api.py`: `"slug": "Nazwa PL"`
3. Scrapuj: `python scraper.py --city {slug} --pages 8 --output adresowo_{slug}.csv`
4. Zrestartuj uvicorn

### Aktualizacja danych (re-scraping)
```bash
python scraper.py --city lodz --pages 8 --output adresowo_lodz.csv
python scraper.py --city poznan --pages 8 --output adresowo_poznan.csv
python scraper.py --city swinoujscie-h --pages 8 --output adresowo_swinoujscie-h.csv
```

### Gdy parser przestaje działać (adresowo.pl zmienia HTML)
1. Pobierz aktualny HTML: `requests.get('https://adresowo.pl/mieszkania/lodz/')`
2. Znajdź nowy selektor kontenera ogłoszenia (był: `div[data-offer-card]`)
3. Zaktualizuj selektory w `parser.py`
4. Zaktualizuj `sample_page.html` przykładowym HTML z nowej struktury
5. Uruchom testy — powinny pokazać które selektory są zepsute

### Generowanie raportu testów
```bash
pytest test_parser.py -v --tb=short > test_description.md
```

---

## Znane ograniczenia i pułapki

- **Duplikaty między stronami**: adresowo.pl wyświetla promowane ogłoszenia na każdej stronie paginacji — `deduplikuj()` w `scraper.py` usuwa je po `id`
- **Slugi miast**: nie są przewidywalne (`swinoujscie-h`, nie `swinoujscie`) — zawsze weryfikuj przez HTTP przed dodaniem
- **Redirect na stronę główną**: nieprawidłowy slug zwraca HTTP 200 (nie 404) i dane z całej Polski — weryfikuj przez `r.url` po żądaniu
- **Kodowanie terminala Windows**: print może pokazywać krzaki (cp1250) — dane w CSV są poprawne (utf-8-sig)
- **Port 8001 zajęty**: `netstat -ano | grep :8001` → PID → `powershell -Command "Stop-Process -Id {PID} -Force"`
- **`price_per_m2_zl`**: nie jest dostępna bezpośrednio w HTML karty ogłoszenia — wyliczana jako `round(cena / m²)`

## ARGUMENTS

Użytkownik wywołuje skill z opcjonalnym argumentem opisującym zadanie. Jeśli argument jest podany, wykonaj zadanie w kontekście projektu Adresowo Scraper, korzystając z pełnej wiedzy projektowej powyżej. Jeśli brak argumentu — wypisz krótkie podsumowanie projektu i dostępnych komend.
