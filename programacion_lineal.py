from pulp import *

def posibles_posiciones(ships_len, orientations, rows, cols):
    nro_cols = len(cols)
    nro_rows = len(rows)
    potentially_positions = {}
    for ship, ship_len in enumerate(ships_len):
        for o in orientations:
            if o == 'H':
                position = [
                    (i, j) for i in range(nro_rows) for j in range(nro_cols - ship_len + 1)
                    if sum(rows[i:j + ship_len]) > 0
                ]
            elif o == 'V':
                position = [
                    (i, j) for i in range(nro_rows - ship_len + 1) for j in range(nro_cols)
                    if sum(cols[j:i + ship_len]) > 0
                ]
            potentially_positions[(ship, o)] = position
    return potentially_positions


def calcular_celdas_adyacentes(n, m, covered_cells):
    # Calcula las celdas adyacentes a las celdas ocupadas por un barco
    adjacent_cells = set()
    for (i_cell, j_cell) in covered_cells:
        for delta_i in [-1, 0, 1]:
            for delta_j in [-1, 0, 1]:
                i_adj, j_adj = i_cell + delta_i, j_cell + delta_j
                if 0 <= i_adj < n and 0 <= j_adj < m and (i_adj, j_adj) not in covered_cells:
                    adjacent_cells.add((i_adj, j_adj))
    return adjacent_cells


def resolve_batalla_naval(nro_filas, nro_columnas, ships_len, rows, cols, posibles_posiciones):
    ships = list(range(len(ships_len)))  # Barcos enumerados
    orientations = ['H', 'V']  # Horizontal (H) o Vertical (V)

    # Variables de decisión
    barco_en_celda = LpVariable.dicts(
        "barco_en_celda",
        [(ship, o, i, j) for ship in ships for o in orientations for (
            i, j) in posibles_posiciones[(ship, o)]],
        0, 1, LpBinary
    )
    barco_no_colocado = LpVariable.dicts(
        "barco_no_colocado", ships, 0, 1, LpBinary)

    # Modelo y función objetivo
    prob = LpProblem("LaBatallaNaval", LpMinimize)
    prob += (
        sum(rows[i] - lpSum(
            lpSum(
                barco_en_celda[(ship, o, i_start, j_start)]
                for ship in ships
                for o in orientations
                for (i_start, j_start) in posibles_posiciones[(ship, o)]
                if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
                   (o == 'V' and j_start == j and i_start <=
                    i < i_start + ships_len[ship])
            )
            for j in range(nro_columnas)
        ) for i in range(nro_filas)) +
        sum(cols[j] - lpSum(
            lpSum(
                barco_en_celda[(ship, o, i_start, j_start)]
                for ship in ships
                for o in orientations
                for (i_start, j_start) in posibles_posiciones[(ship, o)]
                if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
                   (o == 'V' and j_start == j and i_start <=
                    i < i_start + ships_len[ship])
            )
            for i in range(nro_filas)
        ) for j in range(nro_columnas)),
        "Demanda incumplida"
    )

    # Restricción 1: Cada barco se coloca exactamente una vez o no se coloca
    for ship in ships:
        prob += lpSum(barco_en_celda[(ship, o, i, j)] for o in orientations for (
            i, j) in posibles_posiciones[(ship, o)]) + barco_no_colocado[ship] == 1

    # Restricción 2: No superposición de barcos
    for i in range(nro_filas):
        for j in range(nro_columnas):
            prob += lpSum(
                barco_en_celda[(ship, o, i_start, j_start)]
                for ship in ships
                for o in orientations
                for (i_start, j_start) in posibles_posiciones[(ship, o)]
                if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
                   (o == 'V' and j_start == j and i_start <=
                    i < i_start + ships_len[ship])
            ) <= 1

    # Restricción 3: No adyacencia entre barcos
    for ship in ships:
        ship_len = ships_len[ship]
        for o in orientations:
            for (i, j) in posibles_posiciones[(ship, o)]:
                covered_cells = [(i, j + offset) for offset in range(ship_len)
                                 ] if o == 'H' else [(i + offset, j) for offset in range(ship_len)]
                adjacent_cells = calcular_celdas_adyacentes(
                    nro_filas, nro_columnas, covered_cells)
                for (i_adj, j_adj) in adjacent_cells:
                    prob += lpSum(
                        barco_en_celda[(ship_adj, o_adj, i_start, j_start)]
                        for ship_adj in ships
                        for o_adj in orientations
                        for (i_start, j_start) in posibles_posiciones[(ship_adj, o_adj)]
                        if (o_adj == 'H' and i_start == i_adj and j_start <= j_adj < j_start + ships_len[ship_adj]) or
                           (o_adj == 'V' and j_start == j_adj and i_start <=
                            i_adj < i_start + ships_len[ship_adj])
                    ) + barco_en_celda[(ship, o, i, j)] <= 1

    # Restricción 4: Demanda máxima por fila
    for i in range(nro_filas):
        prob += lpSum(
            lpSum(
                barco_en_celda[(ship, o, i_start, j_start)]
                for ship in ships
                for o in orientations
                for (i_start, j_start) in posibles_posiciones[(ship, o)]
                if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
                   (o == 'V' and j_start == j and i_start <=
                    i < i_start + ships_len[ship])
            )
            for j in range(nro_columnas)
        ) <= rows[i]

    # Restricción 5: Demanda máxima por columna
    for j in range(nro_columnas):
        prob += lpSum(
            lpSum(
                barco_en_celda[(ship, o, i_start, j_start)]
                for ship in ships
                for o in orientations
                for (i_start, j_start) in posibles_posiciones[(ship, o)]
                if (o == 'H' and i_start == i and j_start <= j < j_start + ships_len[ship]) or
                   (o == 'V' and j_start == j and i_start <=
                    i < i_start + ships_len[ship])
            )
            for i in range(nro_filas)
        ) <= cols[j]

    # Resolver el modelo
    prob.solve()
    return prob, barco_en_celda


def reconstruir_tablero_y_calcular_demanda(n, m, matriz_resuelta, ships_len, rows, cols):
    tablero = [["-"] * m for _ in range(n)]

    # Recorre todas las variables de decisión
    for (ship, o, i, j), var in matriz_resuelta.items():
        if value(var) > 0.5:  # Si hay barco
            ship_len = ships_len[ship]
            if o == 'H':
                for offset in range(ship_len):
                    tablero[i][j + offset] = "1"
            elif o == 'V':
                for offset in range(ship_len):
                    tablero[i + offset][j] = "1"

    demanda_filas = [sum(1 for j in range(m) if tablero[i][j] == "1")
                     for i in range(n)]
    demanda_columnas = [sum(1 for i in range(
        n) if tablero[i][j] == "1") for j in range(m)]

    demanda_total_cumplida = sum(min(demanda_filas[i], rows[i]) for i in range(n)) + \
        sum(min(demanda_columnas[j], cols[j]) for j in range(m))
    demanda_total = sum(rows) + sum(cols)

    return tablero, demanda_total_cumplida, demanda_total