from __future__ import annotations

"""Megatetris — versión completa
===========================================================
Tetris minimalista con Pygame + NumPy.

Arquitectura *MVC*:
    • Modelo  → `Tablero` y `Pieza` (reglas y estado).
    • Vista   → funciones de dibujo.
    • Control → clase `Juego` (bucle principal y eventos).

Instalación dependencias:
    pip install pygame numpy
"""

###############################################################################
# IMPORTACIONES                                                               #
###############################################################################

# Librerías estándar para lógica de juego, sistema y tipado
import random
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Tuple

# Librerías externas para manejo de matrices y gráficos
import numpy as np
import pygame

###############################################################################
# CONSTANTES                                                                  #
###############################################################################

TAM_BLOQUE: int = 30          # Tamaño en píxeles de cada bloque de la cuadrícula
COLUMNAS: int = 10            # Número de columnas del tablero
FILAS: int = 20               # Número de filas del tablero
FPS: int = 60                 # Fotogramas por segundo del juego

COLOR_CUADRICULA = (50, 50, 50)  # Color de las líneas de la cuadrícula
COLORES_FONDO = [                # Colores de fondo según nivel
    (25, 25, 25),
    (25, 45, 25),
    (25, 25, 45),
    (45, 25, 25),
]
COLORES_BLOQUE = [               # Colores de cada tipo de pieza
    (0, 255, 255),  # I
    (255, 0, 255),  # T
    (255, 128, 0),  # L
    (0, 0, 255),    # J
    (0, 255, 0),    # S
    (255, 0, 0),    # Z
    (255, 255, 0),  # O
]

###############################################################################
# ENUMERACIONES Y FORMAS                                                      #
###############################################################################

class TipoPieza(Enum):
    """Enumera los tipos de pieza de Tetris y proporciona su color."""
    I = 0; T = 1; L = 2; J = 3; S = 4; Z = 5; O = 6

    @property
    def color(self) -> Tuple[int,int,int]:
        """Devuelve el color RGB asociado al tipo de pieza."""
        return COLORES_BLOQUE[self.value]

# Definición de las formas relativas de cada pieza respecto a su posición central
FORMAS: dict[TipoPieza, List[Tuple[int,int]]] = {
    TipoPieza.I: [(-2, 0), (-1, 0), (0, 0), (1, 0)],
    TipoPieza.T: [(-1, 0), (0, 0), (1, 0), (0, -1)],
    TipoPieza.L: [(-1, 0), (0, 0), (1, 0), (-1, -1)],
    TipoPieza.J: [(-1, 0), (0, 0), (1, 0), (1, -1)],
    TipoPieza.S: [(-1, 0), (0, 0), (0, -1), (1, -1)],
    TipoPieza.Z: [(-1, -1), (0, -1), (0, 0), (1, 0)],
    TipoPieza.O: [(0, 0), (1, 0), (0, -1), (1, -1)],
}

###############################################################################
# AUXILIARES                                                                  #
###############################################################################

# Función auxiliar para rotar un punto 90 grados en sentido antihorario
def rotar_90(p: Tuple[int,int]) -> Tuple[int,int]:
    """Rota 90° un par de coordenadas (x, y) y devuelve (−y, x)."""
    x, y = p
    return -y, x

###############################################################################
# MODELO                                                                      #
###############################################################################

@dataclass
class Pieza:
    """Representa una pieza en juego con su tipo, posición y bloques relativos."""
    tipo: TipoPieza
    pos: Tuple[int, int]
    bloques: List[Tuple[int, int]] = field(init=False)

    def __post_init__(self):
        """Inicializa la lista de bloques copiando la forma base según el tipo."""
        self.bloques = FORMAS[self.tipo].copy()

    def celdas(self) -> List[Tuple[int,int]]:
        """Devuelve las coordenadas absolutas de cada bloque de la pieza."""
        c0, f0 = self.pos
        return [(c0 + dx, f0 + dy) for dx, dy in self.bloques]

    def rotar(self, tab: Tablero) -> None:
        """
        Rota la pieza 90° si no es cuadrada y la nueva posición es válida.
        Comprueba colisiones con el tablero antes de aplicar la rotación.
        """
        if self.tipo is TipoPieza.O:
            return  # La pieza O no rota
        nuevos = [rotar_90(b) for b in self.bloques]
        nuevas_celdas = [(self.pos[0] + dx, self.pos[1] + dy) for dx, dy in nuevos]
        if tab.validas(nuevas_celdas):
            self.bloques = nuevos

    def mover(self, dc: int, df: int, tab: Tablero) -> bool:
        """
        Intenta mover la pieza en horizontal (dc) y vertical (df).
        Retorna True si el movimiento es válido y actualiza la posición.
        """
        nueva_pos = (self.pos[0] + dc, self.pos[1] + df)
        nuevas_celdas = [(nueva_pos[0] + dx, nueva_pos[1] + dy) for dx, dy in self.bloques]
        if tab.validas(nuevas_celdas):
            self.pos = nueva_pos
            return True
        return False

