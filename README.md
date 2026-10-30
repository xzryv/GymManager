# GymManager

GymManager to prosty program desktopowy do obsługi siłowni. Dane są zapisywane w bazie SQLite na komputerze użytkownika.

## Funkcje

- obsługa klientów: dodawanie, edycja, lista i usuwanie
- dodawanie karnetów i sprawdzanie ich statusu
- dodawanie trenerów
- tworzenie zajęć z trenerem, datą i limitem miejsc
- zapisywanie klientów na zajęcia z kontrolą wolnych miejsc
- lista zapisów

## Technologie

- Python
- Tkinter do okna programu
- SQLite do bazy danych
- GitHub do wspólnej pracy

Tkinter i SQLite są częścią standardowej biblioteki Pythona. Program nie wymaga dodatkowych pakietów.

## Uruchomienie

1. Zainstaluj Python 3.
2. Otwórz terminal w folderze GymManager.
3. Wpisz `python app.py`.

Przy pierwszym uruchomieniu program utworzy plik `gymmanager.db`.

## Praca zespołowa

Projekt jest prowadzony w Agile. Zadania są opisane jako User Stories, wybierane do krótkich sprintów i śledzone na tablicy Kanban w GitHub Projects. Szczegóły znajdują się w `AGILE_SCRUM_KANBAN.md`.
