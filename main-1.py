from __future__ import annotations

from equipo import Equipo
from mundo import Mundo
from simulador import Simulador


def read_line(prompt: str, default: str | None = None) -> str:
    try:
        value = input(prompt)
    except EOFError:
        return default or ""
    value = value.strip()
    return value if value else (default or "")


def ask_int(prompt: str, default: int, minimum: int, maximum: int) -> int:
    while True:
        raw = read_line(f"{prompt} (default {default}): ", str(default))
        try:
            value = int(raw)
        except ValueError:
            print("Introduce un número entero válido.")
            continue
        if value < minimum or value > maximum:
            print(f"El valor debe estar entre {minimum} y {maximum}.")
            continue
        return value


def crear_equipo() -> Equipo:
    print("Camino al Campeonato Nacional")
    print("Simulador de temporada de voleibol en un mundo bidimensional.\n")
    print("Introduce los parámetros iniciales del equipo.\n")

    nombre = read_line("Nombre del equipo: ", "Karasuno")
    posicion_x = ask_int("Posición inicial X", 0, 0, 20)
    posicion_y = ask_int("Posición inicial Y", 0, 0, 20)
    resistencia = ask_int("Resistencia inicial", 80, 1, 200)
    moral = ask_int("Moral inicial", 60, 1, 200)
    dinero = ask_int("Dinero inicial", 50, 0, 500)

    return Equipo(
        nombre=nombre,
        posicion_x=posicion_x,
        posicion_y=posicion_y,
        resistencia=resistencia,
        moral=moral,
        dinero=dinero,
    )


def main() -> None:
    while True:
        equipo = crear_equipo()
        mundo = Mundo()
        simulador = Simulador(equipo, mundo)
        simulador.ejecutar()

        repetir = read_line("¿Quieres jugar otra temporada? [s/N]: ", "n").lower()
        if repetir not in {"s", "si", "sí", "y", "yes"}:
            print("Fin del programa.")
            break


if __name__ == "__main__":
    main()
