# Rejilla giratoria de Fleissner en Python

[![CI](https://github.com/KevinAndrey96/python-turning-grille-fleissner-cipher/actions/workflows/ci.yml/badge.svg)](https://github.com/KevinAndrey96/python-turning-grille-fleissner-cipher/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-3776AB)
![Cobertura](https://img.shields.io/badge/cobertura-100%25-brightgreen)
![mypy](https://img.shields.io/badge/mypy-strict-2A6DB2)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-yellow.svg)](LICENSE)

Implementación tipada y probada de la **rejilla giratoria** (turning grille), el cifrado por transposición que el coronel austríaco Eduard Fleissner von Wostrowitz describió en 1881. Valida que una rejilla cubra la cuadrícula exactamente una vez, cifra y descifra en ambos sentidos de giro, genera rejillas al azar y busca por fuerza bruta la rejilla de un criptograma pequeño.

## Contenido

- [Cómo funciona](#cómo-funciona)
- [Cuándo una rejilla es válida](#cuándo-una-rejilla-es-válida)
- [Fuerza bruta](#fuerza-bruta)
- [Uso](#uso)
- [Arquitectura](#arquitectura)
- [Pruebas y calidad](#pruebas-y-calidad)
- [Historia del proyecto](#historia-del-proyecto)

## Cómo funciona

Una tarjeta cuadrada con perforaciones se pone sobre una cuadrícula vacía. Se escriben letras del mensaje en los agujeros, en orden de lectura; se gira la tarjeta un cuarto de vuelta y se sigue escribiendo, hasta completar cuatro posiciones. El criptograma es la cuadrícula leída por filas. Con la rejilla del trabajo original y giro antihorario:

```text
rejilla   posición 1   posición 2   posición 3   posición 4
O...      J...         J.T.         JKT.         JKTD
....      ....         ...T         S.AT         SAAT
.O.O      .I.M         .IAM         .IAM         WIAM
..O.      ..A.         C.A.         C.AT         CNAT
```

`JIM ATTACKS AT DAWN` se convierte en `JKTD SAAT WIAM CNAT`. Descifrar es repetir el proceso leyendo por los agujeros. Los textos largos ocupan varias cuadrículas y la última se completa con X.

## Cuándo una rejilla es válida

Cada casilla $(f, c)$ de una cuadrícula $n \times n$ recorre, al girar, una órbita de cuatro casillas: $(f, c) \to (c,\, n-1-f) \to (n-1-f,\, n-1-c) \to (n-1-c,\, f)$. La rejilla expone cada casilla exactamente una vez si y solo si tiene **un agujero en cada órbita**, es decir, $\lfloor n^2/4 \rfloor$ agujeros. En tamaños impares la casilla central es su propia órbita: si está perforada se usa solo en la primera posición, y si no, queda fuera del criptograma.

La clase `Grille` comprueba esta condición al construirse e indica qué órbita falla, así que una rejilla que sobrescribiría letras no puede llegar al cifrado.

## Fuerza bruta

Como cada órbita aporta 4 opciones, hay $4^{\lfloor n^2/4 \rfloor}$ rejillas (el doble en tamaños impares, por el centro) y dos sentidos de giro:

| Tamaño | Candidatos |
| :-- | --: |
| 4 x 4 | 512 |
| 5 x 5 | 16 384 |
| 6 x 6 | 524 288 |
| 10 x 10 | unos $2.3 \times 10^{15}$ |

`search` prueba todas las rejillas hasta 6 x 6 (unos 20 segundos en ese tamaño) y devuelve las que producen un texto con una palabra conocida. Sobre el ejemplo anterior con la palabra `attacks` aparecen dos: la rejilla original y la misma tarjeta empezando un cuarto de vuelta después, que solo rota el texto (`DAWNJIMATTACKSAT`).

## Uso

Requiere Python 3.12 o superior y [uv](https://docs.astral.sh/uv/). La rejilla se escribe por filas separadas por `/`, con `O` para los agujeros.

```bash
uv sync
uv run turning-grille encrypt -g "O.../..../.O.O/..O." -d ccw "Jim attacks at dawn"
# JKTDSAATWIAMCNAT
uv run turning-grille decrypt -g "O.../..../.O.O/..O." -d ccw "JKTD SAAT WIAM CNAT"
# JIMATTACKSATDAWN
uv run turning-grille generate -n 6 --seed 7
# ...OO./.O.O.O/...O../.O..../....../O..O..
uv run turning-grille search -n 4 -c attacks JKTDSAATWIAMCNAT
```

El sentido de giro es `cw` (horario, por defecto) o `ccw`. Sin `--seed`, `generate` usa el generador aleatorio del sistema operativo. Una rejilla inválida, un criptograma que no completa cuadrículas o una búsqueda demasiado grande terminan con código 2 y un mensaje en la salida de error.

Como librería:

```python
from turning_grille import Direction, Grille, decrypt, encrypt, search

rejilla = Grille.parse(["O...", "....", ".O.O", "..O."])
encrypt("Jim attacks at dawn", rejilla, Direction.COUNTERCLOCKWISE)   # 'JKTDSAATWIAMCNAT'
search("JKTDSAATWIAMCNAT", 4, "attacks")[0].grille == rejilla         # True
```

## Arquitectura

```text
src/turning_grille/
  grille.py   rotaciones, órbitas, Grille validada, posiciones de escritura y rejillas al azar
  cipher.py   transposición por bloques con relleno
  attack.py   enumeración de rejillas y búsqueda con palabra conocida
  cli.py      comandos encrypt, decrypt, generate y search
```

Sin dependencias externas. Los errores se reportan con `GrilleError`, `CiphertextLengthError` y `SearchSpaceError`, subclases de `ValueError`.

## Pruebas y calidad

```bash
uv run pytest --cov
uv run ruff check src tests && uv run ruff format --check src tests
uv run mypy
```

31 pruebas con cobertura del 100 % de líneas y ramas. Reproducen los dos ejemplos del trabajo original: la rejilla de 4 x 4 y una de 9 x 9 con centro perforado que cifra `THIS IS A MESSAGE THAT I AM ENCRYPTING WITH A TURNING GRILLE TO PROVIDE THIS ILLUSTRATIVE EXAMPLE`. Las pruebas basadas en propiedades con Hypothesis generan rejillas al azar de hasta 12 x 12 y verifican que cubren la cuadrícula exactamente una vez en ambos sentidos y que descifrar invierte al cifrar. El pipeline de GitHub Actions ejecuta Ruff y mypy en modo estricto, las pruebas en Python 3.12, 3.13 y 3.14, una prueba de humo del comando instalado y la construcción del paquete con `twine check`.

## Historia del proyecto

El proyecto nació en abril de 2020 como un script interactivo con NumPy para la clase de criptografía, en el que se perforaba la rejilla casilla por casilla desde la consola, acompañado de un [video explicativo](https://youtu.be/2eGU6C_wohI). No comprobaba que la rejilla fuera válida, de modo que una perforación de más sobrescribía letras sin aviso, y el criptograma de 9 x 9 que dejó anotado había perdido su última letra. En 2026 se reescribió como un paquete tipado sin dependencias, con validación por órbitas, soporte correcto del centro en tamaños impares, generación de rejillas, búsqueda exhaustiva y pruebas automatizadas; además se eliminaron del historial el entorno virtual y los archivos del IDE que se habían versionado. El código original se conserva en el tag [`v0.1-python-coursework-2020`](https://github.com/KevinAndrey96/python-turning-grille-fleissner-cipher/tree/v0.1-python-coursework-2020).

## Autor

**Kevin Andrey Herrera Silva** · [GitHub](https://github.com/KevinAndrey96)

## Licencia

Distribuido bajo la [licencia MIT](LICENSE).
