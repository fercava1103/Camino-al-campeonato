from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


Coordinate = Tuple[int, int]


@dataclass
class Equipo:
    """Estado del equipo durante toda la temporada."""

    nombre: str
    posicion_x: int
    posicion_y: int
    resistencia: int
    moral: int
    dinero: int
    puntos_clasificacion: int = 0
    historial: List[str] = field(default_factory=list)
    ciudades_visitadas: List[str] = field(default_factory=list)
    eventos_importantes: List[str] = field(default_factory=list)
    pasos_realizados: int = 0
    turnos_perdidos: int = 0

    @property
    def posicion(self) -> Coordinate:
        return self.posicion_x, self.posicion_y

    def mover(self, dx: int, dy: int) -> None:
        self.posicion_x += dx
        self.posicion_y += dy

    def modificar_resistencia(self, delta: int) -> None:
        self.resistencia = max(0, self.resistencia + delta)

    def modificar_moral(self, delta: int) -> None:
        self.moral = max(0, self.moral + delta)

    def modificar_dinero(self, delta: int) -> None:
        self.dinero = max(0, self.dinero + delta)

    def modificar_puntos(self, delta: int) -> None:
        self.puntos_clasificacion = max(0, self.puntos_clasificacion + delta)

    def registrar_evento(self, mensaje: str) -> None:
        self.historial.append(mensaje)
        self.eventos_importantes.append(mensaje)

    def registrar_ciudad(self, nombre: str) -> None:
        if nombre not in self.ciudades_visitadas:
            self.ciudades_visitadas.append(nombre)

    def mostrar_estado(self) -> None:
        print(f"Equipo: {self.nombre}")
        print(f"Posición: {self.posicion}")
        print(f"Resistencia: {self.resistencia}")
        print(f"Moral: {self.moral}")
        print(f"Dinero: {self.dinero}")
        print(f"Puntos de clasificación: {self.puntos_clasificacion}")
from __future__ import annotations

from random import Random



def aplicar_evento_aleatorio(equipo: Equipo, rng: Random) -> str | None:
    """Genera un evento aleatorio que cambia el estado del equipo."""

    if rng.random() > 0.30:
        return None

    eventos = [
        _lesion,
        _patrocinador,
        _partido_espectacular,
        _viaje_complicado,
        _aficion_motivadora,
    ]
    evento = rng.choice(eventos)
    return evento(equipo)


def _lesion(equipo: Equipo) -> str:
    equipo.modificar_resistencia(-15)
    equipo.modificar_moral(-5)
    mensaje = "Lesión: resistencia -15, moral -5."
    equipo.registrar_evento(mensaje)
    return mensaje


def _patrocinador(equipo: Equipo) -> str:
    equipo.modificar_dinero(50)
    mensaje = "Patrocinador: dinero +50."
    equipo.registrar_evento(mensaje)
    return mensaje


def _partido_espectacular(equipo: Equipo) -> str:
    equipo.modificar_puntos(20)
    equipo.modificar_moral(5)
    mensaje = "Partido espectacular: puntos +20, moral +5."
    equipo.registrar_evento(mensaje)
    return mensaje


def _viaje_complicado(equipo: Equipo) -> str:
    equipo.turnos_perdidos += 1
    equipo.modificar_resistencia(-3)
    mensaje = "Viaje complicado: pierde un turno y resistencia -3."
    equipo.registrar_evento(mensaje)
    return mensaje


def _aficion_motivadora(equipo: Equipo) -> str:
    equipo.modificar_moral(10)
    mensaje = "Afición motivadora: moral +10."
    equipo.registrar_evento(mensaje)
    return mensaje
    from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Dict, List, Tuple


Coordinate = Tuple[int, int]


@dataclass
class ExpeditionConfig:
    name: str
    start: Coordinate
    energy: int
    radius: int
    difficulty: int
    mode: str
    max_steps: int
    goal: Coordinate
    team: str


@dataclass
class ExpeditionState:
    position: Coordinate
    energy: int
    step: int = 0
    visited_sites: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


