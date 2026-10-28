# Podział pracy w projekcie GymManager

Termin oddania: 22 stycznia 2027 r.

## Osoba 1 — klienci i karnety
Issues: US-01 i US-02.

Pliki:
- `app.py` — funkcje klientów i karnetów
- `templates/customers.html`
- `templates/edit_customer.html`
- `templates/memberships.html`

Zadania:
- dodawanie, wyświetlanie, edycja i usuwanie klientów
- sprawdzanie wymaganych danych
- dodawanie karnetów
- sprawdzanie dat i statusu karnetu
- testowanie tych funkcji

## Osoba 2 — trenerzy i zajęcia
Issues: US-03, US-04 i US-05.

Pliki:
- `app.py` — funkcje trenerów, zajęć i zapisów
- `templates/trainers.html`
- `templates/classes.html`
- `templates/bookings.html`

Zadania:
- dodawanie trenerów
- tworzenie zajęć i przypisywanie trenerów
- zapisywanie klientów na zajęcia
- kontrola limitu miejsc
- sprawdzanie listy zapisów

## Osoba 3 — interfejs i integracja
Issues: US-06, US-07 i US-08.

Pliki:
- `templates/base.html`
- `templates/home.html`
- `static/style.css`
- `README.md`
- `PODZIAL_PRACY.md`

Zadania:
- poprawa wyglądu aplikacji
- sprawdzanie połączenia między modułami
- testowanie całego projektu
- aktualizacja dokumentacji

Logowanie, panel klienta i pełne raporty wymagają dalszego rozwinięcia. Nie oznaczamy tych funkcji jako ukończonych, dopóki nie zostaną dodane i przetestowane.

## Zasady GitHub
Każda osoba pracuje na osobnej gałęzi. Zmiany wysyłamy przez Pull Requesty. Commity powinny opisywać faktycznie wykonane zmiany.