@dataclass
class Tablero:
    """Modelo de la cuadrícula del juego: estado de celdas y operaciones de línea."""
    cols: int = COLUMNAS
    filas: int = FILAS
    grid: np.ndarray = field(default_factory=lambda: np.zeros((FILAS, COLUMNAS), int))

    def dentro(self, c: int, f: int) -> bool:
        """Comprueba si la columna c y fila f están dentro del tablero."""
        return 0 <= c < self.cols and 0 <= f < self.filas

    def libre(self, c: int, f: int) -> bool:
        """Indica si la celda (c, f) está vacía (valor 0)."""
        return self.grid[f, c] == 0

    def validas(self, celdas: Iterable[Tuple[int,int]]) -> bool:
        """Comprueba que todas las celdas dadas estén dentro y libres."""
        return all(self.dentro(c, f) and self.libre(c, f) for c, f in celdas)

    def fijar(self, p: Pieza) -> None:
        """Fija la pieza p en el tablero marcando sus celdas con su índice (+1)."""
        for c, f in p.celdas():
            self.grid[f, c] = p.tipo.value + 1

    def limpiar(self) -> int:
        """
        Elimina las filas completas y añade filas vacías en la parte superior.
        Retorna el número de filas eliminadas.
        """
        llenas = [i for i in range(self.filas) if all(self.grid[i])]
        if llenas:
            # Eliminar filas completas
            self.grid = np.delete(self.grid, llenas, axis=0)
            # Añadir filas vacías arriba
            nuevas = np.zeros((len(llenas), self.cols), int)
            self.grid = np.vstack([nuevas, self.grid])
        return len(llenas)

    def over(self) -> bool:
        """Determina si el juego ha terminado (si alguna celda de la fila 0 está ocupada)."""
        return any(self.grid[0])

###############################################################################
# TEMPORIZADOR                                                                #
###############################################################################

class Timer:
    """Controla el tiempo para movimientos automáticos de la pieza."""
    def __init__(self, ms: int):
        """
        Inicializa el temporizador.
        :param ms: Intervalo en milisegundos para disparar el evento.
        """
        self.ms = ms
        self.t0 = pygame.time.get_ticks()

    def listo(self) -> bool:
        """
        Comprueba si ha transcurrido el intervalo.
        Si es así, reinicia el contador y retorna True.
        """
        t = pygame.time.get_ticks()
        if t - self.t0 >= self.ms:
            self.t0 = t
            return True
        return False

###############################################################################
# CONTROL Y VISTA                                                             #
###############################################################################

