# Część 1 — klienci i karnety

## Właściciel części

Osoba 1 — właściciel GymManager i lider projektu. Odpowiada za zarządzanie całością projektu oraz wykonuje moduł klientów i karnetów.

## Zakres części

- dodawanie, wyświetlanie, edycja i usuwanie klientów;
- sprawdzanie wymaganych danych klienta i unikalności e-maila;
- dodawanie karnetów do istniejących klientów;
- sprawdzanie poprawności dat i statusu karnetu;
- połączenie modułu z desktopowym oknem GymManager.

## Pliki

- `customer_memberships.py` — logika klientów i karnetów;
- `app.py` — podłączenie formularzy desktopowych do modułu.

## Branch

Utwórz branch:

`feature/osoba-1-klienci-karnety`

## Proponowane commity

Rób commit po każdej ukończonej części. W polu Summary wpisuj:

1. `Add customer and membership functions`
2. `Connect customer screens to customer module`
3. `Add validation for customer and membership data`

Jeśli kilka zmian robisz jednocześnie, użyj tylko tych opisów, które odpowiadają faktycznym zmianom. Nie dodawaj pustych commitów.

## Pull Request

- Tytuł: `Część 1: obsługa klientów i karnetów`
- Base: `main`
- Compare: `feature/osoba-1-klienci-karnety`
- Opis: `Dodaje moduł klientów i karnetów, walidację danych oraz podłącza funkcje do interfejsu desktopowego.`

Przed utworzeniem PR sprawdź listę zmienionych plików i upewnij się, że są tam tylko pliki związane z zadaniem oraz dokumentacja, którą zmieniałeś.

## Jak połączyć zmiany

1. Zrób Pull Request z `feature/osoba-1-klienci-karnety` do `main`.
2. Poproś inną osobę o sprawdzenie zmian.
3. Jeśli nie ma uwag i aplikacja uruchamia się poprawnie, wybierz **Merge pull request**.
4. Po połączeniu pobierz aktualne `main` i dopiero wtedy zaczynaj następną pracę.

Jako lider projektu koordynujesz także sprawdzanie pozostałych Pull Requestów. Łączysz do `main` tylko sprawdzone zmiany, po jednym PR naraz. Nie łączysz bezpośrednio branchy członków zespołu między sobą.
