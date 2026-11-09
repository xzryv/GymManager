# Instrukcja GymManager

## Uruchomienie programu

1. Zainstaluj Python 3.
2. Otwórz terminal w folderze projektu.
3. Uruchom `python app.py`.
4. Jeśli baza nie zawiera użytkowników, utwórz pierwsze konto, podając login i hasło.
5. Zaloguj się utworzonym kontem. Główne okno GymManager otworzy się po poprawnym logowaniu.

Program zapisuje dane w pliku `gymmanager.db` w folderze projektu. Zachowaj ten plik, aby nie stracić danych.

## Logowanie i wylogowanie

Login i hasło są wymagane. Przy pustych polach lub niepoprawnych danych program wyświetla komunikat i pozostaje na ekranie logowania.

Przycisk **Wyloguj** zamyka widok główny i wraca do logowania. Konto pozostaje dostępne po ponownym uruchomieniu programu. Hasło jest zapisywane jako skrót PBKDF2-SHA256 z losową solą, a nie jako zwykły tekst.

## Korzystanie z programu

- **Klienci:** wpisz dane i wybierz Dodaj. Aby zmienić dane, zaznacz klienta w tabeli, popraw pola i wybierz Zapisz edycję. Zaznaczonego klienta można usunąć przyciskiem Usuń.
- **Karnety:** wybierz klienta, rodzaj karnetu i wpisz daty w formacie RRRR-MM-DD.
- **Trenerzy:** dodaj imię i nazwisko oraz specjalizację. ID trenera będzie widoczne w tabeli.
- **Zajęcia:** wpisz nazwę, opcjonalne ID trenera, datę, godzinę i limit miejsc.
- **Zapisy:** wpisz ID klienta i ID zajęć. ID można sprawdzić w tabelach Klienci i Zajęcia.

Daty wpisuj w formacie `2026-10-30`.
