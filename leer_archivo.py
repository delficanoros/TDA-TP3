import sys
from backtracking import batalla_naval, calcular_demanda
from aproximacion import aproximación


def parse_lines_without_numeral(lines):
    return [line.strip() for line in lines if not line.strip().startswith("#")]


def read_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    valid_lines = parse_lines_without_numeral(lines)
    config_actual = []
    configs = []
    for line in valid_lines:
        if line == "":
            if config_actual:
                configs.append(config_actual)
                config_actual = []
        else:
            config_actual.append(line)
    if config_actual:
        configs.append(config_actual)
    if len(configs) != 3:
        raise ValueError(
            f"Se encontraron {len(configs)} configuraciones en lugar de 3. Debes incluir: demandas de filas, columnas y longitudes de barcos separados por un salto de línea.")
    try:
        row_restrictions = [int(x) for x in configs[0]]
        col_restrictions = [int(x) for x in configs[1]]
        ships = list(map(int, configs[2]))
    except ValueError:
        raise ValueError(
            "El archivo contiene datos no numéricos en las restricciones o longitudes de los barcos.")
    return row_restrictions, col_restrictions, ships


def main():
    if len(sys.argv) < 2:
        print("Error: Debes proporcionar la ruta de un archivo de entrada como parámetro.")
        print("Uso: python script.py <ruta_del_archivo>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        row_restrictions, col_restrictions, ships = read_input_file(file_path)
    except ValueError as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

    print("Selecciona el algoritmo que deseas usar para resolver el problema:")
    print("1. Backtracking")
    print("2. Programación lineal")
    print("3. Aproximación")
    choice = input("Ingresa el número correspondiente a tu elección: ")

    n = len(row_restrictions)
    m = len(col_restrictions)
    table = [[0 for _ in range(m)] for _ in range(n)]

    if choice == "1":
        demand_fulfilled, optimal_board, positions = batalla_naval(
            table, ships, row_restrictions, col_restrictions)
    elif choice == "2":
        """orientations = ['H', 'V']
        positions = posibles_posiciones(ships, orientations, n, m)
        prob, optimal_board = resolve_batalla_naval(
            n, m, ships, n, m, posiciones)
"""
    elif choice == "3":
        optimal_board, positions = aproximación(
            table, ships, row_restrictions, col_restrictions)
    else:
        print("Opción no válida. Finalizando el programa.")
        sys.exit(1)

    demand_fulfilled, demand_total = calcular_demanda(
        optimal_board, row_restrictions, col_restrictions)

    print(f"Archivo procesado: {file_path}")
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
        print("".join(["1" if cell == 1 else "." for cell in row]))


if __name__ == "__main__":
    main()
