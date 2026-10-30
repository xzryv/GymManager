# Instrukcja GymManager

## Uruchomienie programu

1. Zainstaluj Python 3.
2. Otwórz terminal w folderze projektu.
3. Uruchom `python app.py`.
4. Poczekaj na otwarcie okna GymManager.

Program zapisuje dane w pliku `gymmanager.db` w folderze projektu. Zachowaj ten plik, aby nie stracić danych.

## Korzystanie z programu

- **Klienci:** wpisz dane i wybierz Dodaj. Aby zmienić dane, zaznacz klienta w tabeli, popraw pola i wybierz Zapisz edycję. Zaznaczonego klienta można usunąć przyciskiem Usuń.
- **Karnety:** wybierz klienta, rodzaj karnetu i wpisz daty w formacie RRRR-MM-DD.
- **Trenerzy:** dodaj imię i nazwisko oraz specjalizację. ID trenera będzie widoczne w tabeli.
- **Zajęcia:** wpisz nazwę, opcjonalne ID trenera, datę, godzinę i limit miejsc.
- **Zapisy:** wpisz ID klienta i ID zajęć. ID można sprawdzić w tabelach Klienci i Zajęcia.

Daty wpisuj w formacie `2026-10-30`.