class Juego:
    """Clase principal que integra la lógica del juego y la renderización."""
    def __init__(self):
        """Configura Pygame, crea el tablero, la primera pieza y valores iniciales."""
        pygame.init()
        self.screen = pygame.display.set_mode((COLUMNAS * TAM_BLOQUE, FILAS * TAM_BLOQUE))
        pygame.display.set_caption("Megatetris — Español")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        self.tab = Tablero()
        self.bag: List[TipoPieza] = []
        self.pieza: Pieza = self._nueva()

        self.nivel = 1
        self.lineas = 0
        self.puntos = 0
        self.timer = Timer(self._intervalo())

    # ----- Gestión de la 'bolsa' y creación de nuevas piezas -----

    def _nueva(self) -> Pieza:
        """
        Saca una pieza aleatoria de la bolsa.
        Rellena la bolsa con las 7 piezas cuando está vacía.
        """
        if not self.bag:
            self.bag = random.sample(list(TipoPieza), 7)
        tipo = self.bag.pop()
        # Posición inicial centrada en la parte superior
        return Pieza(tipo, (COLUMNAS // 2, 0))

    def _intervalo(self) -> int:
        """
        Calcula el intervalo de caída automática según el nivel actual.
        Disminuye el tiempo con niveles más altos, hasta un mínimo de 80 ms.
        """
        return max(80, 600 - (self.nivel - 1) * 50)

    # ----- Lógica de fijado y borrado de líneas -----

    def _bloquear(self) -> None:
        """
        Fija la pieza actual en el tablero, limpia líneas completas,
        actualiza puntos, nivel y configura nueva pieza.
        """
        self.tab.fijar(self.pieza)
        limp = self.tab.limpiar()
        if limp:
            self.lineas += limp
            self.puntos += limp * 100 * self.nivel
            # Subir de nivel cada 10 líneas
            nuevo_nivel = self.lineas // 10 + 1
            if nuevo_nivel > self.nivel:
                self.nivel = nuevo_nivel
                self.timer.ms = self._intervalo()
        self.pieza = self._nueva()

    def _soft(self) -> None:
        """
        Movimiento suave: baja la pieza un paso.
        Si choca, fija la pieza (_bloquear).
        """
        if not self.pieza.mover(0, 1, self.tab):
            self._bloquear()

    def _hard(self) -> None:
        """
        Movimiento duro: baja la pieza hasta el fondo de golpe
        y luego fija la pieza (_bloquear).
        """
        while self.pieza.mover(0, 1, self.tab):
            pass
        self._bloquear()

    # ----- Renderizado de pantalla -----

    def _draw(self) -> None:
        """
        Dibuja fondo, cuadrícula, bloques fijos, pieza activa y HUD.
        """
        # Fondo según nivel
        color_fondo = COLORES_FONDO[(self.nivel - 1) % len(COLORES_FONDO)]
        self.screen.fill(color_fondo)

        # Dibujar líneas de cuadrícula
        for c in range(COLUMNAS):
            x = c * TAM_BLOQUE
            pygame.draw.line(self.screen, COLOR_CUADRICULA, (x, 0), (x, FILAS * TAM_BLOQUE))
        for f in range(FILAS):
            y = f * TAM_BLOQUE
            pygame.draw.line(self.screen, COLOR_CUADRICULA, (0, y), (COLUMNAS * TAM_BLOQUE, y))

        # Dibujar bloques fijos en el tablero
        for f in range(FILAS):
            for c in range(COLUMNAS):
                v = self.tab.grid[f, c]
                if v:
                    rect = pygame.Rect(
                        c * TAM_BLOQUE + 1,
                        f * TAM_BLOQUE + 1,
                        TAM_BLOQUE - 2,
                        TAM_BLOQUE - 2
                    )
                    pygame.draw.rect(self.screen, COLORES_BLOQUE[v - 1], rect)

        # Dibujar pieza activa
        for c, f in self.pieza.celdas():
            rect = pygame.Rect(
                c * TAM_BLOQUE + 1,
                f * TAM_BLOQUE + 1,
                TAM_BLOQUE - 2,
                TAM_BLOQUE - 2
            )
            pygame.draw.rect(self.screen, self.pieza.tipo.color, rect)

        # Dibujar HUD (puntos, líneas, nivel)
        textos = [f"Puntos: {self.puntos}", f"Líneas: {self.lineas}", f"Nivel: {self.nivel}"]
        for i, txt in enumerate(textos):
            surf = self.font.render(txt, True, (240, 240, 240))
            self.screen.blit(surf, (5, 5 + i * 18))

    def _gameover(self) -> None:
        """
        Muestra la pantalla de Game Over con semitransparencia
        y espera 2.5 segundos antes de salir.
        """
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        txt = self.font.render("GAME OVER", True, (255, 60, 60))
        rect = txt.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(txt, rect)
        pygame.display.flip()
        pygame.time.wait(2500)

    # ----- Bucle principal del juego -----

    def run(self) -> None:
        """
        Ejecuta el bucle principal: procesa eventos, actualiza estado,
        dibuja y comprueba fin de juego.
        """
        running = True
        while running:
            # Control de FPS
            self.clock.tick(FPS)

            # Gestión de eventos de usuario
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        self.pieza.mover(-1, 0, self.tab)
                    elif e.key == pygame.K_RIGHT:
                        self.pieza.mover(1, 0, self.tab)
                    elif e.key == pygame.K_DOWN:
                        self._soft()
                    elif e.key == pygame.K_UP:
                        self.pieza.rotar(self.tab)
                    elif e.key == pygame.K_SPACE:
                        self._hard()

            # Salir con ESC
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False

            # Caída automática según temporizador
            if self.timer.listo():
                self._soft()

            # Dibujar todo y actualizar pantalla
            self._draw()
            pygame.display.flip()

            # Comprobar Game Over
            if self.tab.over():
                self._gameover()
                running = False

        # Salir de Pygame y del programa
        pygame.quit()
        sys.exit()

###############################################################################
# MAIN                                                                        #
###############################################################################

if __name__ == "__main__":
    # Inicia el juego cuando se ejecute directamente este archivo
    Juego().run()
