# Megatetris Mejorado

Este proyecto es una implementación completa y moderna del juego **Tetris** en un solo archivo de Python, utilizando **Pygame** para los gráficos y **NumPy** para la gestión eficiente del tablero. El código está completamente comentado en castellano y se inspira en una arquitectura limpia para separar la lógica del juego de su presentación.

## Características

  - **Juego Clásico:** Implementa todas las reglas fundamentales del Tetris.
  - **Sistema de Niveles:** La velocidad de caída de las piezas aumenta cada 10 líneas completadas, hasta un límite de dificultad máxima.
  - **Puntuación Dinámica:** Los puntos obtenidos por línea dependen del nivel actual, premiando el riesgo.
  - **Generador de Piezas "7-Bag":** Asegura una distribución justa y pseudo-aleatoria de las piezas, evitando largas sequías de un tetrominó específico.
  - **Función "Hold":** Permite guardar una pieza para usarla estratégicamente más tarde.
  - **Wall Kick Simplificado:** Ayuda a que las piezas roten suavemente cerca de las paredes del tablero.
  - **Código bien estructurado:** Utiliza clases y una organización clara que facilita la comprensión y modificación del juego.

## Arquitectura del Proyecto

El proyecto está contenido en un único archivo y se organiza de la siguiente manera:

  - **Modelo**: Se encarga de la lógica y el estado del juego.
      - `Tablero`: Representa la cuadrícula del juego, gestiona las colisiones y la limpieza de líneas.
      - `Pieza`: Define los tetrominós, sus formas, rotaciones y movimientos.
  - **Vista**: Responsable de toda la renderización gráfica.
      - El método `_draw_hud` y el bloque de "Dibujado" dentro del bucle principal se encargan de pintar el tablero, las piezas, la cuadrícula y el HUD (puntuación, nivel, etc.).
  - **Controlador**: Gestiona las entradas del usuario y el flujo principal del juego.
      - `Juego`: Es la clase principal que contiene el bucle de juego, procesa los eventos del teclado (Pygame events) y coordina las interacciones entre el Modelo y la Vista.

## Instalación

1.  Asegúrate de tener **Python 3.x** instalado.
2.  Instala las librerías necesarias, **Pygame** y **NumPy**, con el siguiente comando en tu terminal:
    ```bash
    pip install pygame numpy
    ```

## Uso

Para iniciar el juego, simplemente ejecuta el script de Python desde tu terminal:

```bash
python megatetris_mejorado.py
```

*(Nota: Debes guardar el código proporcionado en un archivo llamado `megatetris_mejorado.py` o similar).*

## Controles

  - **Flecha Izquierda**: Mover la pieza hacia la izquierda.
  - **Flecha Derecha**: Mover la pieza hacia la derecha.
  - **Flecha Arriba**: Rotar la pieza 90 grados.
  - **Flecha Abajo (Soft Drop)**: Acelerar la caída de la pieza un paso.
  - **Barra Espaciadora (Hard Drop)**: Dejar caer la pieza instantáneamente al fondo.
  - **Tecla C (Hold)**: Guardar la pieza actual o intercambiarla con la pieza guardada.

## Reglas del Juego

1.  Las piezas (tetrominós) caen desde la parte superior del tablero.
2.  El objetivo es mover y rotar las piezas para formar líneas horizontales completas.
3.  Cuando se completa una o más líneas, estas desaparecen, las filas superiores caen y se otorgan puntos.
4.  El juego termina si las piezas se apilan hasta la parte superior del tablero.
5.  Cada 10 líneas completadas, el nivel aumenta y las piezas caen más rápido.
6.  Puedes usar la tecla 'C' para guardar una pieza y utilizarla más adelante. Solo se puede hacer un intercambio por pieza que cae.

## Créditos

Creado por Juan Galaz
