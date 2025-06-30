# -*- coding: utf-8 -*-
"""
Megatetris Mejorado: Un clon del clásico juego Tetris implementado en Python
utilizando la librería Pygame.

Este script contiene toda la lógica del juego, desde la definición de las piezas
y el tablero, hasta el control de la partida, la renderización y la interfaz
de usuario (HUD).

Autor: [Tu Nombre/Alias Aquí]
Fecha: 30 de junio de 2025
"""

# -------------------------------------------------------------------
# MÓDULOS Y LIBRERÍAS
# -------------------------------------------------------------------
import random
import sys
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Tuple

import numpy as np
import pygame

# -------------------------------------------------------------------
# CONSTANTES DE CONFIGURACIÓN DEL JUEGO
# -------------------------------------------------------------------
# -- Dimensiones y Velocidad --
TAM_BLOQUE = 30  # Tamaño en píxeles de cada bloque cuadrado de una pieza.
COLUMNAS = 10  # Ancho del tablero de juego en número de bloques.
FILAS = 20  # Alto del tablero de juego en número de bloques.
SCREEN_W = COLUMNAS * TAM_BLOQUE + 150  # Ancho total de la ventana (tablero + espacio para HUD).
SCREEN_H = FILAS * TAM_BLOQUE  # Alto total de la ventana.
TARGET_FPS = 60  # Fotogramas por segundo objetivo para el bucle del juego.
BASE_SPEED_MS = 600  # Velocidad de caída inicial en milisegundos por paso.
MIN_SPEED_MS = 80  # Velocidad de caída mínima (máxima dificultad).
LEVEL_LINES = 10  # Cantidad de líneas a limpiar para subir de nivel.

