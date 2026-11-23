# Algoritmo de Cifrado por Rejilla Giratoria (Turning Grille / Fleissner) en Python

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Supported-013243.svg)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Implementación interactiva en Python del algoritmo clásico de **cifrado de transposición por rejilla giratoria (Turning Grille / Rejilla de Fleissner)**. Utiliza matrices bidimensionales de caracteres con **NumPy**, soportando configuración dinámica de dimensiones de rejilla ($N \times N$), rotaciones en sentido horario y antihorario, e inspección visual de las matrices intermedias.

---

## 🔐 Fundamento Histórico y Criptográfico

La rejilla giratoria es un sistema de cifrado de transposición fraccionada inventado por el barón austríaco **Edouard Fleissner von Wostrowitz** en 1881 y utilizado militarmente durante la Primera Guerra Mundial por el ejército alemán.

### 1. Principio de Construcción de la Rejilla

Para una matriz cuadrada de dimensión par $N \times N$ (por ejemplo, $4 \times 4$, $6 \times 6$ u $8 \times 8$):
- El área total es $N^2$ casillas.
- La rejilla contiene exactamente $\frac{N^2}{4}$ perforaciones o ventanas abiertas dispuestas de tal forma que, al rotar la rejilla $90^\circ$ sucesivamente en cuatro orientaciones ($0^\circ, 90^\circ, 180^\circ, 270^\circ$), cada una de las $N^2$ casillas de la matriz subyacente es expuesta **exactamente una vez**.

```text
Orientación 0° ──(Giro 90°)──> Orientación 90° ──(Giro 90°)──> Orientación 180° ──(Giro 90°)──> Orientación 270°
```

### 2. Proceso de Cifrado

1. Se coloca la rejilla en su orientación inicial ($0^\circ$).
2. Se escriben los primeros $\frac{N^2}{4}$ caracteres del mensaje a través de los huecos.
3. Se rota la rejilla $90^\circ$ y se introducen los siguientes $\frac{N^2}{4}$ caracteres.
4. Se repite la rotación para $180^\circ$ y $270^\circ$.
5. Si el mensaje no llena todas las celdas, se añaden caracteres de relleno (*null characters* o letras aleatorias).
6. Al retirar la rejilla, el texto cifrado se obtiene leyendo la matriz fila por fila (o columna por columna), generando una permutación seudoaleatoria no lineal de las posiciones originales.

### 3. Proceso de Descifrado

1. Se transcriben los $N^2$ caracteres del criptograma en la matriz vacía $N \times N$ por filas.
2. Se superpone la rejilla física o lógica en la posición $0^\circ$ y se leen las letras a través de los orificios.
3. Se gira sucesivamente a $90^\circ, 180^\circ$ y $270^\circ$, concatenando los caracteres leídos para reconstruir el mensaje original.

---

## 📂 Estructura del Repositorio

```text
turning-grille-algorithm/
├── main.py        # Algoritmo interactivo de cifrado, descifrado y rotacion matricial
└── Video.txt      # Enlace a demostracion multimedia en YouTube
```

---

## 🚀 Requisitos e Instalación

### Prerrequisitos

- **Python** (versión 3.8 o superior).
- Biblioteca **NumPy**.

### Instalación de Dependencias

```bash
pip install numpy
```

---

## 💻 Guía de Uso

Ejecuta el script principal desde la terminal:

```bash
python main.py
```

### Flujo Interactivo

1. **Modo de Operación**:
   - `1` para Cifrar un mensaje.
   - `2` para Descifrar un criptograma.
2. **Dimensiones de la Rejilla**: Ingresa el tamaño $N$ (ejemplo: `4` para una cuadrícula $4 \times 4$).
3. **Sentido de Rotación**:
   - `1` para Horario.
   - `2` para Antihorario.
4. **Posiciones de las Perforaciones**: El sistema solicita las coordenadas `(fila, columna)` de los orificios correspondientes a la clave compartida.
5. **Ingreso del Texto**: Escribe el texto claro o texto cifrado a procesar.

---

## 📹 Demostración en Video

Demostración práctica del funcionamiento y análisis del algoritmo en YouTube:
[Demostración en YouTube](https://youtu.be/2eGU6C_wohI)

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
