"""
api.py — FastAPI backend dla dashboardu adresowo.pl

Uruchomienie:
    pip install fastapi uvicorn
    uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Adresowo Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CITIES = {
    "lodz":          "Łódź",
    "poznan":        "Poznań",
    "swinoujscie-h": "Świnoujście",
}
BASE_DIR = Path(__file__).parent
DASHBOARD_PATH = BASE_DIR / "dashboard.html"
TEST_FILE = BASE_DIR / "test_parser.py"


# ---------------------------------------------------------------------------
# Modele
# ---------------------------------------------------------------------------

class RunTestsRequest(BaseModel):
    tests: list[str] = []  # pusta lista = uruchom wszystkie


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
    """Zwraca listę dostępnych miast."""
    return [
        {"key": key, "label": label, "available": (BASE_DIR / f"adresowo_{key}.csv").exists()}
        for key, label in CITIES.items()
    ]


@app.get("/api/data")
def get_data(city: str = "lodz"):
    """Zwraca zawartość CSV dla wybranego miasta."""
    if city not in CITIES:
        raise HTTPException(400, f"Nieznane miasto: {city}. Dostępne: {list(CITIES.keys())}")
    csv_path = BASE_DIR / f"adresowo_{city}.csv"
    if not csv_path.exists():
        raise HTTPException(404, f"Brak pliku CSV dla miasta: {city}")

    rekordy = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rekordy.append({
                "id": row["id"],
                "locality": row["locality"],
                "rooms": int(row["rooms"]) if row["rooms"] else None,
                "area_m2": float(row["area_m2"]) if row["area_m2"] else None,
                "price_total_zl": int(row["price_total_zl"]) if row["price_total_zl"] else None,
                "price_per_m2_zl": int(row["price_per_m2_zl"]) if row["price_per_m2_zl"] else None,
                "url": row["url"],
            })
    return {"city": city, "label": CITIES[city], "count": len(rekordy), "data": rekordy}


@app.post("/api/run-tests")
def run_tests(req: RunTestsRequest):
    """
    Uruchamia pytest i zwraca wyniki per-test.
    req.tests: lista node_id testów do uruchomienia (pusta = wszystkie).
    """
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
    wyniki_testow = _parsuj_wyniki_pytest(stdout)
    linia_podsumowania = _znajdz_podsumowanie(stdout)

    return {
        "returncode": wynik.returncode,
        "summary": linia_podsumowania,
        "tests": wyniki_testow,
        "stdout": stdout,
        "stderr": wynik.stderr,
    }


def _parsuj_wyniki_pytest(stdout: str) -> list[dict]:
    """Parsuje linie PASSED/FAILED/ERROR z outputu pytest -v."""
    wyniki = []
    for linia in stdout.splitlines():
        linia = linia.strip()
        for status in ("PASSED", "FAILED", "ERROR"):
            if f" {status}" in linia:
                # Format: "test_parser.py::Klasa::metoda PASSED [ X%]"
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
