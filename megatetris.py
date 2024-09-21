# megatetris.py

import pygame
import numpy as np
import time
import random
import os
from piezas import Pieza, piezas, get_all  # Importar la clase Pieza y el diccionario de piezas

# Función para limpiar la consola
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

class Tablero:
    """Clase que representa el tablero de Tetris."""
    def __init__(self, tamaño_x=10, tamaño_y=20, tamaño_cuadrado=25, c_fondo=[(25, 25, 25)]):
        self.tamaño = tamaño_cuadrado
        self.tx, self.ty = tamaño_x, tamaño_y
        self.width, self.height = tamaño_x * tamaño_cuadrado, tamaño_y * tamaño_cuadrado
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(c_fondo[0])
        self.bg = c_fondo  # Lista de colores de fondo para niveles

class Game:
    """Clase que maneja la lógica del juego de Tetris."""
    def __init__(self, tablero):
        self.tablero = tablero
        self.game_state = np.zeros((self.tablero.tx, self.tablero.ty))
        self.pieza_state = np.zeros((self.tablero.tx, self.tablero.ty))
        self.pieza = Pieza(np.array([5, 0]), "i")  # Pieza inicial
        self.nivel = 1
        self.lineas_eliminadas = 0
        self.velocidad = self.tablero.tx
        self.d_tiempo = 1
        self.puntos = 0
        self.piezas_desordenadas = []

    def desordenar_piezas(self):
        """Desordenar las piezas para el juego."""
        self.piezas_desordenadas.clear()
        orden = list(piezas.keys())
        random.shuffle(orden)
        self.piezas_desordenadas = orden

    def actualizar_grafico(self):
        """Actualizar el gráfico en pantalla."""
        self.tablero.screen.fill(self.tablero.bg[(self.nivel - 1) % len(self.tablero.bg)])
        for y in range(self.tablero.ty):
            for x in range(self.tablero.tx):
                poly = [
                    (x * self.tablero.tamaño, y * self.tablero.tamaño),
                    ((x + 1) * self.tablero.tamaño, y * self.tablero.tamaño),
                    ((x + 1) * self.tablero.tamaño, (y + 1) * self.tablero.tamaño),
                    (x * self.tablero.tamaño, (y + 1) * self.tablero.tamaño),
                ]
                if self.game_state[x, y] == 1:
                    pygame.draw.polygon(self.tablero.screen, (255, 255, 255), poly, 0)
                elif self.pieza_state[x, y] == 1:
                    pygame.draw.polygon(self.tablero.screen, (0, 255, 0), poly, 0)
                else:
                    pygame.draw.polygon(self.tablero.screen, (50, 50, 50), poly, 1)

    def eliminar_lineas(self):
        """Eliminar líneas completas del tablero."""
        lineas_completadas = 0
        for i in range(self.tablero.ty):
            if not (False in self.game_state[:, i]):  # Si la fila está llena
                lineas_completadas += 1
                self.game_state[:, i] = 0
                for y in range(i, 0, -1):  # Mover líneas superiores hacia abajo
                    self.game_state[:, y] = self.game_state[:, y - 1]
                self.puntos += 100 + (100 * (lineas_completadas - 1) / 2)
                self.lineas_eliminadas += 1
                if self.puntos >= 1000 * self.nivel:
                    self.pasar_de_nivel()
                self.actualizar_datos()

    def pasar_de_nivel(self):
        """Pasar al siguiente nivel."""
        self.nivel += 1
        if self.nivel < 4:
            self.velocidad /= self.nivel / 2
        else:
            self.velocidad /= self.nivel / 4
        self.velocidad = max(1, round(self.velocidad))  # Asegura que la velocidad no sea menor a 1
        self.d_tiempo *= self.nivel / 2
        self.actualizar_datos()

    def actualizar_datos(self):
        """Mostrar estadísticas del juego en consola."""
        clear()
        print(f"Puntos: {self.puntos}")
        print(f"Líneas eliminadas: {self.lineas_eliminadas}")
        print(f"Nivel: {self.nivel}")

    def check_game_over(self):
        """Comprobar si la pieza ha llegado a la parte superior del tablero."""
        if np.any(self.game_state[:, 0]):
            print("¡Game Over!")
            return True
        return False

def main():
    # Inicialización de Pygame
    pygame.init()
    pygame.display.set_caption("Megatetris")
    tablero = Tablero(10, 20, 25, [(25, 25, 25), (25, 45, 25), (25, 25, 45), (45, 25, 25)])
    game = Game(tablero)

    clock = pygame.time.Clock()

    # Variables de control
    left_pressed = 0
    right_pressed = 0
    down_pressed = 0

    game.actualizar_datos()

    game.desordenar_piezas()
    game.pieza.tipo = game.piezas_desordenadas.pop(0)
    game.pieza.espacios = piezas[game.pieza.tipo]
    if not game.piezas_desordenadas:
        game.desordenar_piezas()

    ciclos = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.pieza.giro(game.game_state, game.tablero.tx)
                if event.key == pygame.K_LEFT:
                    left_pressed = 1
                if event.key == pygame.K_RIGHT:
                    right_pressed = 1
                if event.key == pygame.K_DOWN:
                    down_pressed = 1
                if event.key == pygame.K_0:
                    game.pasar_de_nivel()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_pressed = 0
                if event.key == pygame.K_RIGHT:
                    right_pressed = 0
                if event.key == pygame.K_DOWN:
                    down_pressed = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False

        if left_pressed:
            game.pieza.mover_horizontal(game, -1, -1)
        if right_pressed:
            game.pieza.mover_horizontal(game, 1, 1)
        if down_pressed:
            game.pieza.caer(game)

        # Controlar la velocidad de caída
        if ciclos % max(1, game.velocidad) == 0:
            game.pieza.caer(game)

        # Actualizar estado de la pieza en el tablero
        game.pieza_state = np.zeros((game.tablero.tx, game.tablero.ty))
        for pos in game.pieza.espacios:
            x = pos[0] + game.pieza.posicion[0]
            y = pos[1] + game.pieza.posicion[1]
            if 0 <= x < game.tablero.tx and 0 <= y < game.tablero.ty:
                game.pieza_state[x, y] = 1

        # Actualizar gráficos
        game.actualizar_grafico()

        # Eliminar líneas completas
        game.eliminar_lineas()

        pygame.display.flip()

        # Limitar a 60 FPS
        clock.tick(60)
        ciclos += 1

        # Verificar Game Over
        if game.check_game_over():
            running = False

    pygame.quit()

if __name__ == "__main__":
    clear()
    main()
