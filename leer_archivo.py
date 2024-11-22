from backtracking import batalla_naval, calcular_demanda
import time


def parse_lines_without_numeral(lines):
    # vamos a ignorar las de comentarios de arriba porque interfieren
    return [line.strip() for line in lines if not line.strip().startswith("#")]


def read_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    valid_lines = parse_lines_without_numeral(lines)
    config_actual = []
    configs = []
    for line in valid_lines:
        if line == "":
            if config_actual:  # llegue y entre aca porque termino la parte pasada del archivo entonces ya puedo guardarla
                configs.append(config_actual)
                config_actual = []
        else:
            config_actual.append(line)
    if config_actual:
        configs.append(config_actual)
    if len(configs) != 3:
        raise ValueError(
            f"Ee encontraron {len(configs)} configuraciones en lugar de 3. No te olvides que necesitamos demandas de filas y columnas y ademas  los largos de los barcos separados por un salto de linea")
    try:
        row_restrictions = [int(x) for x in configs[0]]

        col_restrictions = [int(x) for x in configs[1]]
        ships = list(map(int, configs[2]))
    except ValueError:
        raise ValueError(
            "El archivo contiene datos no numéricos en las restricciones o longitudes de los barcos.")
    return row_restrictions, col_restrictions, ships


def resolve(file_path):
    try:
        row_restrictions, col_restrictions, ships = read_input_file(file_path)
    except ValueError as e:
        print(f"falla al leer el archivo: {e}")
        return

    n = len(row_restrictions)
    m = len(col_restrictions)
    table = [[0 for _ in range(m)] for _ in range(n)]
    demand_fulfilled, optimal_board, positions = batalla_naval(
        table, ships, row_restrictions, col_restrictions)

    _, demand_total = calcular_demanda(
        optimal_board, row_restrictions, col_restrictions)

    file_name = file_path.split("/")[-1]

    print(f"{file_name}")
    print("Posiciones:")
    for i, position in enumerate(positions):
        if position is None:
            print(f"{i}: None")
        else:
            start, end = position
            if start == end:
                print(f"{i}: {start}")
            else:
                print(f"{i}: {start} - {end}")
    print(f"Demanda cumplida: {demand_fulfilled}")
    print(f"Demanda total: {demand_total}")
    print("Tablero final:")
    for row in optimal_board:
        print("".join(["#" if cell == 1 else "." for cell in row]))
