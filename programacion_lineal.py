# Import PuLP library
from pulp import *

def read_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    valid_lines = [line.strip() for line in lines if not line.strip().startswith("#")]
    sections = []
    current_section = []

    for line in valid_lines:
        if line == "":
            if current_section:
                sections.append(current_section)
                current_section = []
        else:
            current_section.append(line)
    if current_section:
        sections.append(current_section)
    if len(sections) != 3:
        raise ValueError(
            f"El archivo no tiene el formato esperado. Se encontraron {len(sections)} secciones en lugar de 3.")

    try:
        rows = list(map(int, sections[0]))
        cols = list(map(int, sections[1]))
        ships = list(map(int, sections[2]))
    except ValueError:
        raise ValueError("El archivo contiene datos no numéricos en las restricciones o longitudes de los barcos.")

    return rows, cols, ships

file_path = 'resultados/10_10_10.txt'
# Leo la data del archivo que nos pasaron.
rows, cols, ships_len = read_input_file(file_path)

n = len(rows)
m = len(cols)
k = len(ships_len)

barcos = list(range(k))  # Barcos
orientations = ['H', 'V']  # Horizontal (H) o Vertical (V)
positions = [(i, j) for i in range(n) for j in range(m)]  # Armo el tablero

# Generar posiciones iniciales factibles para cada barco y orientación
F_po = {}  # F_po[(p, o)] = lista de posiciones iniciales factibles para barco p con orientación o
for p in barcos:
    b_p = ships_len[p]
    for o in orientations:
        feasible_positions = []
        if o == 'H':
            for i in range(n):
                for j in range(m - b_p + 1):
                    feasible_positions.append((i, j))
        elif o == 'V':
            for i in range(n - b_p + 1):
                for j in range(m):
                    feasible_positions.append((i, j))
        F_po[(p, o)] = feasible_positions

# Mapeo de celdas a las posiciones de los barcos
cell_coverage = {pos: [] for pos in positions}
for p in barcos:
    b_p = ships_len[p]
    for o in orientations:
        for (i, j) in F_po[(p, o)]:
            celdas_ocupadas = []
            if o == 'H':
                celdas_ocupadas = [(i, j + offset) for offset in range(b_p)]
            elif o == 'V':
                celdas_ocupadas = [(i + offset, j) for offset in range(b_p)]
            for cell in celdas_ocupadas:
                cell_coverage[cell].append((p, o, i, j))


#### Modelo de programación lineal ########

# Variables de decisión

# barco_en_posicion_{p,o,i,j} = 1 si el barco p se coloca con orientación o en la posición (i, j)
barco_en_posicion = LpVariable.dicts(
    "s", [(p, o, i, j) for p in barcos for o in orientations for (i, j) in F_po[(p, o)]], 0, 1,
    LpBinary)

# Variable de decisión para saber si está ocupada o no una celda
c = LpVariable.dicts("c", positions, 0, 1, LpBinary)

# La demanda incumplida es la diferencia entre la demanda total y la cantidad de celdas ocupadas
demanda_incumplida_filas = sum(rows[i] - lpSum(c[(i, j)] for j in range(m)) for i in range(n))
demanda_incumplida_columnas = sum(cols[j] - lpSum(c[(i, j)] for i in range(n)) for j in range(m))

# Es un problema que busca minimizar la demanda incumplida
prob = LpProblem("LaBatallaNaval", LpMinimize)
demanda_incumplida_total = demanda_incumplida_filas + demanda_incumplida_columnas
prob += demanda_incumplida_total


# Restricción 1: Cada barco se coloca exactamente una vez si o si
for p in barcos:
    prob += lpSum([barco_en_posicion[(p, o, i, j)] for o in orientations for (i, j) in F_po[(p, o)]]) == 1

# Restricción 2: Las celdas ocupadas deben corresponder a las posiciones de los barcos
for (i, j) in positions:
    prob += c[(i, j)] >= lpSum([barco_en_posicion[(p, o, i_p, j_p)] for (p, o, i_p, j_p) in cell_coverage[(i, j)]])

# Restricción 3: No superposición de barcos
for (i, j) in positions:
    prob += lpSum([barco_en_posicion[(p, o, i_p, j_p)] for (p, o, i_p, j_p) in cell_coverage[(i, j)]]) <= 1

# Restricción 4: No adyacencia entre barcos
for p in barcos:
    b_p = ships_len[p]
    for o in orientations:
        for (i, j) in F_po[(p, o)]:
            celdas_ocupadas = []
            if o == 'H':
                celdas_ocupadas = [(i, j + offset) for offset in range(b_p)]
            elif o == 'V':
                celdas_ocupadas = [(i + offset, j) for offset in range(b_p)]
            adyacentes = set()
            for (pos_fila, pos_col) in celdas_ocupadas:
                for fila_delta in [-1, 0, 1]:
                    for columna_delta in [-1, 0, 1]:
                        filas_ady = pos_fila + fila_delta
                        cols_ady = pos_col + columna_delta
                        if (0 <= filas_ady < n) and (0 <= cols_ady < m):
                            if (filas_ady, cols_ady) not in celdas_ocupadas:
                                adyacentes.add((filas_ady, cols_ady))
            for (filas_ady, cols_ady) in adyacentes:
                prob += c[(filas_ady, cols_ady)] + barco_en_posicion[(p, o, i, j)] <= 1

# Restricción 5: Demanda de filas menor a la dada
for i in range(n):
    prob += lpSum([c[(i, j)] for j in range(m)]) <= rows[i]

# Restricción 6: Demanda de columnas menor a la dada
for j in range(m):
    prob += lpSum([c[(i, j)] for i in range(n)]) <= cols[j]

# Resolver el modelo
prob.solve()






# Output de los resultados
print("Status:", LpStatus[prob.status])

if LpStatus[prob.status] == 'Optimal':
    grid = [['-' for _ in range(m)] for _ in range(n)]
    for p in barcos:
        for o in orientations:
            for (i, j) in F_po[(p, o)]:
                if value(barco_en_posicion[(p, o, i, j)]) == 1:
                    b_p = ships_len[p]
                    if o == 'H':
                        for offset in range(b_p):
                            grid[i][j + offset] = str(p)
                    elif o == 'V':
                        for offset in range(b_p):
                            grid[i + offset][j] = str(p)


    # Calcular la demanda total y la demanda cumplida
    demanda_total = sum(rows) + sum(cols)
    demanda_cumplida = demanda_total - demanda_incumplida_total

    # Imprimir la solución
    print("Tablero con la solución:")
    for row in grid:
        print(' '.join(row))

    print(f"Demanda cumplida: {int(value(demanda_cumplida))}")
    print(f"Demanda total: {demanda_total}")
    print(f"Demanda incumplida: {int(value(demanda_incumplida_total))}")
else:
    print("No se encontró solución.")
