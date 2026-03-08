"""
parser.py — parsowanie ogłoszeń mieszkań z adresowo.pl

Wyciągane pola:
    id              – identyfikator ogłoszenia (atrybut data-id)
    url             – pełny link do ogłoszenia
    locality        – dzielnica / lokalizacja
    rooms           – liczba pokoi (int | None)
    area_m2         – powierzchnia w m² (float | None)
    price_total_zl  – cena całkowita w zł (int | None)
    price_per_m2_zl – cena za m² w zł (int | None, wyliczana jeśli brak)
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

BASE_URL = 'https://adresowo.pl'


def _int_z_tekstu(tekst: str) -> int | None:
    """'399 000' / '399\xa0000' → 399000. Zwraca None dla pustego lub błędnego."""
    oczyszczony = tekst.replace('\xa0', '').replace(' ', '').strip()
    try:
        return int(oczyszczony) if oczyszczony else None
    except ValueError:
        return None


def _float_z_tekstu(tekst: str) -> float | None:
    """'50,5' / '54' → 50.5 / 54.0. Zwraca None dla pustego lub błędnego."""
    oczyszczony = tekst.replace(',', '.').strip()
    try:
        return float(oczyszczony) if oczyszczony else None
    except ValueError:
        return None


def _wartosc_przed_jednostka(item: Tag, jednostka: str) -> str:
    """
    W kontenerze `item` szuka paragrafu z jednostką (np. 'zł', 'm²', 'pok.')
    i zwraca tekst z poprzedzającego go <span class="font-bold">.
    """
    for p in item.select('p.flex-auto'):
        jednostki = p.find_all('span')
        for span in jednostki:
            if jednostka in span.get_text():
                bold = p.select_one('span.font-bold')
                return bold.get_text(strip=True) if bold else ''
    return ''


def parsuj_ogloszenie(item: Tag) -> dict | None:
    """
    Parsuje pojedynczy div[data-offer-card].
    Zwraca dict lub None, jeśli brakuje locality albo url.
    """
    # --- ID ---
    listing_id = item.get('data-id') or None

    # --- URL ---
    link_tag = item.select_one('h2 a[href]')
    url = BASE_URL + link_tag['href'] if link_tag else ''

    # --- Lokalizacja i ulica ---
    spans = item.select('h2 a span.line-clamp-1') if link_tag else []
    locality = spans[0].get_text(strip=True) if len(spans) > 0 else ''
    # street = spans[1].get_text(strip=True) if len(spans) > 1 else ''

    if not locality or not url:
        return None

    # --- Cena całkowita ---
    cena_raw = _wartosc_przed_jednostka(item, 'zł')
    price_total_zl = _int_z_tekstu(cena_raw)

    # --- Powierzchnia ---
    area_raw = _wartosc_przed_jednostka(item, 'm²')
    area_m2 = _float_z_tekstu(area_raw)

    # --- Liczba pokoi ---
    rooms_raw = _wartosc_przed_jednostka(item, 'pok.')
    rooms: int | None
    try:
        rooms = int(rooms_raw) if rooms_raw else None
    except ValueError:
        rooms = None

    # --- Cena za m² – wyliczana jeśli oba składniki dostępne ---
    price_per_m2_zl: int | None = None
    if price_total_zl is not None and area_m2 and area_m2 > 0:
        price_per_m2_zl = round(price_total_zl / area_m2)

    return {
        'id': listing_id,
        'url': url,
        'locality': locality,
        'rooms': rooms,
        'area_m2': area_m2,
        'price_total_zl': price_total_zl,
        'price_per_m2_zl': price_per_m2_zl,
    }


def parsuj_strone(html: str) -> list[dict]:
    """
    Parsuje pełny HTML strony. Zwraca listę słowników ogłoszeń.
    Pomija rekordy zwracające None (brak locality lub url).
    """
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('div[data-offer-card]')
    wyniki = []
    for item in items:
        rekord = parsuj_ogloszenie(item)
        if rekord is not None:
            wyniki.append(rekord)
    return wyniki
