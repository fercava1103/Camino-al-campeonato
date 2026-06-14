from __future__ import annotations

from random import Random

from equipo import Equipo
from mundo import Mundo


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
