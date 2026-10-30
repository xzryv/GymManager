# GymManager

## O projekcie

GymManager to prosty program desktopowy do obsługi podstawowych spraw w siłowni. Program otwiera się w osobnym oknie, a dane zapisuje lokalnie na komputerze w bazie SQLite.

Projekt powstał jako praca zespołowa i przykład wykorzystania prostych narzędzi do stworzenia działającej aplikacji. Zespół korzysta z podejścia Agile, planuje pracę w sprintach Scrum i śledzi zadania na tablicy Kanban.

## Problem i pomysł

W małej siłowni część informacji może być zapisywana w kilku miejscach, na przykład w zeszycie lub oddzielnych plikach. Utrudnia to sprawdzenie, kto ma karnet, kto prowadzi zajęcia i ile miejsc jest jeszcze dostępnych.

GymManager zbiera te podstawowe informacje w jednym programie. Pracownik może dodać klienta, przypisać mu karnet, zapisać trenera oraz utworzyć zajęcia i zapisy na zajęcia.

## Cel projektu

Celem jest stworzenie łatwego w obsłudze programu dla pracownika siłowni, który:

- porządkuje dane klientów i trenerów;
- ułatwia sprawdzanie karnetów;
- pomaga przygotować listę zajęć;
- kontroluje limit miejsc na zajęciach;
- przechowuje informacje w lokalnej bazie danych;
- działa jako aplikacja desktopowa bez uruchamiania przeglądarki.

## Użytkownicy

Głównym użytkownikiem jest pracownik lub właściciel małej siłowni. Korzysta z programu na komputerze, aby dopisywać i sprawdzać informacje o klientach, karnetach, trenerach, zajęciach i zapisach.

## Zakres funkcji

### Klienci

- dodawanie klienta z imieniem i nazwiskiem, adresem e-mail oraz telefonem;
- wyświetlanie klientów na liście;
- edycja danych wybranego klienta;
- usuwanie klienta.

### Karnety

- przypisanie karnetu do klienta;
- wybór rodzaju karnetu;
- wpisanie daty początku i końca;
- wyświetlenie statusu: zaplanowany, aktywny lub wygasły.

### Trenerzy

- dodawanie trenera;
- zapisanie specjalizacji;
- wyświetlenie listy trenerów i ich identyfikatorów.

### Zajęcia

- utworzenie zajęć z nazwą, datą, godziną i limitem miejsc;
- przypisanie trenera przez jego ID;
- sprawdzenie liczby zapisanych osób.

### Zapisy

- zapisanie klienta na wybrane zajęcia przez ID klienta i ID zajęć;
- sprawdzenie dostępności miejsc;
- wyświetlenie listy zapisów.

## Wymagania

### Wymagania funkcjonalne

1. Program pozwala dodawać, przeglądać, edytować i usuwać klientów.
2. Program pozwala przypisać karnet do istniejącego klienta.
3. Program pokazuje status karnetu na podstawie dat.
4. Program pozwala zapisywać trenerów i tworzyć zajęcia.
5. Program pozwala zapisywać klientów na zajęcia.
6. Program nie pozwala przekroczyć limitu miejsc ani zapisać tej samej osoby dwa razy na te same zajęcia.
7. Dane są przechowywane w bazie SQLite.

### Wymagania pozafunkcjonalne

- interfejs ma być prosty i czytelny;
- program ma działać na komputerze z Pythonem 3;
- program nie wymaga serwera ani połączenia z internetem;
- baza danych znajduje się lokalnie w folderze projektu;
- kod i użyte narzędzia mają być możliwie proste.

## Technologie

- **Python 3** — język, w którym napisano program;
- **Tkinter** — tworzenie okna i elementów interfejsu;
- **SQLite** — lokalna baza danych;
- **Git i GitHub** — zapisywanie zmian i współpraca zespołu;
- **GitHub Projects** — prowadzenie tablicy Kanban.

Tkinter i SQLite są częścią standardowej biblioteki Pythona, więc projekt nie wymaga instalowania dodatkowych pakietów.

## Jak uruchomić

1. Zainstaluj Python 3.
2. Otwórz terminal w folderze projektu.
3. Uruchom polecenie:

   ```bash
   python app.py
   ```

4. Powinno otworzyć się okno GymManager.

Przy pierwszym uruchomieniu program tworzy plik `gymmanager.db`. W tym pliku są przechowywane dane klientów, karnetów, trenerów, zajęć i zapisów. Nie usuwaj go, jeśli chcesz zachować dane. Warto od czasu do czasu zrobić kopię tego pliku.

## Przykładowy sposób pracy

1. Dodaj trenera w zakładce **Trenerzy** i zapamiętaj jego ID.
2. Dodaj zajęcia w zakładce **Zajęcia**. Możesz podać ID trenera.
3. Dodaj klienta w zakładce **Klienci**.
4. Dodaj mu karnet w zakładce **Karnety**.
5. Zapisz go na zajęcia w zakładce **Zapisy**, podając ID klienta i ID zajęć.

ID potrzebne do zapisów są widoczne w tabelach programu.

## Agile, Scrum i Kanban

Zespół rozwija projekt etapami i regularnie pokazuje działające funkcje. Lista pomysłów i wymagań jest backlogiem produktu. Do pracy wybierane są małe zadania, które można wykonać i sprawdzić.

Praca jest planowana w tygodniowych sprintach Scrum. Sprint zaczyna się od wyboru celu i zadań. W trakcie tygodnia zespół krótko omawia postęp. Na koniec pokazuje gotowe funkcje i rozmawia o tym, co poprawić w następnym sprincie.

Tablica Kanban w GitHub Projects może mieć kolumny:

- **Backlog** — pomysły i zadania na przyszłość;
- **Do zrobienia** — zadania wybrane do pracy;
- **W trakcie** — zadania aktualnie wykonywane;
- **Do sprawdzenia** — zadania zgłoszone w Pull Request;
- **Gotowe** — sprawdzone i połączone zmiany.

Szczegółowy backlog, role i przykładowe sprinty opisuje plik `AGILE_SCRUM_KANBAN.md`.

## Podział pracy

- **Osoba 1:** klienci i karnety;
- **Osoba 2:** trenerzy, zajęcia i zapisy;
- **Osoba 3:** interfejs desktopowy, integracja i dokumentacja.

Każda osoba pracuje na osobnym branchu. Zmiany są zapisywane w commitach i zgłaszane przez Pull Request do gałęzi `main`. Szczegóły podziału znajdują się w `PODZIAL_PRACY.md`.

## Ograniczenia i dalszy rozwój

Obecna wersja jest prostym programem do lokalnego użytku. Nie ma logowania użytkowników, synchronizacji między komputerami, płatności ani automatycznych przypomnień. Nie obsługuje też równoczesnej pracy wielu stanowisk na jednej wspólnej bazie.

W kolejnych wersjach można dodać wyszukiwanie, usuwanie lub edycję karnetów i trenerów, wygodniejsze wybieranie trenera i zajęć z listy, raporty oraz kopię zapasową wykonywaną z poziomu programu.

## Pliki projektu

- `app.py` — kod programu desktopowego;
- `gymmanager.db` — baza danych tworzona podczas uruchomienia;
- `Instrukcja.md` — krótkie wskazówki dla użytkownika;
- `PODZIAL_PRACY.md` — odpowiedzialność członków zespołu;
- `AGILE_SCRUM_KANBAN.md` — backlog i opis organizacji pracy;
- `requirements.txt` — lista dodatkowych bibliotek; projekt korzysta ze standardowej biblioteki Pythona.
