Claro, aquí tienes una propuesta para el archivo `README.md` basada en el nuevo script que proporcionaste. He actualizado la estructura, las dependencias, los controles y las explicaciones para que coincidan con el código actual.

-----

# Megatetris

Este proyecto es una implementación completa y moderna del juego **Tetris** en un solo archivo de Python, utilizando **Pygame** para los gráficos y **NumPy** para la gestión eficiente del tablero. El código está completamente comentado en castellano y sigue una arquitectura Modelo-Vista-Controlador (MVC).

## Características

  - **Juego Clásico:** Implementa todas las reglas fundamentales del Tetris.
  - **Sistema de Niveles:** La velocidad de caída de las piezas aumenta cada 10 líneas completadas.
  - **Puntuación Dinámica:** Los puntos obtenidos por línea dependen del nivel actual.
  - **Generador de Piezas "7-Bag":** Asegura una distribución justa y aleatoria de las piezas, evitando largas sequías de una pieza específica.
  - **Fondos Dinámicos:** El color del fondo cambia sutilmente con cada nivel para mejorar la experiencia visual.
  - **Código bien estructurado:** Sigue el patrón de diseño MVC para separar la lógica del juego de su presentación.

## Arquitectura del Proyecto

El proyecto está contenido en un único archivo, `megatetris.py`, y se organiza siguiendo el patrón **Modelo-Vista-Controlador (MVC)**:

  - **Modelo**: Se encarga de la lógica y el estado del juego.
      - `Tablero`: Representa la cuadrícula del juego, gestiona las colisiones y la limpieza de líneas.
      - `Pieza`: Define las piezas, sus formas, rotaciones y movimientos.
  - **Vista**: Responsable de toda la renderización gráfica.
      - Las funciones de dibujo (`_draw`) dentro de la clase `Juego` se encargan de pintar el tablero, las piezas, la cuadrícula y el HUD (puntuación, nivel, etc.).
  - **Controlador**: Gestiona las entradas del usuario y el flujo principal del juego.
      - `Juego`: Es la clase principal que contiene el bucle de juego, procesa los eventos del teclado y coordina las interacciones entre el Modelo y la Vista.

## Instalación

1.  Asegúrate de tener **Python 3.x** instalado.
2.  Instala las librerías necesarias, **Pygame** y **NumPy**, con el siguiente comando en tu terminal:
    ```bash
    pip install pygame numpy
    ```

## Uso

Para iniciar el juego, simplemente ejecuta el script de Python desde tu terminal:

```bash
python megatetris.py
```

*(Nota: Debes guardar el código proporcionado en un archivo llamado `megatetris.py` o similar).*

## Controles

  - **Flecha Izquierda**: Mover la pieza hacia la izquierda.
  - **Flecha Derecha**: Mover la pieza hacia la derecha.
  - **Flecha Arriba**: Rotar la pieza 90 grados.
  - **Flecha Abajo (Soft Drop)**: Acelerar la caída de la pieza un paso.
  - **Barra Espaciadora (Hard Drop)**: Dejar caer la pieza instantáneamente al fondo.
  - **Tecla ESC**: Salir del juego.

## Reglas del Juego

1.  Las piezas (tetrominós) caen desde la parte superior del tablero.
2.  El objetivo es mover y rotar las piezas para formar líneas horizontales completas.
3.  Cuando se completa una o más líneas, estas desaparecen, las filas superiores caen y se otorgan puntos.
4.  El juego termina si las piezas se apilan hasta la parte superior del tablero.
5.  Cada 10 líneas completadas, el nivel aumenta y las piezas caen más rápido.

## Créditos

Creado por Juan de Dios 
