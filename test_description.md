# Raport testów jednostkowych — parser ogłoszeń adresowo.pl

Plik testowany: `parser.py` | Plik testów: `test_parser.py`
Środowisko: Python 3.14.3, pytest 9.0.2 | Data: 2026-03-08
Wynik ogólny: **42 / 42 PASSED**

---

## TestLiczbaOgloszen

### test_parsuje_cztery_rekordy

`sample_page.html` zawiera 4 bloki `div[data-offer-card]` — parser powinien zwrócić dokładnie 4 rekordy.

Wynik: PASSED

---

### test_zadny_rekord_nie_jest_none

Żaden element listy zwróconej przez `parsuj_strone()` nie powinien mieć wartości `None`. Sprawdza, że filtrowanie niepełnych ogłoszeń nie usuwa prawidłowych rekordów.

Wynik: PASSED

---

### test_pusty_html_zwraca_pusta_liste

Dla strony HTML bez żadnego `div[data-offer-card]` funkcja `parsuj_strone()` powinna zwrócić pustą listę `[]`.

Wynik: PASSED

---

## TestPierwszeOgloszenie

### test_id

Atrybut `data-id="3939824"` powinien trafić do pola `id` jako string `"3939824"`.

Wynik: PASSED

---

### test_locality

Pierwszy `span.line-clamp-1.font-bold` wewnątrz `h2 a` zawiera dzielnicę `Łódź Śródmieście`.

Wynik: PASSED

---

### test_rooms

Paragraf z jednostką `pok.` zawiera wartość `2` — parser powinien zwrócić `int` 2.

Wynik: PASSED

---

### test_area_m2

Paragraf z jednostką `m²` zawiera wartość `54` — parser powinien zwrócić `float` 54.0.

Wynik: PASSED

---

### test_price_total_zl

Paragraf z jednostką `zł` zawiera tekst `399 000` (ze spacją) — parser powinien zwrócić `int` 399000.

Wynik: PASSED

---

### test_price_per_m2_wyliczona

Cena za m² nie jest dostępna bezpośrednio na karcie ogłoszenia — parser wylicza ją jako `round(price_total_zl / area_m2)`. Dla 399000 / 54 wynik to 7389.

Wynik: PASSED

---

### test_url_zaczyna_sie_od_base

URL ogłoszenia powinien zaczynać się od `https://adresowo.pl` (sklejenie stałej `BASE_URL` ze ścieżką z atrybutu `href`).

Wynik: PASSED

---

### test_url_zawiera_slug_ulicy

Slug URL powinien zawierać `wolczanska` — odpowiednik ul. Wólczańskiej zakodowany w adresie ogłoszenia.

Wynik: PASSED

---

## TestDrugieOgloszenie

### test_id

Atrybut `data-id="3966006"` powinien trafić do pola `id` jako string `"3966006"`.

Wynik: PASSED

---

### test_locality

Drugie ogłoszenie pochodzi z dzielnicy `Łódź Śródmieście`.

Wynik: PASSED

---

### test_rooms

Drugie ogłoszenie ma 2 pokoje — parser zwraca `int` 2.

Wynik: PASSED

---

### test_area_m2

Powierzchnia drugiego ogłoszenia wynosi 50.0 m².

Wynik: PASSED

---

### test_price_total_zl

Cena całkowita drugiego ogłoszenia wynosi 340 000 zł — parser zwraca `int` 340000.

Wynik: PASSED

---

### test_price_per_m2_wyliczona

Cena za m² drugiego ogłoszenia: `round(340000 / 50)` = 6800.

Wynik: PASSED

---

## TestPowierzchniaZPrzecinkiem

### test_locality

Trzecie ogłoszenie pochodzi z dzielnicy `Łódź Bałuty`.

Wynik: PASSED

---

### test_area_m2_z_przecinkiem

Tekst `50,5 m²` (z przecinkiem dziesiętnym) powinien być sparsowany jako `float` 50.5. Funkcja `_float_z_tekstu()` zamienia przecinek na kropkę przed konwersją.

Wynik: PASSED

---

### test_price_total_zl

Cena całkowita trzeciego ogłoszenia wynosi 450 000 zł.

Wynik: PASSED

---

### test_rooms

Trzecie ogłoszenie ma 3 pokoje.

