# Instrukcja GymManager

## Uruchomienie programu

1. Zainstaluj Python 3.
2. Otwórz terminal w folderze projektu.
3. Uruchom `python app.py`.
4. Wybierz **Zaloguj się** lub **Zarejestruj się**. Jeśli nie masz konta, zarejestruj login i hasło, a następnie się zaloguj.
5. Możesz też wybrać **Wejdź jako administrator (bez logowania)**, aby otworzyć wszystkie funkcje aplikacji bez podawania danych konta.

Program zapisuje dane w pliku `gymmanager.db` w folderze projektu. Zachowaj ten plik, aby nie stracić danych.

## Logowanie i wylogowanie

Przy logowaniu i rejestracji login oraz hasło są wymagane. Przy pustych polach lub niepoprawnych danych program wyświetla komunikat i pozostaje na formularzu. Rejestracja umożliwia dodawanie kolejnych kont; każdy login musi być unikalny.

Przycisk **Wyloguj** zamyka widok główny i wraca do logowania. Konto pozostaje dostępne po ponownym uruchomieniu programu. Hasło jest zapisywane jako skrót PBKDF2-SHA256 z losową solą, a nie jako zwykły tekst.

## Korzystanie z programu

- **Klienci:** wpisz dane i wybierz Dodaj. Aby zmienić dane, zaznacz klienta w tabeli, popraw pola i wybierz Zapisz edycję. Zaznaczonego klienta można usunąć przyciskiem Usuń.
- **Karnety:** wybierz klienta, rodzaj karnetu i wpisz daty w formacie RRRR-MM-DD.
- **Trenerzy:** dodaj imię i nazwisko oraz specjalizację. ID trenera będzie widoczne w tabeli.
- **Zajęcia:** wpisz nazwę, opcjonalne ID trenera, datę, godzinę i limit miejsc.
- **Zapisy:** wpisz ID klienta i ID zajęć. ID można sprawdzić w tabelach Klienci i Zajęcia.

Daty wpisuj w formacie `2026-10-30`.
