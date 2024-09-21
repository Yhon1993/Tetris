
# MegaTetris

Este proyecto es una implementación del juego **Tetris** en Python utilizando la librería **Pygame**. Además de las funcionalidades básicas del Tetris, el juego incluye niveles con diferentes velocidades y una interfaz gráfica simple pero efectiva.

## Estructura del Proyecto

El proyecto se compone de dos archivos principales:

1. **megatetris.py**: Es el archivo principal del juego donde se define la clase `Game` y el flujo principal del juego.
2. **piezas.py**: Contiene la definición de las piezas del Tetris y su comportamiento (movimientos, rotaciones).

## Instalación

1. Clonar este repositorio o descargar los archivos.
2. Asegúrate de tener **Python 3.x** instalado en tu sistema.
3. Instala la librería **Pygame** con el siguiente comando:
    ```
    pip install pygame
    ```

## Uso

Ejecuta el archivo `megatetris.py` para iniciar el juego:
```
python megatetris.py
```

## Controles

- **Flecha arriba**: Rotar la pieza.
- **Flecha izquierda**: Mover la pieza hacia la izquierda.
- **Flecha derecha**: Mover la pieza hacia la derecha.
- **Flecha abajo**: Acelerar la caída de la pieza.
- **Tecla 0**: Saltar de nivel.

## Clases Principales

### `Tablero`
Clase que representa el tablero de juego de Tetris. Define el tamaño del tablero, el tamaño de los bloques, y el manejo de los gráficos.

### `Game`
Clase que maneja toda la lógica del juego, como la generación de piezas, el control del movimiento, la eliminación de líneas y la gestión de niveles.

### `Pieza`
Clase que representa las piezas del Tetris. Maneja los movimientos de las piezas (rotación, traslación) y su interacción con el tablero.

## Reglas

1. Las piezas caen desde la parte superior del tablero.
2. El objetivo es organizar las piezas de tal manera que formen líneas horizontales completas sin espacios vacíos.
3. Al completar una línea, esta desaparece y se otorgan puntos.
4. El juego finaliza si las piezas se acumulan hasta la parte superior del tablero.

## Créditos

Creado por [Tu Nombre].