# -- Colores (Tuplas RGB) --
COLOR_GRID = (50, 50, 50)  # Color de las líneas de la cuadrícula del tablero.
FONDO_NIVELES = [(25, 25, 25), (25, 45, 25), (25, 25, 45), (45, 25, 25)]  # Colores de fondo (actualmente solo se usa el primero).
COLORES_BLOQUES = [
    (0, 255, 255), (255, 0, 255), (255, 128, 0),
    (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
]

# -- Mecánicas de Juego --
# Desplazamientos para 'wall-kick', una técnica que permite rotar piezas cerca de las paredes.
WALL_KICKS = [(0, 0), (1, 0), (-1, 0), (0, -1)]

# -------------------------------------------------------------------
# DEFINICIÓN DE PIEZAS
# -------------------------------------------------------------------
class TipoPieza(Enum):
    """Enumeración para los distintos tipos de piezas (tetrominós)."""
    I = 0
    T = 1
    L = 2
    J = 3
    S = 4
    Z = 5
    O = 6

    @property
    def color(self) -> Tuple[int, int, int]:
        """Devuelve el color asociado a este tipo de pieza."""
        return COLORES_BLOQUES[self.value]

# Diccionario que mapea cada tipo de pieza a la forma de sus bloques.
# Las coordenadas son relativas a un punto de pivote (0,0).
FORMAS = {
    TipoPieza.I: [(-2, 0), (-1, 0), (0, 0), (1, 0)],
    TipoPieza.T: [(-1, 0), (0, 0), (1, 0), (0, -1)],
    TipoPieza.L: [(-1, 0), (0, 0), (1, 0), (-1, -1)],
    TipoPieza.J: [(-1, 0), (0, 0), (1, 0), (1, -1)],
    TipoPieza.S: [(-1, 0), (0, 0), (0, -1), (1, -1)],
    TipoPieza.Z: [(-1, -1), (0, -1), (0, 0), (1, 0)],
    TipoPieza.O: [(0, 0), (1, 0), (0, -1), (1, -1)],
}

def rotar_90(p: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calcula la nueva coordenada de un punto al rotarlo 90 grados en sentido horario
    alrededor del origen (0,0).

    Args:
        p (Tuple[int, int]): La coordenada (x, y) a rotar.

    Returns:
        Tuple[int, int]: La nueva coordenada después de la rotación.
    """
    x, y = p
    return -y, x

# -------------------------------------------------------------------
# MODELO DE DATOS (Clases para la lógica del juego)
# -------------------------------------------------------------------
@dataclass
class Pieza:
    """
    Representa una pieza activa en el juego.

    Attributes:
        tipo (TipoPieza): El tipo de tetrominó (I, T, L, etc.).
        pos (Tuple[int, int]): La posición (columna, fila) del pivote de la pieza en el tablero.
        bloques (List[Tuple[int, int]]): Coordenadas relativas de los bloques que la componen.
        has_held (bool): Bandera para controlar si la pieza ya fue guardada (hold).
    """
    tipo: TipoPieza
    pos: Tuple[int, int]
    bloques: List[Tuple[int, int]] = field(init=False)
    has_held: bool = False

    def __post_init__(self):
        """Inicializa los bloques de la pieza copiando su forma base."""
        self.bloques = FORMAS[self.tipo].copy()

    def celdas(self) -> List[Tuple[int, int]]:
        """
        Calcula las coordenadas absolutas de cada bloque de la pieza en el tablero.

        Returns:
            List[Tuple[int, int]]: Una lista de tuplas (columna, fila) para cada bloque.
        """
        x0, y0 = self.pos
        return [(x0 + dx, y0 + dy) for dx, dy in self.bloques]

    def mover(self, dx: int, dy: int, tab: 'Tablero') -> bool:
        """
        Intenta mover la pieza en una dirección (dx, dy).

        Args:
            dx (int): Desplazamiento horizontal.
            dy (int): Desplazamiento vertical.
            tab (Tablero): Referencia al tablero para validar el movimiento.

        Returns:
            bool: True si el movimiento fue exitoso, False en caso contrario.
        """
        nueva_pos = (self.pos[0] + dx, self.pos[1] + dy)
        celdas_propuestas = [(nueva_pos[0] + bx, nueva_pos[1] + by) for bx, by in self.bloques]
        if tab.validas(celdas_propuestas):
            self.pos = nueva_pos
            return True
        return False

    def rotar(self, tab: 'Tablero') -> None:
        """
        Intenta rotar la pieza 90 grados. Aplica 'wall-kicks' si es necesario.

        Args:
            tab (Tablero): Referencia al tablero para validar la rotación.
        """
        # La pieza 'O' no rota.
        if self.tipo is TipoPieza.O:
            return

        nueva_forma = [rotar_90(b) for b in self.bloques]

        # Intenta la rotación con cada posible 'wall-kick'.
        for ox, oy in WALL_KICKS:
            celdas_propuestas = [(self.pos[0] + dx + ox, self.pos[1] + dy + oy) for dx, dy in nueva_forma]
            if tab.validas(celdas_propuestas):
                self.bloques = nueva_forma
                self.pos = (self.pos[0] + ox, self.pos[1] + oy)
                break  # Sale del bucle al encontrar una rotación válida.

@dataclass
class Tablero:
    """
    Representa el estado del tablero de juego.

    Attributes:
        cols (int): Número de columnas.
        filas (int): Número de filas.
        grid (np.ndarray): Matriz 2D que almacena el estado de cada celda.
                           0 si está vacía, o el valor del tipo de pieza + 1 si está ocupada.
    """
    cols: int = COLUMNAS
    filas: int = FILAS
    grid: np.ndarray = field(default_factory=lambda: np.zeros((FILAS, COLUMNAS), int))

    def dentro(self, c: int, f: int) -> bool:
        """Verifica si una coordenada (c, f) está dentro de los límites del tablero."""
        return 0 <= c < self.cols and 0 <= f < self.filas

    def libre(self, c: int, f: int) -> bool:
        """Verifica si una celda (c, f) del tablero está vacía."""
        return self.grid[f, c] == 0

    def validas(self, celdas: Iterable[Tuple[int, int]]) -> bool:
        """Verifica si una colección de celdas son posiciones válidas y libres."""
        return all(self.dentro(c, f) and self.libre(c, f) for c, f in celdas)

    def fijar(self, p: Pieza) -> None:
        """
        Fija una pieza en el tablero, haciendo que sus bloques formen parte del grid.

        Args:
            p (Pieza): La pieza a fijar.
        """
        for c, f in p.celdas():
            if self.dentro(c, f):
                self.grid[f, c] = p.tipo.value + 1

    def limpiar(self) -> int:
        """
        Busca y elimina las filas completas del tablero.

        Returns:
            int: El número de filas limpiadas en esta operación.
        """
        # Encuentra los índices de las filas donde todas las celdas son no-cero.
        filas_llenas = [i for i in range(self.filas) if all(self.grid[i])]
        if not filas_llenas:
            return 0  # No hay nada que limpiar.

        # Elimina las filas llenas del grid.
        self.grid = np.delete(self.grid, filas_llenas, axis=0)

        # Añade nuevas filas vacías en la parte superior del tablero.
        nuevas_filas = np.zeros((len(filas_llenas), self.cols), int)
        self.grid = np.vstack([nuevas_filas, self.grid])

        return len(filas_llenas)

    def game_over(self) -> bool:
        """Verifica si la condición de Game Over se ha cumplido (bloques en la fila superior)."""
        return any(self.grid[0])

# -------------------------------------------------------------------
# CLASES AUXILIARES
# -------------------------------------------------------------------
class DeltaTimer:
    """
    Un temporizador que se activa a intervalos regulares, independiente de los FPS.
    Utiliza el tiempo delta (dt) para acumular tiempo.
    """

    def __init__(self, speed_ms: int):
        """
        Inicializa el temporizador con una velocidad de activación.

        Args:
            speed_ms (int): El intervalo en milisegundos para que el timer se active.
        """
        self.speed = speed_ms
        self.accum = 0

    def update(self, dt: int) -> bool:
        """
        Actualiza el temporizador con el tiempo transcurrido desde el último frame.

        Args:
            dt (int): Delta time en milisegundos.

        Returns:
            bool: True si el temporizador ha cumplido su intervalo, False de lo contrario.
        """
        self.accum += dt
        if self.accum >= self.speed:
            self.accum %= self.speed  # Resetea el acumulador conservando el exceso.
            return True
        return False

# -------------------------------------------------------------------
# CLASE PRINCIPAL DEL JUEGO
# -------------------------------------------------------------------
class Juego:
    """
    Clase que encapsula toda la lógica, el estado y la visualización del juego.
    """

    def __init__(self):
        """Inicializa Pygame, la ventana, y el estado inicial del juego."""
        # Inicialización de Pygame y la ventana.
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Megatetris Mejorado")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        # Creación de una superficie pre-renderizada para la cuadrícula para optimizar el dibujado.
        self.grid_surf = pygame.Surface((COLUMNAS * TAM_BLOQUE, FILAS * TAM_BLOQUE))
        self.grid_surf.fill(FONDO_NIVELES[0])
        for c in range(COLUMNAS + 1):
            x = c * TAM_BLOQUE
            pygame.draw.line(self.grid_surf, COLOR_GRID, (x, 0), (x, SCREEN_H))
        for r in range(FILAS + 1):
            y = r * TAM_BLOQUE
            pygame.draw.line(self.grid_surf, COLOR_GRID, (0, y), (COLUMNAS * TAM_BLOQUE, y))

        # Inicialización del estado del juego.
        self.tab = Tablero()
        self.bag = deque()  # '7-bag' para generar piezas de forma pseudo-aleatoria.
        self.pieza = self._sacar_pieza()
        self.next = self._sacar_pieza()
        self.hold = None

        # Estadísticas del jugador.
        self.level = 1
        self.lines = 0
        self.score = 0
        self.timer = DeltaTimer(BASE_SPEED_MS)

    def _sacar_pieza(self) -> Pieza:
        """
        Obtiene una nueva pieza del '7-bag'. Si el 'bag' está casi vacío, lo rellena.

        Returns:
            Pieza: La nueva pieza generada.
        """
        if len(self.bag) < 2:
            # Rellena el 'bag' con las 7 piezas en orden aleatorio.
            piezas_nuevas = list(TipoPieza)
            random.shuffle(piezas_nuevas)
            self.bag.extend(piezas_nuevas)
        
        tipo_pieza = self.bag.popleft()
        return Pieza(tipo_pieza, (COLUMNAS // 2, 0)) # Posición inicial en la parte superior central.

    def _update_speed(self):
        """Actualiza la velocidad de caída de la pieza según el nivel actual."""
        ms = max(MIN_SPEED_MS, BASE_SPEED_MS - (self.level - 1) * 50)
        self.timer.speed = ms

    def _lock_piece(self):
        """Fija la pieza actual, limpia líneas, actualiza puntaje y genera una nueva pieza."""
        self.tab.fijar(self.pieza)
        cleared = self.tab.limpiar()

        if cleared:
            self.lines += cleared
            self.score += cleared * 100 * self.level
            # Calcula el nuevo nivel basado en el total de líneas limpiadas.
            new_level = self.lines // LEVEL_LINES + 1
            if new_level > self.level:
                self.level = new_level
                self._update_speed()

        # La pieza siguiente ('next') se convierte en la pieza actual.
        self.pieza = self.next
        self.next = self._sacar_pieza()
        
        # Permite usar la función 'hold' de nuevo.
        self.pieza.has_held = False

    def _hard_drop(self):
        """Deja caer la pieza instantáneamente hasta el fondo."""
        # Mueve la pieza hacia abajo hasta que no pueda más.
        while self.pieza.mover(0, 1, self.tab):
            pass
        self._lock_piece()

    def _draw_hud(self):
        """Dibuja toda la información de la interfaz (Score, Level, Next, Hold)."""
        # Dibuja el texto de Score, Lines y Level.
        hud_texts = [f"Score: {self.score}", f"Lines: {self.lines}", f"Level: {self.level}"]
        for i, text in enumerate(hud_texts):
            surf = self.font.render(text, True, (240, 240, 240))
            self.screen.blit(surf, (COLUMNAS * TAM_BLOQUE + 10, 10 + i * 20))

        # Dibuja la previsualización de la pieza 'Next'.
        self.font.set_italic(True)
        self.screen.blit(self.font.render("Next:", True, (240, 240, 240)), (COLUMNAS * TAM_BLOQUE + 10, 80))
        for dx, dy in FORMAS[self.next.tipo]:
            x = COLUMNAS * TAM_BLOQUE + 50 + dx * TAM_BLOQUE // 2
            y = 120 + dy * TAM_BLOQUE // 2
            rect = pygame.Rect(x, y, TAM_BLOQUE // 2, TAM_BLOQUE // 2)
            pygame.draw.rect(self.screen, self.next.tipo.color, rect)
        
        # Dibuja la pieza en 'Hold' si existe.
        self.screen.blit(self.font.render("Hold:", True, (240, 240, 240)), (COLUMNAS * TAM_BLOQUE + 10, 200))
        if self.hold:
            for dx, dy in FORMAS[self.hold.tipo]:
                x = COLUMNAS * TAM_BLOQUE + 50 + dx * TAM_BLOQUE // 2
                y = 230 + dy * TAM_BLOQUE // 2
                rect = pygame.Rect(x, y, TAM_BLOQUE // 2, TAM_BLOQUE // 2)
                pygame.draw.rect(self.screen, self.hold.tipo.color, rect)
        
        self.font.set_italic(False)

    def run(self):
        """El bucle principal del juego que maneja eventos, lógica y renderizado."""
        running = True
        while running:
            # Calcula el tiempo delta (dt) para un movimiento y lógica consistentes.
            dt = self.clock.tick(TARGET_FPS)

            # --- GESTIÓN DE EVENTOS ---
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        self.pieza.mover(-1, 0, self.tab)
                    elif e.key == pygame.K_RIGHT:
                        self.pieza.mover(1, 0, self.tab)
                    elif e.key == pygame.K_DOWN:
                        # Si no puede bajar más, se fija. Si no, baja un paso.
                        if not self.pieza.mover(0, 1, self.tab):
                            self._lock_piece()
                    elif e.key == pygame.K_UP:
                        self.pieza.rotar(self.tab)
                    elif e.key == pygame.K_SPACE:
                        self._hard_drop()
                    elif e.key == pygame.K_c: # Tecla para 'Hold'
                        # Solo se puede hacer 'hold' una vez por pieza.
                        if not self.pieza.has_held:
                            if self.hold is None:
                                self.hold = self.pieza
                                self.pieza = self.next
                                self.next = self._sacar_pieza()
                            else:
                                # Intercambia la pieza actual con la de 'hold'.
                                self.hold, self.pieza = self.pieza, self.hold
                            
                            self.pieza.pos = (COLUMNAS // 2, 0) # Resetea la posición.
                            self.pieza.has_held = True # Bloquea el 'hold' para esta pieza.

            # --- LÓGICA DEL JUEGO ---
            # Caída automática de la pieza basada en el temporizador.
            if self.timer.update(dt):
                if not self.pieza.mover(0, 1, self.tab):
                    self._lock_piece()

            # --- DIBUJADO / RENDERIZADO ---
            # 1. Limpia toda la pantalla con un fondo negro.
            self.screen.fill((0, 0, 0))
            # 2. Dibuja la cuadrícula pre-renderizada.
            self.screen.blit(self.grid_surf, (0, 0))
            # 3. Dibuja los bloques ya fijados en el tablero.
            for r in range(FILAS):
                for c in range(COLUMNAS):
                    val_celda = self.tab.grid[r, c]
                    if val_celda:
                        rect = pygame.Rect(c * TAM_BLOQUE + 1, r * TAM_BLOQUE + 1, TAM_BLOQUE - 2, TAM_BLOQUE - 2)
                        pygame.draw.rect(self.screen, COLORES_BLOQUES[val_celda - 1], rect)
            # 4. Dibuja la pieza activa.
            for c, r in self.pieza.celdas():
                rect = pygame.Rect(c * TAM_BLOQUE + 1, r * TAM_BLOQUE + 1, TAM_BLOQUE - 2, TAM_BLOQUE - 2)
                pygame.draw.rect(self.screen, self.pieza.tipo.color, rect)
            # 5. Dibuja la interfaz de usuario (HUD).
            self._draw_hud()

            # 6. Actualiza la pantalla para mostrar todo lo dibujado.
            pygame.display.flip()

            # --- COMPROBACIÓN DE FIN DE JUEGO ---
            if self.tab.game_over():
                pygame.time.wait(1500) # Pausa para que el jugador vea el tablero final.
                running = False

        # Cierra Pygame y el programa al salir del bucle.
        pygame.quit()
        sys.exit()

# -------------------------------------------------------------------
# PUNTO DE ENTRADA PRINCIPAL
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Crea una instancia del juego y ejecuta el bucle principal.
    juego = Juego()
    juego.run()