Wynik: PASSED

---

### test_price_per_m2_wyliczona

Cena za m² trzeciego ogłoszenia: `round(450000 / 50.5)` = 8911.

Wynik: PASSED

---

## TestBrakujaceDane

### test_brakujaca_cena_zwraca_none

Ogłoszenie z pustym `span.font-bold` przy jednostce `zł` powinno dać `price_total_zl = None`. Sprawdza, że `_int_z_tekstu("")` zwraca `None`, a nie podnosi wyjątku.

Wynik: PASSED

---

### test_brakujaca_powierzchnia_zwraca_none

Ogłoszenie z pustym `span.font-bold` przy jednostce `m²` powinno dać `area_m2 = None`. Sprawdza, że `_float_z_tekstu("")` zwraca `None`.

Wynik: PASSED

---

### test_price_per_m2_none_gdy_brak_skladnikow

Gdy `price_total_zl` lub `area_m2` to `None`, obliczenie ceny za m² jest niemożliwe — pole `price_per_m2_zl` powinno być `None`.

Wynik: PASSED

---

### test_brak_locality_wyklucza_rekord

Ogłoszenie z pustym `span.line-clamp-1` (brak tekstu dzielnicy) powinno być odrzucone — `parsuj_ogloszenie()` zwraca `None` zamiast niekompletnego rekordu.

Wynik: PASSED

---

### test_brak_url_wyklucza_rekord

Ogłoszenie bez tagu `<a>` wewnątrz `<h2>` powinno być odrzucone — `parsuj_ogloszenie()` zwraca `None`, bo nie można ustalić URL ani ID ogłoszenia.

Wynik: PASSED

---

## TestIntZTekstu

### test_poprawne_wartosci[399 000-399000]

Tekst `"399 000"` (spacja jako separator tysięcy) powinien być sparsowany do `int` 399000.

Wynik: PASSED

---

### test_poprawne_wartosci[399\xa0000-399000]

Tekst `"399\xa0000"` (twarda spacja `&nbsp;` jako separator tysięcy) powinien być sparsowany do `int` 399000. Sprawdza obsługę znaku `\xa0` typowego dla HTML.

Wynik: PASSED

---

### test_poprawne_wartosci[1000-1000]

Tekst `"1000"` bez separatora powinien być sparsowany do `int` 1000.

Wynik: PASSED

---

### test_poprawne_wartosci[0-0]

Tekst `"0"` powinien być sparsowany do `int` 0 (nie do `None`).

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[]

Pusty string `""` powinien zwrócić `None` — brak danych w polu nie jest błędem, lecz wartością oczekiwaną.

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[brak]

Tekst `"brak"` jest nienumeryczny — `_int_z_tekstu()` powinien zwrócić `None`, nie podnosić wyjątku `ValueError`.

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[abc]

Tekst `"abc"` jest nienumeryczny — `_int_z_tekstu()` powinien zwrócić `None`.

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[12.5]

Tekst `"12.5"` zawiera kropkę dziesiętną — `_int_z_tekstu()` nie obsługuje floatów i powinien zwrócić `None`.

Wynik: PASSED

---

## TestFloatZTekstu

### test_poprawne_wartosci[50,5-50.5]

Tekst `"50,5"` (przecinek dziesiętny, format polski) powinien być sparsowany do `float` 50.5.

Wynik: PASSED

---

### test_poprawne_wartosci[80-80.0]

Tekst `"80"` (liczba całkowita) powinien być sparsowany do `float` 80.0.

Wynik: PASSED

---

### test_poprawne_wartosci[100,0-100.0]

Tekst `"100,0"` powinien być sparsowany do `float` 100.0.

Wynik: PASSED

---

### test_poprawne_wartosci[0-0.0]

Tekst `"0"` powinien być sparsowany do `float` 0.0 (nie do `None`).

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[]

Pusty string `""` powinien zwrócić `None`.

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[brak]

Tekst `"brak"` jest nienumeryczny — `_float_z_tekstu()` powinien zwrócić `None`.

Wynik: PASSED

---

### test_niepoprawne_lub_puste_zwracaja_none[abc]

Tekst `"abc"` jest nienumeryczny — `_float_z_tekstu()` powinien zwrócić `None`.

Wynik: PASSED