def read_line(prompt: str, default: str | None = None) -> str:
    try:
        raw = input(prompt)
    except EOFError:
        return default or ""
    raw = raw.strip()
    return raw if raw else (default or "")


def ask_int(
    prompt: str,
    default: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    while True:
        raw = read_line(prompt, str(default) if default is not None else None)
        try:
            value = int(raw)
        except ValueError:
            print("  Valor inválido. Introduce un número entero.")
            continue
        if min_value is not None and value < min_value:
            print(f"  El valor debe ser al menos {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"  El valor debe ser como máximo {max_value}.")
            continue
        return value


def ask_choice(prompt: str, options: Dict[str, str], default_key: str) -> str:
    keys = ", ".join(f"{k}={v}" for k, v in options.items())
    while True:
        raw = read_line(f"{prompt} [{keys}] (default {default_key}): ", default_key).lower()
        if raw in options:
            return raw
        print("  Opción no válida.")


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def generate_world(radius: int, rng: Random, start: Coordinate, goal: Coordinate) -> Dict[Coordinate, str]:
    world: Dict[Coordinate, str] = {}
    blocked = {start, goal}

    def place(kind: str, count: int) -> None:
        attempts = 0
        while count > 0 and attempts < 2000:
            attempts += 1
            coord = (rng.randint(-radius, radius), rng.randint(-radius, radius))
            if coord in blocked or coord in world:
                continue
            world[coord] = kind
            blocked.add(coord)
            count -= 1

    place("recharge_station", 2 + max(1, radius // 4))
    place("rock_field", 3 + max(1, radius // 3))
    place("supply_cache", 2 + max(1, radius // 5))
    return world


def move_toward_goal(state: ExpeditionState, goal: Coordinate, rng: Random) -> Tuple[int, int, str]:
    x, y = state.position
    gx, gy = goal
    dx = gx - x
    dy = gy - y
    if dx == 0 and dy == 0:
        return 0, 0, "mantener posición"

    options: List[Tuple[int, int, str]] = []
    if dx:
        options.append((sign(dx), 0, "este" if dx > 0 else "oeste"))
    if dy:
        options.append((0, sign(dy), "norte" if dy > 0 else "sur"))

    if len(options) == 2 and rng.random() < 0.35:
        chosen = options[1]
    else:
        chosen = options[0]
    return chosen


def manual_move() -> Tuple[int, int, str]:
    options = {
        "n": (0, 1, "norte"),
        "s": (0, -1, "sur"),
        "e": (1, 0, "este"),
        "o": (-1, 0, "oeste"),
        "x": (0, 0, "esperar"),
    }
    while True:
        raw = read_line("  Dirección [n/s/e/o/x]: ", "x").lower()
        if raw in options:
            return options[raw]
        print("  Dirección no válida.")


def random_event(state: ExpeditionState, config: ExpeditionConfig, rng: Random) -> str | None:
    chance = {1: 0.12, 2: 0.20, 3: 0.28}[config.difficulty]
    if rng.random() > chance:
        return None

    roll = rng.random()
    if roll < 0.5:
        loss = 4 + config.difficulty
        state.energy -= loss
        note = f"Tormenta de viento: la energía baja {loss} por el desgaste adicional."
        state.highlights.append(note)
        return note
    if roll < 0.85:
        x, y = state.position
        drift = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        state.position = (
            clamp(x + drift[0], -config.radius, config.radius),
            clamp(y + drift[1], -config.radius, config.radius),
        )
        state.energy -= 2
        note = "Se desacomoda el ritmo: Hinata y Yaichi corrigen la ruta y gastan 2 de energía."
        state.highlights.append(note)
        return note

    gain = 3
    state.energy += gain
    note = f"Momento de coordinación perfecta: se recuperan {gain} puntos de energía."
    state.highlights.append(note)
    return note


def apply_site_effect(
    state: ExpeditionState,
    config: ExpeditionConfig,
    site: str,
    before_position: Coordinate,
) -> str:
    x, y = state.position
    if site == "recharge_station":
        gain = 8 + config.difficulty
        state.energy += gain
        state.visited_sites.append(f"Banco de energía en ({x}, {y})")
        note = f"Banco de energía: energía +{gain}."
        state.highlights.append(note)
        return note
    if site == "rock_field":
        loss = 5 + config.difficulty
        state.energy -= loss
        if state.position != config.goal:
            state.position = (
                clamp(state.position[0] - sign(state.position[0] - before_position[0]), -config.radius, config.radius),
                clamp(state.position[1] - sign(state.position[1] - before_position[1]), -config.radius, config.radius),
            )
        state.visited_sites.append(f"Zona de bloqueo en ({x}, {y})")
        note = f"Zona de bloqueo: energía -{loss} y retroceso por una mala recepción."
        state.highlights.append(note)
        return note
    if site == "supply_cache":
        gain = 5 + config.difficulty
        state.energy += gain
        state.visited_sites.append(f"Puesto de hidratación en ({x}, {y})")
        note = f"Puesto de hidratación: energía +{gain}."
        state.highlights.append(note)
        return note
    return ""


def print_intro(config: ExpeditionConfig, world: Dict[Coordinate, str]) -> None:
    print("\n=== Inicio de la expedición ===")
    print(f"Equipo: {config.team}")
    print(f"Nombre: {config.name}")
    print(f"Posición inicial: {config.start}")
    print(f"Energía inicial: {config.energy}")
    print(f"Límites del mundo: x e y entre {-config.radius} y {config.radius}")
    print(f"Objetivo: llegar a {config.goal}")
    print(f"Modo de control: {'manual' if config.mode == 'manual' else 'automático'}")
    print(f"Límite de pasos: {config.max_steps}")
    print("Condiciones de finalización: llegar al objetivo, quedarse sin energía o superar el límite de pasos.")
    print(f"Elementos del mundo generados: {len(world)} sitios especiales.")
    print("================================\n")


def build_config() -> ExpeditionConfig:
    print("Simulador de expedición en un mundo bidimensional.")
    print("Hinata y Yaichi cruzan una ruta de entrenamiento hacia la meta.\n")

    team = read_line("Nombre del equipo: ", "Hinata y Yaichi")
    name = read_line("Nombre de la expedición: ", "Ruta del salto definitivo")
    radius = ask_int("Radio del mundo (5-20): ", default=8, min_value=5, max_value=20)
    start_x = ask_int(f"Posición inicial X (-{radius} a {radius}): ", default=0, min_value=-radius, max_value=radius)
    start_y = ask_int(f"Posición inicial Y (-{radius} a {radius}): ", default=0, min_value=-radius, max_value=radius)
    energy = ask_int("Energía inicial (10-200): ", default=35, min_value=10, max_value=200)
    difficulty_key = ask_choice("Dificultad", {"1": "fácil", "2": "normal", "3": "difícil"}, "2")
    mode = ask_choice("Modo", {"auto": "automático", "manual": "manual"}, "auto")

    difficulty = int(difficulty_key)
    max_steps = radius * 4 + difficulty * 4
    goal = (radius, radius)

    return ExpeditionConfig(
        name=name,
        start=(start_x, start_y),
        energy=energy,
        radius=radius,
        difficulty=difficulty,
        mode=mode,
        max_steps=max_steps,
        goal=goal,
        team=team,
    )


def simulate_one_run() -> None:
    rng = Random()
    config = build_config()
    world = generate_world(config.radius, rng, config.start, config.goal)
    state = ExpeditionState(position=config.start, energy=config.energy)

    print_intro(config, world)

    if state.position == config.goal:
        print("La expedición empieza ya en el objetivo. Resultado: éxito inmediato.")
        return

    while True:
        state.step += 1
        before_position = state.position
        before_energy = state.energy

        if config.mode == "manual":
            dx, dy, action_label = manual_move()
        else:
            dx, dy, action_label = move_toward_goal(state, config.goal, rng)

        target = (before_position[0] + dx, before_position[1] + dy)
        boundary_hit = False
        if not (-config.radius <= target[0] <= config.radius and -config.radius <= target[1] <= config.radius):
            boundary_hit = True
            target = (
                clamp(target[0], -config.radius, config.radius),
                clamp(target[1], -config.radius, config.radius),
            )

        state.position = target
        state.energy -= 1 + config.difficulty

        event_note = random_event(state, config, rng)
        site = world.get(state.position)
        site_note = apply_site_effect(state, config, site, before_position) if site else ""

        if boundary_hit:
            state.energy -= 2

        print(f"Paso {state.step}")
        print(f"  Acción: {action_label}")
        print(f"  Posición antes: {before_position} -> después: {state.position}")
        print(f"  Energía antes: {before_energy} -> después: {state.energy}")
        if boundary_hit:
            print("  Límite alcanzado: el equipo intentó salir del mundo y ajustó la trayectoria.")
        if event_note:
            print(f"  Evento aleatorio: {event_note}")
        else:
            print("  Evento aleatorio: ninguno.")
        if site:
            print(f"  Elemento del mundo: {site.replace('_', ' ')} en {state.position}.")
            print(f"  Efecto: {site_note}")
        else:
            print("  Elemento del mundo: ninguno.")
        print("  Explicación: cada paso consume energía; eventos y zonas especiales alteran la ruta o el recurso.")
        print()

        if state.position == config.goal:
            result = "éxito"
            cause = "la expedición llegó a la meta."
            break
        if state.energy <= 0:
            result = "fracaso"
            cause = "la energía se agotó."
            break
        if state.step >= config.max_steps:
            result = "éxito parcial"
            cause = "se alcanzó el límite máximo de pasos."
            break

    print("=== Informe final ===")
    print(f"Equipo: {config.team}")
    print(f"Nombre: {config.name}")
    print(f"Parámetros iniciales: inicio={config.start}, energía={config.energy}, radio={config.radius}, dificultad={config.difficulty}, modo={config.mode}")
    print(f"Posición final: {state.position}")
    print(f"Pasos realizados: {state.step}")
    print(f"Energía restante: {max(state.energy, 0)}")
    if state.highlights:
        print("Eventos y sitios importantes:")
        for entry in state.highlights[:10]:
            print(f"  - {entry}")
    else:
        print("Eventos y sitios importantes: ninguno.")
    print(f"Causa de finalización: {cause}")
    print(f"Resultado final: {result}")
    print("====================\n")


def main() -> None:
    while True:
        simulate_one_run()
        again = read_line("¿Quieres iniciar otra expedición? [s/N]: ", "n").lower()
        if again not in {"s", "si", "sí", "y", "yes"}:
            print("Fin del simulador.")
            break
 from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Tuple


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
from __future__ import annotations

from random import Random
from eventos import aplicar_evento_aleatorio
from mundo import Mundo


class Simulador:
    """Controla la temporada completa turno a turno."""

    def __init__(self, equipo: Equipo, mundo: Mundo, rng: Random | None = None) -> None:
        self.equipo = equipo
        self.mundo = mundo
        self.rng = rng or Random()
        self.max_pasos = 100
        self.ultimo_motivo = ""
        self.ultimo_resultado = ""
        self.parametros_iniciales = {
            "nombre": equipo.nombre,
            "posicion": equipo.posicion,
            "resistencia": equipo.resistencia,
            "moral": equipo.moral,
            "dinero": equipo.dinero,
        }

    def ejecutar(self) -> None:
        self._mostrar_intro()

        while True:
            self.equipo.pasos_realizados += 1
            paso = self.equipo.pasos_realizados

            print(f"\n=== Paso {paso} ===")

            if self.equipo.turnos_perdidos > 0:
                self.equipo.turnos_perdidos -= 1
                print("Turno perdido por un viaje complicado. No hay movimiento este paso.")
                self.equipo.modificar_resistencia(-1)
                self._mostrar_estado_basico()
                self._registrar_y_resolver_post_turno()
                if self._fin_del_juego():
                    break
                continue

            antes = self._capturar_estado()
            dx, dy, direccion = self._pedir_movimiento()
            print(f"Movimiento elegido: {direccion}")

            exito, mensaje_movimiento = self.mundo.intentar_mover(self.equipo, dx, dy)
            if not exito:
                print(mensaje_movimiento)
            print(f"Posición antes: {antes['posicion']} -> después: {self.equipo.posicion}")

            self.equipo.modificar_resistencia(-3)
            print(
                "Resistencia antes: "
                f"{antes['resistencia']} -> después: {self.equipo.resistencia}"
            )
            print(f"Moral antes: {antes['moral']} -> después: {self.equipo.moral}")
            print(f"Dinero antes: {antes['dinero']} -> después: {self.equipo.dinero}")
            print(f"Puntos antes: {antes['puntos']} -> después: {self.equipo.puntos_clasificacion}")

            evento = aplicar_evento_aleatorio(self.equipo, self.rng)
            if evento:
                print(f"Evento aleatorio: {evento}")
            else:
                print("Evento aleatorio: ninguno.")

            mensajes_ciudad = self.mundo.aplicar_ciudad_especial(self.equipo, self.rng)
            if mensajes_ciudad:
                print("Ciudad especial:")
                for mensaje in mensajes_ciudad:
                    print(f"  - {mensaje}")
            else:
                print("Ciudad especial: ninguna.")

            if self.mundo.partida_en(self.equipo.posicion) is not None:
                nombre_partido = self.mundo.partida_en(self.equipo.posicion)
                print(f"Partido automático: {nombre_partido}")
                for mensaje in self.mundo.jugar_partido_automatico(self.equipo, nombre_partido, self.rng):
                    print(f"  - {mensaje}")

            self._registrar_y_resolver_post_turno()
            if self._fin_del_juego():
                break

        self._mostrar_informe_final()

    def _mostrar_intro(self) -> None:
        print("\n========== CAMINO AL CAMPEONATO NACIONAL ==========")
        print(f"Nombre del equipo: {self.equipo.nombre}")
        print(f"Posición inicial: {self.equipo.posicion}")
        print(f"Resistencia inicial: {self.equipo.resistencia}")
        print(f"Moral inicial: {self.equipo.moral}")
        print(f"Dinero inicial: {self.equipo.dinero}")
        print(f"Puntos de clasificación iniciales: {self.equipo.puntos_clasificacion}")
        print(f"Límites del mundo: x e y de {self.mundo.limite_min} a {self.mundo.limite_max}")
        print(f"Campeonato Nacional en: {self.mundo.campeonato}")
        print("Condiciones de victoria: llegar a (20,20) con al menos 200 puntos de clasificación.")
        print("Condiciones de derrota: resistencia <= 0, moral <= 0 o más de 100 pasos.")
        print("===================================================\n")

    def _capturar_estado(self) -> dict[str, int | tuple[int, int]]:
        return {
            "posicion": self.equipo.posicion,
            "resistencia": self.equipo.resistencia,
            "moral": self.equipo.moral,
            "dinero": self.equipo.dinero,
            "puntos": self.equipo.puntos_clasificacion,
        }

    def _pedir_movimiento(self) -> tuple[int, int, str]:
        opciones = {
            "1": (0, 1, "Norte"),
            "2": (0, -1, "Sur"),
            "3": (1, 0, "Este"),
            "4": (-1, 0, "Oeste"),
        }
        while True:
            try:
                raw = input("Elige movimiento [1=Norte, 2=Sur, 3=Este, 4=Oeste]: ").strip()
            except EOFError:
                if self.equipo.posicion_x < self.mundo.limite_max:
                    print("Entrada finalizada. Se usa movimiento automático: Este.")
                    return opciones["3"]
                if self.equipo.posicion_y < self.mundo.limite_max:
                    print("Entrada finalizada. Se usa movimiento automático: Norte.")
                    return opciones["1"]
                print("Entrada finalizada. Se usa movimiento automático: Esperar.")
                return 0, 0, "Esperar"
            if raw in opciones:
                return opciones[raw]
            print("Opción no válida. Debes elegir 1, 2, 3 o 4.")

    def _registrar_y_resolver_post_turno(self) -> None:
        self._guardar_evento_importante()
        self._actualizar_resultado_si_corresponde()

    def _guardar_evento_importante(self) -> None:
        mensaje = (
            f"Paso {self.equipo.pasos_realizados}: "
            f"pos={self.equipo.posicion}, "
            f"res={self.equipo.resistencia}, "
            f"mor={self.equipo.moral}, "
            f"din={self.equipo.dinero}, "
            f"pts={self.equipo.puntos_clasificacion}"
        )
        self.equipo.registrar_evento(mensaje)

    def _actualizar_resultado_si_corresponde(self) -> None:
        if self.mundo.es_campeonato(self.equipo.posicion) and self.equipo.puntos_clasificacion >= 200:
            self.ultimo_motivo = "Llegaron al Campeonato Nacional con los puntos necesarios."
            self.ultimo_resultado = "Campeón Nacional"
            return
        if self.equipo.resistencia <= 0:
            self.ultimo_motivo = "La resistencia llegó a 0."
            self.ultimo_resultado = "Temporada fallida"
            return
        if self.equipo.moral <= 0:
            self.ultimo_motivo = "La moral llegó a 0."
            self.ultimo_resultado = "Temporada fallida"
            return
        if self.equipo.pasos_realizados > self.max_pasos:
            self.ultimo_motivo = "Se superó el límite de 100 pasos."
            self.ultimo_resultado = "Temporada fallida"
            return

    def _fin_del_juego(self) -> bool:
        if self.ultimo_resultado:
            return True
        return False

    def _mostrar_estado_basico(self) -> None:
        print(f"Posición actual: {self.equipo.posicion}")
        print(f"Resistencia: {self.equipo.resistencia}")
        print(f"Moral: {self.equipo.moral}")
        print(f"Dinero: {self.equipo.dinero}")
        print(f"Puntos de clasificación: {self.equipo.puntos_clasificacion}")

    def _mostrar_informe_final(self) -> None:
        if not self.ultimo_resultado:
            self._clasificar_temporada_final()

        print("\n========== INFORME FINAL ==========")
        print(f"Nombre del equipo: {self.equipo.nombre}")
        print(
            "Parámetros iniciales: "
            f"pos={self.parametros_iniciales['posicion']}, "
            f"resistencia={self.parametros_iniciales['resistencia']}, "
            f"moral={self.parametros_iniciales['moral']}, "
            f"dinero={self.parametros_iniciales['dinero']}"
        )
        print(f"Posición final: {self.equipo.posicion}")
        print(f"Pasos realizados: {self.equipo.pasos_realizados}")
        print(f"Resistencia restante: {self.equipo.resistencia}")
        print(f"Moral restante: {self.equipo.moral}")
        print(f"Dinero restante: {self.equipo.dinero}")
        print(f"Puntos de clasificación: {self.equipo.puntos_clasificacion}")
        print("Eventos importantes:")
        if self.equipo.eventos_importantes:
            for evento in self.equipo.eventos_importantes[:15]:
                print(f"  - {evento}")
        else:
            print("  - Ninguno.")
        print("Ciudades visitadas:")
        if self.equipo.ciudades_visitadas:
            for ciudad in self.equipo.ciudades_visitadas:
                print(f"  - {ciudad}")
        else:
            print("  - Ninguna.")
        print(f"Motivo de finalización: {self.ultimo_motivo}")
        print(f"Resultado final: {self.ultimo_resultado}")
        print("==================================\n")

    def _clasificar_temporada_final(self) -> None:
        if self.mundo.es_campeonato(self.equipo.posicion) and self.equipo.puntos_clasificacion >= 200:
            self.ultimo_resultado = "Campeón Nacional"
            self.ultimo_motivo = "Llegaron al Campeonato Nacional con los puntos necesarios."
        elif self.equipo.puntos_clasificacion >= 200:
            self.ultimo_resultado = "Clasificación conseguida"
            self.ultimo_motivo = "Se alcanzó la clasificación, pero no el campeonato."
        elif self.equipo.puntos_clasificacion >= 100:
            self.ultimo_resultado = "Temporada aceptable"
            self.ultimo_motivo = "Se completó una temporada competitiva con puntos suficientes."
        else:
            self.ultimo_resultado = "Temporada fallida"
            self.ultimo_motivo = "No se alcanzaron los puntos necesarios."    
from __future__ import 
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