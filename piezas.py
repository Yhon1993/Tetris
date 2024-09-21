
# piezas.py

import numpy as np

# Definición del diccionario de piezas
piezas = {
    "t": [np.array([0, 0]), np.array([1, 0]), np.array([-1, 0]), np.array([0, -1])],
    "L": [np.array([0, 0]), np.array([1, 1]), np.array([0, -1]), np.array([0, 1])],
    "Lin": [np.array([0, 0]), np.array([-1, 1]), np.array([0, -1]), np.array([0, 1])],
    "i": [np.array([-1, 2]), np.array([-1, 1]), np.array([-1, 0]), np.array([-1, -1])],
    "s": [np.array([0, 0]), np.array([0, 1]), np.array([1, 0]), np.array([1, -1])],
    "z": [np.array([0, 0]), np.array([0, -1]), np.array([1, 0]), np.array([1, 1])],
    "o": [np.array([0, 0]), np.array([1, 0]), np.array([0, 1]), np.array([1, 1])],
}

# Definición de las rotaciones para la pieza "i"
giros_i = [
    [np.array([-1, 2]), np.array([-1, 1]), np.array([-1, 0]), np.array([-1, -1])],
    [np.array([-2, 0]), np.array([-1, 0]), np.array([0, 0]), np.array([1, 0])],
    [np.array([0, 2]), np.array([0, 1]), np.array([0, 0]), np.array([0, -1])],
    [np.array([-2, 1]), np.array([-1, 1]), np.array([0, 1]), np.array([1, 1])],
]

def get_all(dict_obj):
    """Retorna todas las claves del diccionario."""
    return list(dict_obj.keys())

class Pieza:
    """Clase para manejar las piezas del Tetris."""
    def __init__(self, posicion, tipo):
        """
        Inicializa una nueva pieza.

        Args:
            posicion (np.array): Coordenadas iniciales de la pieza en el tablero.
            tipo (str): Tipo de la pieza (e.g., "t", "L", "i", etc.).
        """
        self.posicion = posicion  # Posición actual de la pieza en el tablero
        self.tipo = tipo  # Tipo de pieza (e.g., "t", "L", "i", etc.)
        self.espacios = piezas[tipo].copy()  # Copia de las coordenadas de la pieza
        self.giros = -1  # Inicialización de giros para manejar rotaciones

    def get_piezas_keys(self):
        """Retorna todas las claves del diccionario de piezas."""
        return get_all(piezas)

    def giro(self, game_state, nxC):
        """
        Rotar la pieza si es posible.

        Args:
            game_state (np.array): Estado actual del tablero del juego.
            nxC (int): Número de columnas del tablero.
        """
        espacios2 = []
        if self.tipo == "o":
            return  # La pieza "o" no necesita rotación
        elif self.tipo == "i":
            # Rotaciones específicas para la pieza "i"
            if self.giros + 1 >= len(giros_i):
                return  # No hay más rotaciones disponibles
            for num in range(4):
                new_espace = giros_i[self.giros + 1][num]
                espacios2.append(new_espace)
                x, y = new_espace[0] + self.posicion[0], new_espace[1] + self.posicion[1]
                # Verificar colisión
                if (x < 0 or x >= nxC or y < 0 or y >= game_state.shape[1] or game_state[x, y] == 1):
                    return  # No se puede rotar
        else:
            # Rotaciones para otras piezas
            for esp in self.espacios:
                new_espace = np.array([0, 0])
                new_espace[1] = esp[0]
                new_espace[0] = esp[1] * -1
                espacios2.append(new_espace)
                x, y = new_espace[0] + self.posicion[0], new_espace[1] + self.posicion[1]
                # Verificar colisión
                if (x < 0 or x >= nxC or y < 0 or y >= game_state.shape[1] or game_state[x, y] == 1):
                    return  # No se puede rotar

        # Actualizar el índice de rotación
        self.giros = (self.giros + 1) % 4
        self.espacios = espacios2

    def mover_horizontal(self, game, cuanto, direccion):
        """
        Mover la pieza a la izquierda o derecha.

        Args:
            game (Game): Instancia actual del juego.
            cuanto (int): Cantidad de unidades para mover.
            direccion (int): Dirección del movimiento (-1 para izquierda, 1 para derecha).
        """
        puede = True
        if direccion == -1:
            for esp in self.espacios:
                x, y = esp[0] + self.posicion[0] - 1, esp[1] + self.posicion[1]
                if (x < 0 or x >= game.tablero.tx or game.game_state[x, y] == 1):
                    puede = False
                    break
        elif direccion == 1:
            for esp in self.espacios:
                x, y = esp[0] + self.posicion[0] + 1, esp[1] + self.posicion[1]
                if (x < 0 or x >= game.tablero.tx or game.game_state[x, y] == 1):
                    puede = False
                    break

        if puede:
            self.posicion[0] += cuanto

    def mover_vertical(self, estado, tx, ty):
        """
        Mover la pieza hacia abajo.

        Args:
            estado (np.array): Estado actual del tablero del juego.
            tx (int): Número de columnas del tablero.
            ty (int): Número de filas del tablero.

        Returns:
            bool: True si la pieza no puede caer más, False si puede seguir cayendo.
        """
        puede = True
        for pos in self.espacios:
            x, y = pos[0] + self.posicion[0], pos[1] + self.posicion[1] + 1
            if (y >= ty or estado[x, y] == 1):
                puede = False
                break

        if puede:
            self.posicion[1] += 1
            return False  # La pieza ha caído exitosamente
        else:
            return True  # La pieza no puede caer más

    def caer(self, game):
        """
        Hacer caer la pieza. Si no puede caer más, fijarla en el tablero y generar una nueva pieza.

        Args:
            game (Game): Instancia actual del juego.
        """
        if self.mover_vertical(game.game_state, game.tablero.tx, game.tablero.ty):
            for pos in self.espacios:
                x = pos[0] + self.posicion[0]
                y = pos[1] + self.posicion[1]
                if 0 <= x < game.tablero.tx and 0 <= y < game.tablero.ty:
                    game.game_state[x, y] = 1
            # Generar una nueva pieza
            if not game.piezas_desordenadas:
                game.desordenar_piezas()
            self.tipo = game.piezas_desordenadas.pop(0)
            self.espacios = piezas[self.tipo].copy()
            self.posicion = np.array([5, 0])
            self.giros = -1