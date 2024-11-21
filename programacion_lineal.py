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

file_path = 'resultados/3_3_2.txt'
#Leo la data del archivo que nos pasaron.
rows, cols, ships_len = read_input_file(file_path)

n = len(rows)
m = len(cols)
k = len(ships_len)

ships = list(range(k))  # Ship indices
orientations = ['H', 'V']  # Horizontal (H) o Vertical (V)
positions = [(i, j) for i in range(n) for j in range(m)]  # Armo el tablero

# Generate feasible starting positions for each ship and orientation
F_po = {}  # F_po[(p, o)] = list of feasible starting positions for ship p with orientation o
for p in ships:
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

# Crear el problema
prob = LpProblem("LaBatallaNaval", LpMinimize)

# Variables de decisión
s = LpVariable.dicts(
    "s", [(p, o, i, j) for p in ships for o in orientations for (i, j) in F_po[(p, o)]], 0, 1,
    LpBinary)

c = LpVariable.dicts("c", positions, 0, 1, LpBinary)

# Variables para la demanda incumplida
unfulfilled_row_demand = LpVariable.dicts("UnfulfilledRow", range(n), 0, None, LpContinuous)
unfulfilled_col_demand = LpVariable.dicts("UnfulfilledCol", range(m), 0, None, LpContinuous)

# Función objetivo: Minimizar la demanda incumplida
prob += lpSum(unfulfilled_row_demand[i] for i in range(n)) + lpSum(unfulfilled_col_demand[j] for j in range(m)), "TotalUnfulfilledDemand"

# Relación entre celdas ocupadas y demanda incumplida para filas
for i in range(n):
    prob += unfulfilled_row_demand[i] == rows[i] - lpSum(c[(i, j)] for j in range(m)), f"RowDemandBalance_{i}"
    prob += lpSum(c[(i, j)] for j in range(m)) <= rows[i], f"RowDemandLimit_{i}"  # No superar la demanda

# Relación entre celdas ocupadas y demanda incumplida para columnas
for j in range(m):
    prob += unfulfilled_col_demand[j] == cols[j] - lpSum(c[(i, j)] for i in range(n)), f"ColDemandBalance_{j}"
    prob += lpSum(c[(i, j)] for i in range(n)) <= cols[j], f"ColDemandLimit_{j}"  # No superar la demanda

# Mapeo de celdas ocupadas a posiciones iniciales factibles de los barcos
cell_coverage = {pos: [] for pos in positions}
for p in ships:
    b_p = ships_len[p]
    for o in orientations:
        for (i, j) in F_po[(p, o)]:
            cells_covered = []
            if o == 'H':
                cells_covered = [(i, j + offset) for offset in range(b_p)]
            elif o == 'V':
                cells_covered = [(i + offset, j) for offset in range(b_p)]
            for cell in cells_covered:
                cell_coverage[cell].append((p, o, i, j))

# Restricción: Las celdas ocupadas reflejan los barcos colocados
for (i, j) in positions:
    prob += c[(i, j)] >= lpSum([s[(p, o, i_p, j_p)] for (p, o, i_p, j_p) in cell_coverage[(i, j)]]), f"Cell_occupied_{i}_{j}"
    prob += lpSum([s[(p, o, i_p, j_p)] for (p, o, i_p, j_p) in cell_coverage[(i, j)]]) <= 1, f"No_overlap_{i}_{j}"

# Resolver el modelo
prob.solve()

# Imprimir resultados
print("Status:", LpStatus[prob.status])

if LpStatus[prob.status] == 'Optimal':
    grid = [['-' for _ in range(m)] for _ in range(n)]
    for p in ships:
        for o in orientations:
            for (i, j) in F_po[(p, o)]:
                if value(s[(p, o, i, j)]) == 1:
                    b_p = ships_len[p]
                    if o == 'H':
                        for offset in range(b_p):
                            grid[i][j + offset] = str(p)
                    elif o == 'V':
                        for offset in range(b_p):
                            grid[i + offset][j] = str(p)
    print("Tablero con la solución:")
    for row in grid:
        print(' '.join(row))
    print("Demanda incumplida por fila:")
    for i in range(n):
        print(f"Fila {i}: Incumplida = {int(value(unfulfilled_row_demand[i]))}")
    print("Demanda incumplida por columna:")
    for j in range(m):
        print(f"Columna {j}: Incumplida = {int(value(unfulfilled_col_demand[j]))}")
else:
    print("No se encontró solución.")
