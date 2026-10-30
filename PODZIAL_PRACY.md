# Podział pracy i role w GymManager

## Główne role

### Osoba 1 — lider projektu i właściciel produktu

Osoba 1 zarządza całym projektem i wykonuje część 1 — klientów i karnety. Do jej zadań należy:

- ustalanie celu i kolejności zadań;
- utrzymywanie backlogu produktu;
- dzielenie pracy między trzy osoby;
- pilnowanie sprintu i tablicy Kanban;
- sprawdzanie postępu i łączenie zaakceptowanych Pull Requestów do `main`;
- przygotowanie końcowej wersji projektu.

### Osoba 2 — programista modułu zajęć

Odpowiada za trenerów, zajęcia i zapisy klientów. Pracuje na branchu `feature/osoba-2-trenerzy-zajecia`.

### Osoba 3 — programista interfejsu i dokumentacji

Odpowiada za poprawki interfejsu desktopowego, integrację, sprawdzenie całości oraz dokumentację. Pracuje na branchu `feature/osoba-3-interfejs-dokumentacja`.

## Część 1 — klienci i karnety

Właściciel: Osoba 1.

- dodawanie, wyświetlanie, edycja i usuwanie klientów;
- walidacja danych klientów;
- dodawanie karnetów do klientów;
- sprawdzanie dat i statusu karnetu.

Szczegółowy opis branchu, commitów i Pull Requesta znajduje się w `CZESC_1_OSOBA_1.md`.

## Wspólne zasady

- Każda osoba pracuje na własnym branchu.
- Zmiany trafiają do `main` przez Pull Request.
- Osoba 1 koordynuje przegląd i integrację, ale każdą zmianę warto sprawdzić z autorem lub innym członkiem zespołu.
- Commity opisują konkretne zmiany.
- Zadania są widoczne na tablicy Kanban i wybierane do sprintu.
