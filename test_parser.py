"""
test_parser.py — testy jednostkowe parsera ogłoszeń adresowo.pl

Uruchomienie:
    pytest test_parser.py -v
"""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from parser import (
    parsuj_strone,
    parsuj_ogloszenie,
    _int_z_tekstu,
    _float_z_tekstu,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sample_html() -> str:
    """Wczytuje sample_page.html raz dla całego modułu."""
    return Path(__file__).parent.joinpath("sample_page.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def rekordy(sample_html) -> list[dict]:
    """Parsuje sample_page.html i zwraca listę rekordów."""
    return parsuj_strone(sample_html)


@pytest.fixture(scope="module")
def r0(rekordy) -> dict:
    """Pierwsze ogłoszenie: Łódź Śródmieście, ul. Wólczańska, 2 pok., 54 m², 399 000 zł."""
    return rekordy[0]


@pytest.fixture(scope="module")
def r1(rekordy) -> dict:
    """Drugie ogłoszenie: Łódź Śródmieście, ul. Sterlinga, 2 pok., 50 m², 340 000 zł."""
    return rekordy[1]


@pytest.fixture(scope="module")
def r2(rekordy) -> dict:
    """Trzecie ogłoszenie: Łódź Bałuty, 3 pok., 50,5 m² (przecinek w powierzchni)."""
    return rekordy[2]


@pytest.fixture(scope="module")
def r3(rekordy) -> dict:
    """Czwarte ogłoszenie: Łódź Polesie — brakująca cena i powierzchnia (edge case)."""
    return rekordy[3]


# ---------------------------------------------------------------------------
# Pomocnicze HTML snippety dla testów izolowanych
# ---------------------------------------------------------------------------

HTML_BEZ_LOCALITY = (
    '<div data-offer-card="" data-id="0">'
    '<h2><a href="/o/x"><span class="line-clamp-1"></span></a></h2></div>'
)

HTML_BEZ_URL = (
    '<div data-offer-card="" data-id="0">'
    '<h2><span class="line-clamp-1 font-bold">Łódź Test</span></h2></div>'
)


# ---------------------------------------------------------------------------
# 1. Liczba i kompletność ogłoszeń
# ---------------------------------------------------------------------------

class TestLiczbaOgloszen:
    def test_parsuje_cztery_rekordy(self, rekordy):
        """sample_page.html zawiera 4 bloki div[data-offer-card] — parser powinien zwrócić 4 rekordy."""
        assert len(rekordy) == 4

    def test_zadny_rekord_nie_jest_none(self, rekordy):
        """Żaden element listy zwróconej przez parsuj_strone() nie powinien być wartością None."""
        assert all(r is not None for r in rekordy)

    def test_pusty_html_zwraca_pusta_liste(self):
        """Dla strony bez div[data-offer-card] parser powinien zwrócić pustą listę."""
        assert parsuj_strone("<html><body></body></html>") == []


# ---------------------------------------------------------------------------
# 2. Pola pierwszego ogłoszenia
# ---------------------------------------------------------------------------

class TestPierwszeOgloszenie:
    def test_id(self, r0):
        """Atrybut data-id='3939824' powinien trafić do pola 'id' jako string."""
        assert r0["id"] == "3939824"

    def test_locality(self, r0):
        """Pierwszy span.line-clamp-1.font-bold w h2 a zawiera dzielnicę 'Łódź Śródmieście'."""
        assert r0["locality"] == "Łódź Śródmieście"

    def test_rooms(self, r0):
        """Paragraf z jednostką 'pok.' zawiera wartość 2 — parser zwraca int."""
        assert r0["rooms"] == 2

    def test_area_m2(self, r0):
        """Paragraf z jednostką 'm²' zawiera wartość 54 — parser zwraca float 54.0."""
        assert r0["area_m2"] == pytest.approx(54.0)

    def test_price_total_zl(self, r0):
        """Paragraf z jednostką 'zł' zawiera '399 000' — parser zwraca int 399000."""
        assert r0["price_total_zl"] == 399_000

    def test_price_per_m2_wyliczona(self, r0):
        """Cena za m² jest wyliczana: round(399000 / 54) = 7389."""
        assert r0["price_per_m2_zl"] == round(399_000 / 54)

    def test_url_zaczyna_sie_od_base(self, r0):
        """URL ogłoszenia powinien zaczynać się od 'https://adresowo.pl'."""
        assert r0["url"].startswith("https://adresowo.pl")

    def test_url_zawiera_slug_ulicy(self, r0):
        """Slug URL powinien zawierać 'wolczanska' odpowiadające ul. Wólczańskiej."""
        assert "wolczanska" in r0["url"]


# ---------------------------------------------------------------------------
# 3. Pola drugiego ogłoszenia
# ---------------------------------------------------------------------------

class TestDrugieOgloszenie:
    def test_id(self, r1):
        """Atrybut data-id='3966006' powinien trafić do pola 'id' jako string."""
        assert r1["id"] == "3966006"

    def test_locality(self, r1):
        """Drugie ogłoszenie pochodzi z dzielnicy 'Łódź Śródmieście'."""
        assert r1["locality"] == "Łódź Śródmieście"

    def test_rooms(self, r1):
        """Drugie ogłoszenie ma 2 pokoje."""
        assert r1["rooms"] == 2

    def test_area_m2(self, r1):
        """Powierzchnia drugiego ogłoszenia wynosi 50.0 m²."""
        assert r1["area_m2"] == pytest.approx(50.0)

    def test_price_total_zl(self, r1):
        """Cena całkowita drugiego ogłoszenia wynosi 340 000 zł."""
        assert r1["price_total_zl"] == 340_000

    def test_price_per_m2_wyliczona(self, r1):
        """Cena za m² drugiego ogłoszenia: round(340000 / 50) = 6800."""
        assert r1["price_per_m2_zl"] == round(340_000 / 50)


# ---------------------------------------------------------------------------
# 4. Ogłoszenie z przecinkiem w powierzchni
# ---------------------------------------------------------------------------

class TestPowierzchniaZPrzecinkiem:
    def test_locality(self, r2):
        """Trzecie ogłoszenie pochodzi z dzielnicy 'Łódź Bałuty'."""
        assert r2["locality"] == "Łódź Bałuty"

    def test_area_m2_z_przecinkiem(self, r2):
        """Tekst '50,5 m²' powinien być sparsowany jako float 50.5 (przecinek → kropka)."""
        assert r2["area_m2"] == pytest.approx(50.5)

    def test_price_total_zl(self, r2):
        """Cena całkowita trzeciego ogłoszenia wynosi 450 000 zł."""
        assert r2["price_total_zl"] == 450_000

    def test_rooms(self, r2):
        """Trzecie ogłoszenie ma 3 pokoje."""
        assert r2["rooms"] == 3

    def test_price_per_m2_wyliczona(self, r2):
        """Cena za m² trzeciego ogłoszenia: round(450000 / 50.5) = 8911."""
        assert r2["price_per_m2_zl"] == round(450_000 / 50.5)


# ---------------------------------------------------------------------------
# 5. Edge case — ogłoszenie z brakującymi danymi
# ---------------------------------------------------------------------------

class TestBrakujaceDane:
    def test_brakujaca_cena_zwraca_none(self, r3):
        """Pusty span.font-bold przy 'zł' powinien dać price_total_zl = None."""
        assert r3["price_total_zl"] is None

    def test_brakujaca_powierzchnia_zwraca_none(self, r3):
        """Pusty span.font-bold przy 'm²' powinien dać area_m2 = None."""
        assert r3["area_m2"] is None

    def test_price_per_m2_none_gdy_brak_skladnikow(self, r3):
        """Gdy price_total_zl lub area_m2 to None, price_per_m2_zl też powinno być None."""
        assert r3["price_per_m2_zl"] is None

    def test_brak_locality_wyklucza_rekord(self):
        """Ogłoszenie bez tekstu w span.line-clamp-1 powinno zostać odrzucone (None)."""
        soup = BeautifulSoup(HTML_BEZ_LOCALITY, "lxml")
        item = soup.select_one("div[data-offer-card]")
        assert parsuj_ogloszenie(item) is None

    def test_brak_url_wyklucza_rekord(self):
        """Ogłoszenie bez tagu <a> w h2 powinno zostać odrzucone (None)."""
        soup = BeautifulSoup(HTML_BEZ_URL, "lxml")
        item = soup.select_one("div[data-offer-card]")
        assert parsuj_ogloszenie(item) is None


# ---------------------------------------------------------------------------
# 6. Funkcje pomocnicze — parametryzowane
# ---------------------------------------------------------------------------

class TestIntZTekstu:
    @pytest.mark.parametrize("wejscie,oczekiwane", [
        ("399 000",    399_000),
        ("399\xa0000", 399_000),
        ("1000",       1_000),
        ("0",          0),
    ])
    def test_poprawne_wartosci(self, wejscie, oczekiwane):
        """_int_z_tekstu() powinien poprawnie przetworzyć liczbę ze spacjami i nbsp."""
        assert _int_z_tekstu(wejscie) == oczekiwane

    @pytest.mark.parametrize("wejscie", ["", "brak", "abc", "12.5"])
    def test_niepoprawne_lub_puste_zwracaja_none(self, wejscie):
        """_int_z_tekstu() dla pustego stringa lub tekstu nienumerycznego zwraca None."""
        assert _int_z_tekstu(wejscie) is None


class TestFloatZTekstu:
    @pytest.mark.parametrize("wejscie,oczekiwane", [
        ("50,5",  50.5),
        ("80",    80.0),
        ("100,0", 100.0),
        ("0",     0.0),
    ])
    def test_poprawne_wartosci(self, wejscie, oczekiwane):
        """_float_z_tekstu() powinien zamieniać przecinek na kropkę i zwracać float."""
        assert _float_z_tekstu(wejscie) == pytest.approx(oczekiwane)

    @pytest.mark.parametrize("wejscie", ["", "brak", "abc"])
    def test_niepoprawne_lub_puste_zwracaja_none(self, wejscie):
        """_float_z_tekstu() dla pustego stringa lub tekstu nienumerycznego zwraca None."""
        assert _float_z_tekstu(wejscie) is None
