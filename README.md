# Adresowo Scraper

Scraper ogłoszeń mieszkaniowych z portalu [adresowo.pl](https://adresowo.pl) z dashboardem webowym do eksploracji danych i uruchamiania testów.

## Funkcjonalności

- Scraping ogłoszeń dla wielu miast (Łódź, Poznań, Świnoujście)
- Automatyczna deduplikacja ogłoszeń między stronami paginacji
- Zapis danych do CSV (utf-8-sig, kompatybilny z Excelem)
- REST API (FastAPI) serwujące dane i uruchamiające testy
- Dashboard SPA: tabela z filtrowaniem, sortowaniem i paginacją, statystyki dzielnic, test runner
- Eksport danych do JSON, Markdown, XLSX i PDF (z nagłówkiem raportu zawierającym aktywne filtry)
- Selekcja rekordów checkboxami — eksport obejmuje zaznaczone lub wszystkie przefiltrowane
- Przelicznik ceny mieszkania na kebaby, hot-dogi i piwa (popup przy każdym ogłoszeniu)
- 42 testy jednostkowe parsera HTML

## Struktura projektu

```
housing_scraper/
├── scraper.py               # CLI: pobieranie stron, deduplikacja, zapis CSV
├── parser.py                # Parsowanie HTML adresowo.pl → dict
├── api.py                   # FastAPI backend + serwowanie dashboard.html
├── dashboard.html           # Single-page app (HTML/CSS/JS)
├── test_parser.py           # Testy jednostkowe pytest
├── sample_page.html         # Fixture HTML dla testów
├── requirements.txt         # Zależności pip
├── adresowo_lodz.csv        # Dane — Łódź
├── adresowo_poznan.csv      # Dane — Poznań
└── adresowo_swinoujscie-h.csv  # Dane — Świnoujście
```

## Instalacja

```bash
git clone <repo>
cd housing_scraper
pip install -r requirements.txt
```

## Uruchomienie

### Scraping danych

```bash
python scraper.py --city lodz --pages 8
python scraper.py --city poznan --pages 8 --output adresowo_poznan.csv
python scraper.py --city swinoujscie-h --pages 8
```

### Dashboard

```bash
uvicorn api:app --port 8001
# Otwórz: http://localhost:8001
```

### Testy

```bash
pytest test_parser.py -v
```

## Stack

| Warstwa | Technologia |
|---|---|
| Scraper | `requests`, `BeautifulSoup4`, `lxml` |
| Backend | `FastAPI`, `Uvicorn`, `Pydantic` |
| Frontend | HTML/CSS/JS (bez frameworków), SheetJS (XLSX), jsPDF (PDF) |
| Testy | `pytest` |
| Dane | CSV (`utf-8-sig`) |

## Dostępne miasta

| Miasto | Slug | Rekordy |
|---|---|---|
| Łódź | `lodz` | ~768 |
| Poznań | `poznan` | ~246 |
| Świnoujście | `swinoujscie-h` | ~88 |

> Slugi na adresowo.pl nie są przewidywalne. Przed dodaniem nowego miasta zweryfikuj slug przez HTTP — nieprawidłowy slug zwraca HTTP 200 z danymi ogólnopolskimi zamiast 404.

## Licencja

Do użytku prywatnego i edukacyjnego.
