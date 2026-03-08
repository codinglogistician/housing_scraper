"""
scraper.py — pobieranie ogłoszeń mieszkań z adresowo.pl i zapis do CSV

Użycie:
    python scraper.py
    python scraper.py --city warszawa --pages 3 --output wyniki.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import time

import requests

from parser import parsuj_strone

BASE_URL = 'https://adresowo.pl'

CSV_HEADERS = [
    'id',
    'url',
    'locality',
    'rooms',
    'area_m2',
    'price_total_zl',
    'price_per_m2_zl',
]

HTTP_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}


def url_strony(miasto: str, nr: int) -> str:
    """Strona 1: /mieszkania/{miasto}/, kolejne: /mieszkania/{miasto}/_l{nr}."""
    if nr == 1:
        return f'{BASE_URL}/mieszkania/{miasto}/'
    return f'{BASE_URL}/mieszkania/{miasto}/_l{nr}'


def pobierz_strone(sesja: requests.Session, miasto: str, nr_strony: int) -> str | None:
    """
    Pobiera HTML jednej strony wyników.
    Zwraca treść HTML lub None przy błędzie sieciowym.
    """
    url = url_strony(miasto, nr_strony)
    try:
        odpowiedz = sesja.get(url, timeout=15)
        odpowiedz.raise_for_status()
        return odpowiedz.text
    except requests.RequestException as e:
        print(f'[BŁĄD] Strona {nr_strony} ({url}): {e}')
        return None


def deduplikuj(rekordy: list[dict]) -> list[dict]:
    """Usuwa rekordy z powtarzającym się id, zachowując pierwsze wystąpienie."""
    seen: set[str] = set()
    wynik = []
    for r in rekordy:
        rid = r.get('id')
        if rid and rid in seen:
            continue
        if rid:
            seen.add(rid)
        wynik.append(r)
    return wynik


def zapisz_csv(rekordy: list[dict], sciezka: str) -> None:
    """
    Zapisuje listę rekordów do pliku CSV.
    Kodowanie utf-8-sig zapewnia poprawny odczyt polskich znaków w Excelu.
    """
    katalog = os.path.dirname(sciezka)
    if katalog:
        os.makedirs(katalog, exist_ok=True)

    with open(sciezka, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rekordy)


def uruchom(miasto: str, strony: int, plik_wyjsciowy: str) -> None:
    """Główna logika: pobieranie, parsowanie, zapis."""
    print(f'Scrapuję: {miasto}, stron: {strony}')
    wszystkie: list[dict] = []

    with requests.Session() as sesja:
        sesja.headers.update(HTTP_HEADERS)
        for nr in range(1, strony + 1):
            print(f'  Strona {nr}/{strony}...', end=' ', flush=True)
            html = pobierz_strone(sesja, miasto, nr)
            if html is None:
                print('pominięta')
                continue
            rekordy = parsuj_strone(html)
            print(f'{len(rekordy)} ogłoszeń')
            wszystkie.extend(rekordy)
            if nr < strony:
                time.sleep(0.5)

    if wszystkie:
        unikalne = deduplikuj(wszystkie)
        zapisz_csv(unikalne, plik_wyjsciowy)
        usuniete = len(wszystkie) - len(unikalne)
        print(f'\nZapisano {len(unikalne)} rekordow -> {plik_wyjsciowy}', end='')
        if usuniete:
            print(f'  (usunieto {usuniete} duplikatow)', end='')
        print()
    else:
        print('\nNie zebrano żadnych danych.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraper adresowo.pl')
    parser.add_argument('--city', default='lodz', help='Miasto (domyślnie: lodz)')
    parser.add_argument('--pages', type=int, default=8, help='Liczba stron (domyślnie: 8)')
    parser.add_argument('--output', default=None, help='Plik wyjściowy CSV')
    args = parser.parse_args()

    plik = args.output or f'adresowo_{args.city}.csv'
    uruchom(args.city, args.pages, plik)
