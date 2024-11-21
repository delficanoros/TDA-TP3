# Import PuLP library
import pulp

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

file_path = 'resultados/5_5_6.txt'
# Leo la data del archivo que nos pasaron.
filas, columnas, longitud_barcos = read_input_file(file_path)

n = len(filas)
m = len(columnas)
k = len(longitud_barcos)

barcos = list(range(k))  # Barcos



def solve_batalla_naval( demandas_filas, demandas_columnas, barcos):
    n = len(demandas_filas)
    m = len(demandas_columnas)

    # Crear problema
    problem = pulp.LpProblem("BatallaNaval", pulp.LpMinimize)

    # Variables
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(n) for j in range(m)), 0, 1, pulp.LpBinary)
    u = pulp.LpVariable.dicts("u", (i for i in range(n)), 0, None, pulp.LpInteger)
    v = pulp.LpVariable.dicts("v", (j for j in range(m)), 0, None, pulp.LpInteger)
    y = pulp.LpVariable.dicts("y", ((i, b, k) for i in range(n) for b in range(m) for k in range(len(barcos))), 0, 1,
                              pulp.LpBinary)
    z = pulp.LpVariable.dicts("z", ((j, b, k) for j in range(m) for b in range(n) for k in range(len(barcos))), 0, 1,
                              pulp.LpBinary)

    # Función objetivo: minimizar la demanda incumplida
    problem += pulp.lpSum(u[i] for i in range(n)) + pulp.lpSum(v[j] for j in range(m))

    # Restricciones
    for i in range(n):
        # Restricción de demanda de filas
        problem += pulp.lpSum(x[i, j] for j in range(m)) + u[i] == demandas_filas[i]

    for j in range(m):
        # Restricción de demanda de columnas
        problem += pulp.lpSum(x[i, j] for i in range(n)) + v[j] == demandas_columnas[j]

    for k, length in enumerate(barcos):
        # Restricciones para cada barco
        for i in range(n):
            for j in range(m - length + 1): #horizontal
                problem += pulp.lpSum(x[i, j + l] for l in range(length)) >= y[i, j, k] * length
        for j in range(m):
            for i in range(n - length + 1): #vertical
                problem += pulp.lpSum(x[i + l, j] for l in range(length)) >= z[j, i, k] * length

        # Un barco puede colocarse una vez como máximo (horizontal o verticalmente)
        problem += (pulp.lpSum(y[i, b, k] for i in range(n) for b in range(m))
                    + pulp.lpSum(z[j, b, k] for j in range(m) for b in range(n)) <= 1)

    # Las celdas ocupadas con maximo del barco
    problem += pulp.lpSum(x[i, j] for i in range(n) for j in range(m)) <= sum(barcos)

    # Resolver problema
    problem.solve()

    # Resultados
    solution = [[pulp.value(x[i, j]) for j in range(m)] for i in range(n)]
    incumplido_por_filas = [pulp.value(u[i]) for i in range(n)]
    incumplido_por_columna = [pulp.value(v[j]) for j in range(m)]

    return solution, incumplido_por_filas, incumplido_por_columna

solucion, incumplido_por_filas, incumplido_por_columna = solve_batalla_naval(filas, columnas, longitud_barcos)

print("Tablero:")
for row in solucion:
    print(row)
demanda_incumplida_filas = int(sum(incumplido_por_filas))
demanda_incumplida_columnas = int(sum(incumplido_por_columna))
demanda_total = sum(filas) + sum(columnas)
#print("Demanda incumplida:", demanda_incumplida_filas + demanda_incumplida_columnas)
print("Demanda cumplida:", demanda_total - (demanda_incumplida_columnas + demanda_incumplida_filas))
print("Demanda total:", demanda_total)