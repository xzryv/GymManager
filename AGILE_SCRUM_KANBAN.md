# Agile, Scrum i Kanban w GymManager

## Cel produktu

Prosty program desktopowy, który pomaga pracownikowi siłowni obsługiwać klientów, karnety, trenerów, zajęcia i zapisy.

## Agile

Zespół tworzy program małymi częściami. Po każdej części pokazuje działającą funkcję, zbiera uwagi i wybiera kolejne zadania. Kod jest przechowywany w GitHubie, a zmiany trafiają do głównej gałęzi przez Pull Request.

## Backlog produktu

| ID | User Story | Priorytet |
|---|---|---|
| US-01 | Jako pracownik chcę dodawać, przeglądać, edytować i usuwać klientów. | Wysoki |
| US-02 | Jako pracownik chcę dodawać karnety i sprawdzać ich status. | Wysoki |
| US-03 | Jako pracownik chcę zapisywać trenerów i ich specjalizacje. | Średni |
| US-04 | Jako pracownik chcę planować zajęcia i ustawiać limit miejsc. | Średni |
| US-05 | Jako pracownik chcę zapisywać klientów na zajęcia i kontrolować liczbę miejsc. | Średni |
| US-06 | Jako pracownik chcę uruchamiać program w oknie na komputerze i przechowywać dane lokalnie. | Wysoki |

## Scrum

- **Product Owner i lider projektu:** Osoba 1 ustala priorytety, utrzymuje backlog i koordynuje cały projekt.
- **Scrum Master:** Osoba 3 prowadzi krótkie spotkania i pomaga zespołowi usuwać problemy.
- **Zespół:** Osoba 1 prowadzi projekt i realizuje klientów oraz karnety, Osoba 2 tworzy trenerów, zajęcia i zapisy, Osoba 3 rozwija interfejs, integrację i dokumentację.
- **Sprint:** tydzień pracy nad wybranym celem.
- **Planowanie sprintu:** zespół wybiera zadania z backlogu i dzieli je na mniejsze części.
- **Daily Scrum:** krótkie spotkanie, na którym każdy mówi, co zrobił, co zrobi dalej i czy ma problem.
- **Sprint Review:** pokaz ukończonych funkcji.
- **Retrospektywa:** rozmowa o tym, co poprawić w kolejnym sprincie.

Szczegółowy branch, commity i Pull Request dla części 1 opisuje `CZESC_1_OSOBA_1.md`. Osoba 1 sprawdza i koordynuje łączenie PR-ów do main po ich przeglądzie.

## Przykładowy plan sprintów

| Sprint | Cel |
|---|---|
| 1 | Okno desktopowe, baza SQLite i obsługa klientów |
| 2 | Karnety i trenerzy |
| 3 | Zajęcia i zapisy klientów |
| 4 | Poprawki, sprawdzenie programu i dokumentacja |

## Kanban

Tablica jest prowadzona w GitHub Projects. Każde zadanie ma kartę i przechodzi przez kolumny:

| Backlog | Do zrobienia | W trakcie | Do sprawdzenia | Gotowe |
|---|---|---|---|---|
| Pomysły na później | Zadania wybrane na teraz | Zadania aktualnie wykonywane | Pull Request do sprawdzenia | Działające i zaakceptowane |

Zasady tablicy:

1. Każda osoba wykonuje najwyżej jedno główne zadanie naraz.
2. Zadanie trafia do „Gotowe”, gdy działa i zostało sprawdzone przez inną osobę.
3. Jeśli zadanie utknie, zespół omawia problem na najbliższym krótkim spotkaniu.
4. Nowe pomysły trafiają najpierw do backlogu.

## Definition of Done

Zadanie jest gotowe, gdy jego funkcja działa, dane zapisują się w SQLite, zmiany zostały sprawdzone, a Pull Request jest połączony z główną gałęzią.


