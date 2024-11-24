from pulp import *
import leer_archivo

def posibles_posiciones(nro_filas, nro_columnas, ships_len, orientations):
    """
    Genera las posiciones iniciales posibles para cada barco según su longitud y orientación.
    Garantiza que los barcos no queden fuera del tablero.
    """
    return {
        (ship, o): [
            (i, j)
            for i in range(nro_filas if o == 'H' else nro_filas - ship_len + 1)
            for j in range(nro_columnas - ship_len + 1 if o == 'H' else nro_columnas)
        ]
        for ship, ship_len in enumerate(ships_len)
        for o in orientations
    }

def celdas_ocupadas(ships, orientations, posibles_posiciones, ships_len, i, j, barco_en_celda):
    # Suma las variables que ocupan la celda (i, j).
    return lpSum(
        barco_en_celda[(ship, o, i_start, j_start)]
        for ship in ships
        for o in orientations
        for (i_start, j_start) in posibles_posiciones[(ship, o)]
        if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
           (o == 'V' and j_start == j and i_start <= i < i_start + ships_len[ship])
    )

def calcular_celdas_adyacentes(nro_filas, nro_columnas, covered_cells):
    """Calcula las celdas adyacentes a las celdas cubiertas por un barco."""
    adjacent_cells = set()
    for (i_cell, j_cell) in covered_cells:
        for delta_i in [-1, 0, 1]:
            for delta_j in [-1, 0, 1]:
                i_adj, j_adj = i_cell + delta_i, j_cell + delta_j
                if 0 <= i_adj < nro_filas and 0 <= j_adj < nro_columnas and (i_adj, j_adj) not in covered_cells:
                    adjacent_cells.add((i_adj, j_adj))
    return adjacent_cells

def imprimir_resultados(matriz, rows, cols):
    nro_filas, nro_columnas = len(rows), len(cols)
    demanda_incumplida = sum(rows[i] - lpSum(matriz[i, j] for j in range(nro_columnas)) for i in range(nro_filas)) + \
                         sum(cols[j] - lpSum(matriz[(i, j)] for i in range(nro_filas)) for j in range(nro_columnas))
    print("Tablero con la solución:")
    for i in range(nro_filas):
        print(" ".join("1" if value(matriz[(i, j)]) > 0.5 else "-" for j in range(nro_columnas)))
    print(f"Demanda cumplida: {int(sum(rows) + sum(cols)) - int(value(demanda_incumplida))}")
    print(f"Demanda total: {int(sum(rows) + sum(cols))}")

def resolve_batalla_naval(ships_len, rows, cols, posibles_posiciones):
    nro_filas, nro_columnas = len(rows), len(cols)

    """Resuelve el problema de la batalla naval."""
    ships = list(range(len(ships_len)))  # Barcos enumerados
    orientations = ['H', 'V']  # Horizontal (H) o Vertical (V)

    # Variables de decisión
    barco_en_celda = LpVariable.dicts(
        "barco_en_celda",
        [(ship, o, i, j) for ship in ships for o in orientations for (i, j) in posibles_posiciones[(ship, o)]],
        0, 1, LpBinary
    )
    celda_ocupada = LpVariable.dicts("celda_ocupada", [(i, j) for i in range(nro_filas) for j in range(nro_columnas)], 0, 1, LpBinary)
    barco_no_colocado = LpVariable.dicts("barco_no_colocado", ships, 0, 1, LpBinary)

    # Modelo y función objetivo
    prob = LpProblem("LaBatallaNaval", LpMinimize)
    prob += (
        sum(rows[i] - lpSum(celda_ocupada[(i, j)] for j in range(nro_columnas)) for i in range(nro_filas)) +
        sum(cols[j] - lpSum(celda_ocupada[(i, j)] for i in range(nro_filas)) for j in range(nro_columnas)),
        "Demanda incumplida"
    )

    # Restricción 1: Cada barco se coloca exactamente una vez o no se coloca
    for ship in ships:
        prob += (lpSum(barco_en_celda[(ship, o, i, j)]
                      for o in orientations
                      for (i, j) in posibles_posiciones[(ship, o)])
                 + barco_no_colocado[ship] == 1)

    # Restricción 2: Las celdas ocupadas deben corresponder a las posiciones de los barcos
    for i in range(nro_filas):
        for j in range(nro_columnas):
            prob += celda_ocupada[(i, j)] == celdas_ocupadas(ships, orientations, posibles_posiciones, ships_len, i, j, barco_en_celda)

    # Restricción 3: No superposición de barcos
    for i in range(nro_filas):
        for j in range(nro_columnas):
            prob += celdas_ocupadas(ships, orientations, posibles_posiciones, ships_len, i, j, barco_en_celda) <= 1

    # Restricción 4: No adyacencia entre barcos
    for ship in ships:
        ship_len = ships_len[ship]
        for o in orientations:
            for (i, j) in posibles_posiciones[(ship, o)]:
                covered_cells = [(i, j + offset)
                                 for offset in range(ship_len)] if o == 'H' else [(i + offset, j)
                                                                                  for offset in range(ship_len)]
                adjacent_cells = calcular_celdas_adyacentes(nro_filas, nro_columnas, covered_cells)
                for (i_adj, j_adj) in adjacent_cells:
                    prob += celda_ocupada[(i_adj, j_adj)] + barco_en_celda[(ship, o, i, j)] <= 1

    # Restricción 5: Demanda máxima por fila
    for i in range(nro_filas):
        prob += lpSum(celda_ocupada[(i, j)] for j in range(nro_columnas)) <= rows[i]

    # Restricción 6: Demanda máxima por columna
    for j in range(nro_columnas):
        prob += lpSum(celda_ocupada[(i, j)] for i in range(nro_filas)) <= cols[j]

    # Resolver el modelo
    prob.solve()
    return prob, celda_ocupada


file_path = 'resultados/20_20_20.txt'
rows, cols, ships = leer_archivo.read_input_file(file_path)

nro_filas, nro_columnas = len(rows), len(cols)
orientations = ['H', 'V']
posiciones = posibles_posiciones(nro_filas, nro_columnas, ships, orientations)


prob, matriz_resuelta = resolve_batalla_naval(ships, rows, cols, posiciones)

if LpStatus[prob.status] == 'Optimal':
    imprimir_resultados(matriz_resuelta, rows, cols)
else:
    print("No se encontró solución.")
