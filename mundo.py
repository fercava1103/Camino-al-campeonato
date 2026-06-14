from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Tuple

from equipo import Equipo


Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class CiudadEspecial:
    nombre: str
    tipo: str
    mensaje: str
    activa_partido: bool = False


class Mundo:
    """Mapa bidimensional, límites y ciudades especiales."""

    limite_min: int = 0
    limite_max: int = 20
    campeonato: Coordinate = (20, 20)

    def __init__(self) -> None:
        self.ciudades_especiales: Dict[Coordinate, CiudadEspecial] = {
            (3, 4): CiudadEspecial(
                "Torneo local de Sano",
                "torneo_local",
                "Sube la intensidad competitiva y otorga puntos por participación.",
                True,
            ),
            (6, 9): CiudadEspecial(
                "Centro de entrenamiento de Kitagawa",
                "centro_entrenamiento",
                "Recupera resistencia con una sesión extra de práctica.",
            ),
            (10, 10): CiudadEspecial(
                "Clínica deportiva de Aoba",
                "clinica_deportiva",
                "Recupera resistencia y moral con tratamiento y descanso.",
            ),
            (13, 7): CiudadEspecial(
                "Patrocinador local de Miyagi",
                "patrocinador_local",
                "Aporta dinero para viajes y alimentación.",
            ),
            (16, 15): CiudadEspecial(
                "Evento de aficionados de Sendai",
                "evento_aficionados",
                "La afición empuja al equipo y mejora su moral.",
                True,
            ),
        }

        self.partidos_automaticos: Dict[Coordinate, str] = {
            (5, 5): "Partido de acceso regional",
            (11, 12): "Partido de semifinal",
            (18, 17): "Partido decisivo de temporada",
        }

    def dentro_de_limites(self, x: int, y: int) -> bool:
        return self.limite_min <= x <= self.limite_max and self.limite_min <= y <= self.limite_max

    def es_campeonato(self, posicion: Coordinate) -> bool:
        return posicion == self.campeonato

    def ciudad_en(self, posicion: Coordinate) -> CiudadEspecial | None:
        return self.ciudades_especiales.get(posicion)

    def partida_en(self, posicion: Coordinate) -> str | None:
        return self.partidos_automaticos.get(posicion)

    def intentar_mover(self, equipo: Equipo, dx: int, dy: int) -> tuple[bool, str]:
        nuevo_x = equipo.posicion_x + dx
        nuevo_y = equipo.posicion_y + dy
        if not self.dentro_de_limites(nuevo_x, nuevo_y):
            return False, "El movimiento se cancela porque el equipo intentó salir del mapa."

        posicion_anterior = equipo.posicion
        equipo.mover(dx, dy)
        return True, f"{posicion_anterior} -> {equipo.posicion}"

    def aplicar_ciudad_especial(self, equipo: Equipo, rng: Random) -> List[str]:
        ciudad = self.ciudad_en(equipo.posicion)
        if ciudad is None:
            return []

        mensajes = [f"Llegan a {ciudad.nombre}: {ciudad.mensaje}"]
        equipo.registrar_ciudad(ciudad.nombre)

        if ciudad.tipo == "torneo_local":
            equipo.modificar_puntos(20)
            equipo.modificar_dinero(20)
            equipo.modificar_moral(5)
            equipo.modificar_resistencia(-8)
            mensajes.append("Torneo local: puntos +20, dinero +20, moral +5, resistencia -8.")
        elif ciudad.tipo == "centro_entrenamiento":
            equipo.modificar_resistencia(18)
            equipo.modificar_moral(4)
            mensajes.append("Centro de entrenamiento: resistencia +18, moral +4.")
        elif ciudad.tipo == "clinica_deportiva":
            equipo.modificar_resistencia(14)
            equipo.modificar_moral(10)
            mensajes.append("Clínica deportiva: resistencia +14, moral +10.")
        elif ciudad.tipo == "patrocinador_local":
            equipo.modificar_dinero(50)
            mensajes.append("Patrocinador local: dinero +50.")
        elif ciudad.tipo == "evento_aficionados":
            equipo.modificar_moral(10)
            equipo.modificar_puntos(10)
            mensajes.append("Evento de aficionados: moral +10, puntos +10.")

        if ciudad.activa_partido:
            mensajes.extend(self.jugar_partido_automatico(equipo, ciudad.nombre, rng))

        return mensajes

    def jugar_partido_automatico(self, equipo: Equipo, contexto: str, rng: Random) -> List[str]:
        base = rng.randint(1, 100)
        potencia = base + equipo.moral // 2 + equipo.resistencia // 3 + equipo.puntos_clasificacion // 25

        mensajes = [f"Partido automático en {contexto}: base={base}, potencia={potencia}."]
        if potencia >= 95:
            equipo.modificar_puntos(35)
            equipo.modificar_dinero(25)
            equipo.modificar_moral(8)
            mensajes.append("Resultado: victoria. Puntos +35, dinero +25, moral +8.")
        else:
            equipo.modificar_moral(-12)
            equipo.modificar_resistencia(-10)
            mensajes.append("Resultado: derrota. Moral -12, resistencia -10.")
        return mensajes
