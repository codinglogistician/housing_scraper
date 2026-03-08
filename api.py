"""
api.py — FastAPI backend dla dashboardu adresowo.pl

Uruchomienie:
    pip install fastapi uvicorn
    uvicorn api:app --reload --port 8001
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
import threading
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Adresowo Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------

BASE_URL = "https://adresowo.pl"

# Trzy "stałe" miasta wyświetlane zawsze jako szybkie przyciski
CITIES_STATIC = {
    "lodz":          "Łódź",
    "poznan":        "Poznań",
    "swinoujscie-h": "Świnoujście",
}

# Kody wszystkich województw na adresowo.pl
PROVINCE_CODES = [
    "fds", "fkp", "flu", "flb", "fld", "fma", "fmz",
    "fop", "fpk", "fpd", "fpm", "fsl", "fsk", "fwn", "fwp", "fzp",
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

BASE_DIR = Path(__file__).parent
DASHBOARD_PATH = BASE_DIR / "dashboard.html"
TEST_FILE = BASE_DIR / "test_parser.py"

# Cache listy miast — wypełniany przy pierwszym żądaniu /api/cities/all
_lista_miast_cache: list[dict] | None = None
_lista_miast_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Modele
# ---------------------------------------------------------------------------

class RunTestsRequest(BaseModel):
    tests: list[str] = []


class ScrapeRequest(BaseModel):
    city: str
    pages: int = 8


# ---------------------------------------------------------------------------
# Pomocnicze — lista miast z adresowo.pl
# ---------------------------------------------------------------------------

def _wyciagnij_miasta_z_html(html: str) -> list[dict]:
    """
    Z HTML strony prowincji wyciąga linki /mieszkania/{slug}/.
    Zwraca listę {"slug": ..., "name": ...}.
    Wyklucza kody prowincji (f[a-z]{2}).
    """
    soup = BeautifulSoup(html, "lxml")
    wzorzec = re.compile(r"^/mieszkania/([^/]+)/$")
    wzorzec_prowincji = re.compile(r"^f[a-z]{2}$")
    wynik: list[dict] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=wzorzec):
        slug = wzorzec.match(a["href"]).group(1)
        if wzorzec_prowincji.match(slug):
            continue
        if slug in seen:
            continue
        seen.add(slug)
        nazwa = a.get_text(strip=True)
        if nazwa:
            wynik.append({"slug": slug, "name": nazwa})

    return wynik


def _pobierz_liste_miast() -> list[dict]:
    """
    Pobiera pełną listę miast z wszystkich stron województw adresowo.pl.
    Wywoływana jednorazowo; wynik trafia do _lista_miast_cache.
    """
    wszystkie: list[dict] = []
    seen: set[str] = set()

    with requests.Session() as sesja:
        sesja.headers.update(HTTP_HEADERS)
        for kod in PROVINCE_CODES:
            try:
                resp = sesja.get(f"{BASE_URL}/mieszkania/{kod}", timeout=15)
                if not resp.ok:
                    continue
                for miasto in _wyciagnij_miasta_z_html(resp.text):
                    if miasto["slug"] not in seen:
                        seen.add(miasto["slug"])
                        wszystkie.append(miasto)
            except requests.RequestException:
                continue

    return sorted(wszystkie, key=lambda m: m["name"].casefold())


# ---------------------------------------------------------------------------
# Pomocnicze — odczyt CSV
# ---------------------------------------------------------------------------

def _csv_do_listy(slug: str) -> list[dict]:
    """Wczytuje CSV dla danego slugu i zwraca listę rekordów z typami."""
    csv_path = BASE_DIR / f"adresowo_{slug}.csv"
    if not csv_path.exists():
        raise HTTPException(404, f"Brak pliku CSV dla: {slug}. Uruchom scraping.")
    rekordy = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rekordy.append({
                "id":              row["id"],
                "locality":        row["locality"],
                "rooms":           int(row["rooms"]) if row["rooms"] else None,
                "area_m2":         float(row["area_m2"]) if row["area_m2"] else None,
                "price_total_zl":  int(row["price_total_zl"]) if row["price_total_zl"] else None,
                "price_per_m2_zl": int(row["price_per_m2_zl"]) if row["price_per_m2_zl"] else None,
                "url":             row["url"],
            })
    return rekordy


def _slug_z_walidacja(city: str) -> str:
    """Normalizuje i waliduje slug miasta. Rzuca HTTPException przy błędzie."""
    slug = city.strip()
    if not re.match(r"^[a-zA-Z0-9-]+$", slug):
        raise HTTPException(400, f"Nieprawidłowy slug miasta: {city!r}")
    return slug


# ---------------------------------------------------------------------------
# Endpointy
# ---------------------------------------------------------------------------

@app.get("/")
def serve_dashboard():
    if not DASHBOARD_PATH.exists():
        raise HTTPException(404, "dashboard.html nie istnieje")
    return FileResponse(DASHBOARD_PATH, media_type="text/html")


@app.get("/api/cities")
def get_cities():
    """Zwraca trzy stałe miasta z flagą available (czy CSV istnieje)."""
    return [
        {
            "key": key,
            "label": label,
            "available": (BASE_DIR / f"adresowo_{key}.csv").exists(),
        }
        for key, label in CITIES_STATIC.items()
    ]


@app.get("/api/cities/all")
def get_all_cities():
    """
    Zwraca pełną listę miast z adresowo.pl (slug + name).
    Przy pierwszym wywołaniu pobiera dane ze wszystkich stron województw (~16 req).
    Kolejne wywołania zwracają wynik z cache.
    """
    global _lista_miast_cache
    if _lista_miast_cache is None:
        with _lista_miast_lock:
            if _lista_miast_cache is None:
                _lista_miast_cache = _pobierz_liste_miast()
    return _lista_miast_cache


@app.get("/api/data")
def get_data(city: str = "lodz"):
    """
    Zwraca zawartość CSV dla wybranego miasta.
    Działa dla dowolnego slugu (nie tylko trzech stałych).
    """
    slug = _slug_z_walidacja(city)
    rekordy = _csv_do_listy(slug)
    label = CITIES_STATIC.get(slug, slug.replace("-", " ").title())
    return {"city": slug, "label": label, "count": len(rekordy), "data": rekordy}


@app.post("/api/scrape")
def scrape_city(req: ScrapeRequest):
    """
    Scrapuje ogłoszenia dla podanego slugu, deduplikuje, zapisuje CSV.
    Zwraca dane w tym samym formacie co /api/data.
    Może trwać 20–90 sekund w zależności od miasta i liczby stron.
    """
    from scraper import pobierz_dane, zapisz_csv

    slug = _slug_z_walidacja(req.city)
    pages = max(1, min(req.pages, 30))

    try:
        rekordy = pobierz_dane(slug, pages)
    except Exception as e:
        raise HTTPException(502, f"Błąd scrapowania: {e}")

    if not rekordy:
        raise HTTPException(404, f"Brak ogłoszeń dla miasta: {slug!r}. Sprawdź slug.")

    csv_path = BASE_DIR / f"adresowo_{slug}.csv"
    try:
        zapisz_csv(rekordy, str(csv_path))
    except Exception as e:
        raise HTTPException(500, f"Błąd zapisu CSV: {e}")

    # Wczytaj przez standardową ścieżkę — gwarantuje spójność typów
    return get_data(slug)


@app.post("/api/run-tests")
def run_tests(req: RunTestsRequest):
    """Uruchamia pytest i zwraca wyniki per-test."""
    cmd = [
        sys.executable, "-m", "pytest", str(TEST_FILE),
        "-v", "--tb=short", "--no-header",
    ]
    if req.tests:
        cmd += req.tests

    try:
        wynik = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent),
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Timeout podczas wykonywania testów")

    stdout = wynik.stdout
    return {
        "returncode": wynik.returncode,
        "summary": _znajdz_podsumowanie(stdout),
        "tests": _parsuj_wyniki_pytest(stdout),
        "stdout": stdout,
        "stderr": wynik.stderr,
    }


def _parsuj_wyniki_pytest(stdout: str) -> list[dict]:
    wyniki = []
    for linia in stdout.splitlines():
        linia = linia.strip()
        for status in ("PASSED", "FAILED", "ERROR"):
            if f" {status}" in linia:
                node_id = linia.split(f" {status}")[0].strip()
                wyniki.append({"node_id": node_id, "status": status})
                break
    return wyniki


def _znajdz_podsumowanie(stdout: str) -> str:
    for linia in reversed(stdout.splitlines()):
        l = linia.strip()
        if l and ("passed" in l or "failed" in l or "error" in l):
            return l
    return ""
