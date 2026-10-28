# GymManager

GymManager to prosta aplikacja webowa do zarządzania siłownią.

## Funkcje
- dodawanie, edycja i usuwanie klientów
- dodawanie karnetów i sprawdzanie ich statusu
- dodawanie trenerów
- tworzenie zajęć grupowych
- zapisywanie klientów na zajęcia
- sprawdzanie limitu miejsc
- lista zapisów
- panel główny z podstawowymi danymi

## Technologie
- Python
- Flask
- SQLite
- HTML
- CSS

## Uruchomienie w Windows
1. Otwórz terminal w folderze projektu.
2. Wpisz `python -m venv .venv`.
3. Aktywuj środowisko: `.venv\\Scripts\\activate`.
4. Zainstaluj Flask: `python -m pip install -r requirements.txt`.
5. Uruchom aplikację: `python app.py`.
6. Otwórz w przeglądarce `http://127.0.0.1:5001`.

## Podział pracy
- Osoba 1: klienci i karnety.
- Osoba 2: trenerzy, zajęcia i zapisy.
- Osoba 3: wygląd aplikacji, integracja, testowanie i dokumentacja.

Szczegóły podziału znajdują się w pliku `PODZIAL_PRACY.md`.

Projekt edukacyjny.
